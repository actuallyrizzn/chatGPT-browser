# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
from flask import Flask, g, render_template, request, redirect, url_for, session, jsonify
from markupsafe import Markup
import sqlite3
import json
from datetime import datetime, timezone
import markdown
from markdown.extensions import fenced_code, tables
import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.join(BASE_DIR, 'chatgpt.db')

app = Flask(__name__)

# Secret key: prefer SECRET_KEY env, then .secret_key file, else urandom (sessions invalidated on restart)
def _load_secret_key():
    key = os.environ.get("SECRET_KEY")
    if key:
        return key.encode("utf-8") if isinstance(key, str) else key
    secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".secret_key")
    if os.path.isfile(secret_file):
        with open(secret_file, "rb") as f:
            return f.read().strip()
    import warnings
    warnings.warn("SECRET_KEY not set; using random key. Sessions will be invalidated on restart. Set SECRET_KEY or create .secret_key.", UserWarning)
    return os.urandom(24)

app.secret_key = _load_secret_key()

# Limit request body size (e.g. import JSON) to avoid DoS; 100 MB default, overridable via env
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_UPLOAD_MB", "100")) * 1024 * 1024

from werkzeug.exceptions import RequestEntityTooLarge
@app.errorhandler(RequestEntityTooLarge)
def handle_413(e):
    return "Upload exceeds maximum allowed size (set MAX_UPLOAD_MB env to change limit).", 413

# Markdown: fresh instance per render to avoid state bleed; output sanitized to prevent XSS
import bleach
ALLOWED_MD_TAGS = ['p', 'br', 'strong', 'em', 'b', 'i', 'u', 'code', 'pre', 'ul', 'ol', 'li', 'a', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'span', 'div', 'hr', 'table', 'thead', 'tbody', 'tr', 'th', 'td']
ALLOWED_MD_ATTRS = {'a': ['href', 'title']}

# Add Jinja filters
@app.template_filter('fromjson')
def fromjson(value):
    try:
        return json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return []

@app.template_filter('tojson')
def tojson(value, indent=None):
    try:
        return json.dumps(value, indent=indent)
    except (TypeError, ValueError):
        return str(value)

def get_db():
    try:
        if 'db' not in g:
            conn = sqlite3.connect(DATABASE_PATH)
            conn.execute('PRAGMA foreign_keys = ON')
            conn.row_factory = sqlite3.Row
            g.db = conn
        return g.db
    except RuntimeError:
        # Outside application context (e.g. CLI, unit tests); caller must close
        conn = sqlite3.connect(DATABASE_PATH)
        conn.execute('PRAGMA foreign_keys = ON')
        conn.row_factory = sqlite3.Row
        return conn

