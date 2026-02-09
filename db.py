# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
"""Database access: connection lifecycle, schema init, settings, and conversation import."""

import json
import os
import sqlite3
import sys

from flask import g

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.join(BASE_DIR, 'chatgpt.db')

IMPORT_BATCH_SIZE = 50


def get_db():
    try:
        if 'db' not in g:
            conn = sqlite3.connect(DATABASE_PATH)
            conn.execute('PRAGMA foreign_keys = ON')
            conn.row_factory = sqlite3.Row
            g.db = conn
        return g.db
    except RuntimeError:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row
        return conn


def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def _close_if_not_from_g(conn):
    try:
        if g.get('db') is not conn:
            conn.close()
    except RuntimeError:
        conn.close()


def init_db():
    """Create schema and defaults. Uses schema.sql. Uses get_db() so tests can patch it; run within app.app_context() when calling from CLI."""
    conn = get_db()
    schema_path = os.path.join(BASE_DIR, 'schema.sql')
    with open(schema_path, encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()


def get_setting(key, default=None):
    conn = get_db()
    try:
        setting = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
        return setting['value'] if setting else default
    finally:
        _close_if_not_from_g(conn)


def set_setting(key, value):
    conn = get_db()
    try:
        conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
        conn.commit()
    finally:
        _close_if_not_from_g(conn)


def _parse_timestamp(ts):
    if ts is None:
        return None
    try:
        if isinstance(ts, str):
            return float(ts)
        return ts
    except (ValueError, TypeError):
        return None


def import_conversations_data(data):
    """Import a list of conversation dicts into the database. Used by both web upload and CLI ingest."""
    if not isinstance(data, list):
        data = [data]
    total = len(data)
    print(f"Importing {total} conversations...")
    conn = get_db()
    imported = 0
    for conversation in data:
        try:
            conversation_id = conversation.get('id')
            if not conversation_id:
                print("Skipping conversation: missing ID")
                continue
            create_time = conversation.get('create_time', '')
            update_time = conversation.get('update_time', '')
            title = conversation.get('title', '')
            conn.execute('''
                INSERT OR REPLACE INTO conversations
                (id, create_time, update_time, title)
                VALUES (?, ?, ?, ?)
            ''', (conversation_id, create_time, update_time, title))
            messages = conversation.get('mapping', {})
            for message_id, message_data in messages.items():
                try:
                    message = message_data.get('message', {})
                    if not message:
                        continue
                    author = message.get('author', {})
                    content = message.get('content', {})
                    role = author.get('role', '')
                    content_text = json.dumps(content.get('parts', []))
                    msg_create_time = _parse_timestamp(message.get('create_time'))
                    msg_update_time = _parse_timestamp(message.get('update_time'))
                    parent_id = message_data.get('parent', '')
                    conn.execute('''
                        INSERT OR REPLACE INTO messages
                        (id, conversation_id, role, content, create_time, update_time, parent_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (message_id, conversation_id, role, content_text,
                          msg_create_time, msg_update_time, parent_id))
                    children = message_data.get('children', [])
                    if children:
                        conn.execute('DELETE FROM message_children WHERE parent_id = ?', (message_id,))
                        for child_id in children:
                            conn.execute('''
                                INSERT INTO message_children (parent_id, child_id)
                                VALUES (?, ?)
                            ''', (message_id, child_id))
                    metadata = message.get('metadata', {})
                    if metadata:
                        conn.execute('''
                            INSERT OR REPLACE INTO message_metadata
                            (message_id, message_type, model_slug, citations,
                             content_references, finish_details, is_complete,
                             request_id, timestamp_, message_source, serialization_metadata)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (
                            message_id,
                            metadata.get('message_type', ''),
                            metadata.get('model_slug', ''),
                            json.dumps(metadata.get('citations', [])),
                            json.dumps(metadata.get('content_references', [])),
                            json.dumps(metadata.get('finish_details', {})),
                            metadata.get('is_complete', False),
                            metadata.get('request_id', ''),
                            metadata.get('timestamp', ''),
                            metadata.get('message_source', ''),
                            json.dumps(metadata.get('serialization_metadata', {}))
                        ))
                except Exception as e:
                    print(f"Error processing message {message_id}: {str(e)}")
                    continue
            imported += 1
            if imported % IMPORT_BATCH_SIZE == 0:
                conn.commit()
                print(f"Imported {imported} / {total} conversations", file=sys.stderr)
        except Exception as e:
            print(f"Error processing conversation {conversation_id}: {str(e)}")
            continue
    conn.commit()
    _close_if_not_from_g(conn)