@app.teardown_appcontext
def close_db(exc):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Create schema and defaults. Uses schema.sql as single source of truth. Uses get_db() so tests can patch it; run within app.app_context() when calling from CLI."""
    conn = get_db()
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
    with open(schema_path, encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()

def _close_if_not_from_g(conn):
    try:
        if g.get('db') is not conn:
            conn.close()
    except RuntimeError:
        conn.close()

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

@app.template_filter('datetime')
def format_datetime(timestamp):
    if timestamp is None:
        return '—'
    try:
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    except (ValueError, TypeError):
        return '—'

@app.template_filter('json_loads')
def json_loads_filter(value):
    if value is None:
        return []
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []

@app.template_filter('markdown')
def markdown_filter(text):
    if text is None:
        return ""
    # New Markdown instance per call to avoid shared state bleed between messages
    md_instance = markdown.Markdown(extensions=['fenced_code', 'tables'])
    raw_html = md_instance.convert(text)
    # Sanitize to prevent stored XSS (e.g. <script>, event handlers)
    safe_html = bleach.clean(raw_html, tags=ALLOWED_MD_TAGS, attributes=ALLOWED_MD_ATTRS, strip=True)
    return Markup(safe_html)

@app.route('/')
def index():
    per_page = min(max(int(request.args.get('per_page', 50)), 1), 100)
    page = max(int(request.args.get('page', 1)), 1)
    conn = get_db()
    total = conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0]
    total_pages = max(1, (total + per_page - 1) // per_page) if total else 1
    page = min(page, total_pages)
    offset = (page - 1) * per_page
    conversations = conn.execute('''
        SELECT id, title, create_time, update_time 
        FROM conversations 
        ORDER BY CAST(update_time AS REAL) DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset)).fetchall()
    dev_mode = get_setting('dev_mode', 'false') == 'true'
    dark_mode = get_setting('dark_mode', 'false') == 'true'
    user_name = get_setting('user_name', 'User')
    assistant_name = get_setting('assistant_name', 'Assistant')
    return render_template('index.html',
                         conversations=conversations,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         dev_mode=dev_mode,
                         dark_mode=dark_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)

@app.route('/conversation/<conversation_id>')
def conversation(conversation_id):
    # Get settings and handle overrides
    dev_mode = get_setting('dev_mode', 'false') == 'true'
    override_dev_mode = session.get('override_dev_mode', False)
    verbose_mode = get_setting('verbose_mode', 'false') == 'true'
    override_verbose_mode = session.get('override_verbose_mode', False)
    dark_mode = get_setting('dark_mode', 'false') == 'true'
    
    # If in nice mode (dev_mode is false) and no override, redirect to nice view
    if not dev_mode and not override_dev_mode:
        return redirect(url_for('nice_conversation', conversation_id=conversation_id))
    
    # Clear any existing overrides
    session.pop('override_dev_mode', None)
    session.pop('override_verbose_mode', None)
    
    conn = get_db()
    conversation = conn.execute('SELECT * FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
    
    if not conversation:
        return "Conversation not found", 404
    # Get all messages with their metadata
    messages = conn.execute('''
        SELECT m.*, 
               mm.message_type, mm.model_slug, mm.citations, mm.content_references,
               mm.finish_details, mm.is_complete, mm.request_id, mm.timestamp_,
               mm.message_source, mm.serialization_metadata
        FROM messages m
        LEFT JOIN message_metadata mm ON m.id = mm.message_id
        WHERE m.conversation_id = ?
        ORDER BY m.create_time
    ''', (conversation_id,)).fetchall()
    
    message_list = [message_row_to_dict(msg) for msg in messages]
    _attach_content_parts(message_list)

    dev_mode = get_setting('dev_mode', 'false') == 'true'
    dark_mode = get_setting('dark_mode', 'false') == 'true'
    user_name = get_setting('user_name', 'User')
    assistant_name = get_setting('assistant_name', 'Assistant')
    
    return render_template('conversation.html',
                         conversation=conversation,
                         messages=message_list,
                         dev_mode=dev_mode,
                         verbose_mode=verbose_mode or override_verbose_mode,
                         dark_mode=dark_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)

@app.route('/conversation/<conversation_id>/nice')
def nice_conversation(conversation_id):
    conn = get_db()
    conversation = conn.execute('SELECT * FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
    
    if not conversation:
        return "Conversation not found", 404
    
    # Find the canonical endpoint
    canonical_endpoint = conn.execute('''
        SELECT m.id, m.role, m.content, m.create_time, m.parent_id
        FROM messages m
        LEFT JOIN messages child ON m.id = child.parent_id
        WHERE m.conversation_id = ? AND child.id IS NULL
        ORDER BY m.create_time DESC
        LIMIT 1
    ''', (conversation_id,)).fetchone()
    
    if not canonical_endpoint:
        return "No canonical endpoint found", 404
    
    # Get the path from endpoint to root in one query (recursive CTE; no conversation_id filter so branches work)
    endpoint_id = canonical_endpoint['id']
    path_rows = conn.execute('''
        WITH RECURSIVE path AS (
            SELECT m.id, m.conversation_id, m.role, m.content, m.create_time, m.update_time, m.parent_id,
                   mm.message_type, mm.model_slug, mm.citations, mm.content_references,
                   mm.finish_details, mm.is_complete, mm.request_id, mm.timestamp_,
                   mm.message_source, mm.serialization_metadata
            FROM messages m
            LEFT JOIN message_metadata mm ON m.id = mm.message_id
            WHERE m.id = ?
            UNION ALL
            SELECT m.id, m.conversation_id, m.role, m.content, m.create_time, m.update_time, m.parent_id,
                   mm.message_type, mm.model_slug, mm.citations, mm.content_references,
                   mm.finish_details, mm.is_complete, mm.request_id, mm.timestamp_,
                   mm.message_source, mm.serialization_metadata
            FROM messages m
            LEFT JOIN message_metadata mm ON m.id = mm.message_id
            INNER JOIN path p ON m.id = p.parent_id
        )
        SELECT * FROM path
    ''', (endpoint_id,)).fetchall()
    path = [message_row_to_dict(message) for message in path_rows]
    _attach_content_parts(path)

    # In Nice view, hide system messages and messages with no displayable content
    path = [m for m in path if m.get('role') != 'system' and _message_has_displayable_content(m)]
    
    # Get total message count for the conversation
    total_messages = conn.execute('''
        SELECT COUNT(*) as count
        FROM messages
        WHERE conversation_id = ?
    ''', (conversation_id,)).fetchone()['count']
    
    dev_mode = get_setting('dev_mode', 'false') == 'true'
    dark_mode = get_setting('dark_mode', 'false') == 'true'
    verbose_mode = get_setting('verbose_mode', 'false') == 'true'
    override_verbose_mode = session.get('override_verbose_mode', False)
    user_name = get_setting('user_name', 'User')
    assistant_name = get_setting('assistant_name', 'Assistant')
    
    return render_template('nice_conversation.html',
                         conversation=conversation,
                         canonical_path=path,
                         total_messages=total_messages,
                         dev_mode=dev_mode,
                         verbose_mode=verbose_mode or override_verbose_mode,
                         dark_mode=dark_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)

@app.route('/conversation/<conversation_id>/full')
def full_conversation(conversation_id):
    session['override_dev_mode'] = True
    return redirect(url_for('conversation', conversation_id=conversation_id))

def _parse_timestamp(ts):
    if ts is None:
        return None
    try:
        if isinstance(ts, str):
            return float(ts)
        return ts
    except (ValueError, TypeError):
        return None


def _message_has_displayable_content(message):
    """True if message has at least one non-empty part (for hiding empty/system bubbles in Nice view)."""
    content = message.get('content_parts')
    if content is None:
        content = message.get('content')
    if content is None:
        return False
    if isinstance(content, str):
        try:
            content = json.loads(content) if content.strip() else []
        except (TypeError, ValueError):
            return False
    if not content or not isinstance(content, list):
        return False
    for part in content:
        if part is None:
            continue
        if isinstance(part, str) and part.strip():
            return True
        if isinstance(part, dict):
            return True  # dict parts are shown (e.g. as JSON) so consider as content
    return False

def message_row_to_dict(row):
    """Convert a message row (with optional metadata columns from JOIN) to a dict with nested metadata."""
    d = dict(row)
    if d.get('message_type'):
        d['metadata'] = {
            'message_type': d.pop('message_type', None),
            'model_slug': d.pop('model_slug', None),
            'citations': d.pop('citations', None),
            'content_references': d.pop('content_references', None),
            'finish_details': d.pop('finish_details', None),
            'is_complete': d.pop('is_complete', None),
            'request_id': d.pop('request_id', None),
            'timestamp_': d.pop('timestamp_', None),
            'message_source': d.pop('message_source', None),
            'serialization_metadata': d.pop('serialization_metadata', None),
        }
    return d

def _attach_content_parts(message_list):
    """Parse each message's content JSON once and attach as content_parts (fixes #31)."""
    for m in message_list:
        try:
            m['content_parts'] = json.loads(m['content']) if m.get('content') else []
        except (TypeError, ValueError, json.JSONDecodeError):
            m['content_parts'] = []

IMPORT_BATCH_SIZE = 50  # Commit every N conversations for partial progress and lower memory use

def import_conversations_data(data):
    """Import a list of conversation dicts into the database. Used by both web upload and CLI ingest.
    Commits in batches (IMPORT_BATCH_SIZE) so partial progress is persisted if the process fails."""
    if not isinstance(data, list):
        data = [data]
    total = len(data)
    print(f"Importing {total} conversations...")
    conn = get_db()
    imported = 0
    for conversation in data:
        try:
            # Extract conversation data
            conversation_id = conversation.get('id')
            if not conversation_id:
                print(f"Skipping conversation: missing ID")
                continue
            create_time = conversation.get('create_time', '')
            update_time = conversation.get('update_time', '')
            title = conversation.get('title', '')
            # Insert conversation
            conn.execute('''
                INSERT OR REPLACE INTO conversations 
                (id, create_time, update_time, title)
                VALUES (?, ?, ?, ?)
            ''', (conversation_id, create_time, update_time, title))
            # Process messages
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

@app.route('/import', methods=['POST'])
def import_json():
    # Accept both 'file' and 'json_file' for compatibility with different form names
    file = request.files.get('file') or request.files.get('json_file')
    if not file:
        return 'No file uploaded', 400
    if file.filename == '':
        return 'No file selected', 400
    try:
        content = file.read()
        if not content:
            return 'Empty file', 400
        data = json.loads(content)
        import_conversations_data(data)
        return redirect(url_for('index'))
    except json.JSONDecodeError:
        return 'Invalid JSON file', 400
    except Exception as e:
        return f'Error importing file: {str(e)}', 400

@app.route('/toggle_view_mode', methods=['POST'])
def toggle_view_mode():
    current = get_setting('dev_mode', 'false')
    new_value = 'false' if current == 'true' else 'true'
    set_setting('dev_mode', new_value)
    if request.args.get('redirect'):
        return redirect(request.referrer or url_for('index'))
    return jsonify({'success': True, 'dev_mode': new_value == 'true'})

@app.route('/toggle_dark_mode', methods=['POST'])
def toggle_dark_mode():
    current_mode = get_setting('dark_mode', 'false')
    new_mode = 'true' if current_mode == 'false' else 'false'
    set_setting('dark_mode', new_mode)
    return redirect(request.referrer or url_for('index'))

@app.route('/toggle_verbose_mode', methods=['POST'])
def toggle_verbose_mode():
    if request.args.get('temp') == 'true':
        session['override_verbose_mode'] = not session.get('override_verbose_mode', False)
        return jsonify({'success': True, 'verbose_mode': session.get('override_verbose_mode')})
    else:
        current = get_setting('verbose_mode', 'false')
        new_value = 'false' if current == 'true' else 'true'
        set_setting('verbose_mode', new_value)
        return jsonify({'success': True, 'verbose_mode': new_value == 'true'})

@app.route('/settings')
def settings():
    dev_mode = get_setting('dev_mode', 'false') == 'true'
    dark_mode = get_setting('dark_mode', 'false') == 'true'
    verbose_mode = get_setting('verbose_mode', 'false') == 'true'
    user_name = get_setting('user_name', 'User')
    assistant_name = get_setting('assistant_name', 'Assistant')
    return render_template('settings.html',
                         dev_mode=dev_mode,
                         dark_mode=dark_mode,
                         verbose_mode=verbose_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)

@app.route('/update_names', methods=['POST'])
def update_names():
    user_name = request.form.get('user_name', 'User')
    assistant_name = request.form.get('assistant_name', 'Assistant')
    
    # Update settings in database
    conn = get_db()
    conn.execute('UPDATE settings SET value = ? WHERE key = ?', (user_name, 'user_name'))
    conn.execute('UPDATE settings SET value = ? WHERE key = ?', (assistant_name, 'assistant_name'))
    conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 