# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
"""Main routes: index, conversations, import, settings, toggles."""

import json

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

import db
from content_helpers import (
    _attach_content_parts,
    _message_has_displayable_content,
    message_row_to_dict,
)

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    per_page = min(max(int(request.args.get('per_page', 50)), 1), 100)
    page = max(int(request.args.get('page', 1)), 1)
    conn = db.get_db()
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
    dev_mode = db.get_setting('dev_mode', 'false') == 'true'
    dark_mode = db.get_setting('dark_mode', 'false') == 'true'
    user_name = db.get_setting('user_name', 'User')
    assistant_name = db.get_setting('assistant_name', 'Assistant')
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


@bp.route('/conversation/<conversation_id>')
def conversation(conversation_id):
    dev_mode = db.get_setting('dev_mode', 'false') == 'true'
    override_dev_mode = session.get('override_dev_mode', False)
    verbose_mode = db.get_setting('verbose_mode', 'false') == 'true'
    override_verbose_mode = session.get('override_verbose_mode', False)
    dark_mode = db.get_setting('dark_mode', 'false') == 'true'

    if not dev_mode and not override_dev_mode:
        return redirect(url_for('main.nice_conversation', conversation_id=conversation_id))

    session.pop('override_dev_mode', None)
    session.pop('override_verbose_mode', None)

    conn = db.get_db()
    conversation = conn.execute('SELECT * FROM conversations WHERE id = ?', (conversation_id,)).fetchone()

    if not conversation:
        return "Conversation not found", 404
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

    dev_mode = db.get_setting('dev_mode', 'false') == 'true'
    dark_mode = db.get_setting('dark_mode', 'false') == 'true'
    user_name = db.get_setting('user_name', 'User')
    assistant_name = db.get_setting('assistant_name', 'Assistant')

    return render_template('conversation.html',
                         conversation=conversation,
                         messages=message_list,
                         dev_mode=dev_mode,
                         verbose_mode=verbose_mode or override_verbose_mode,
                         dark_mode=dark_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)


@bp.route('/conversation/<conversation_id>/nice')
def nice_conversation(conversation_id):
    conn = db.get_db()
    conversation = conn.execute('SELECT * FROM conversations WHERE id = ?', (conversation_id,)).fetchone()

    if not conversation:
        return "Conversation not found", 404

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

    path = [m for m in path if m.get('role') != 'system' and _message_has_displayable_content(m)]

    total_messages = conn.execute('''
        SELECT COUNT(*) as count
        FROM messages
        WHERE conversation_id = ?
    ''', (conversation_id,)).fetchone()['count']

    dev_mode = db.get_setting('dev_mode', 'false') == 'true'
    dark_mode = db.get_setting('dark_mode', 'false') == 'true'
    verbose_mode = db.get_setting('verbose_mode', 'false') == 'true'
    override_verbose_mode = session.get('override_verbose_mode', False)
    user_name = db.get_setting('user_name', 'User')
    assistant_name = db.get_setting('assistant_name', 'Assistant')

    return render_template('nice_conversation.html',
                         conversation=conversation,
                         canonical_path=path,
                         total_messages=total_messages,
                         dev_mode=dev_mode,
                         verbose_mode=verbose_mode or override_verbose_mode,
                         dark_mode=dark_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)


@bp.route('/conversation/<conversation_id>/full')
def full_conversation(conversation_id):
    session['override_dev_mode'] = True
    return redirect(url_for('main.conversation', conversation_id=conversation_id))


@bp.route('/import', methods=['POST'])
def import_json():
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
        db.import_conversations_data(data)
        return redirect(url_for('main.index'))
    except json.JSONDecodeError:
        return 'Invalid JSON file', 400
    except Exception as e:
        return f'Error importing file: {str(e)}', 400


@bp.route('/toggle_view_mode', methods=['POST'])
def toggle_view_mode():
    from flask import jsonify
    current = db.get_setting('dev_mode', 'false')
    new_value = 'false' if current == 'true' else 'true'
    db.set_setting('dev_mode', new_value)
    if request.args.get('redirect'):
        return redirect(request.referrer or url_for('main.index'))
    return jsonify({'success': True, 'dev_mode': new_value == 'true'})


@bp.route('/toggle_dark_mode', methods=['POST'])
def toggle_dark_mode():
    from flask import jsonify
    current_mode = db.get_setting('dark_mode', 'false')
    new_mode = 'true' if current_mode == 'false' else 'false'
    db.set_setting('dark_mode', new_mode)
    if request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'dark_mode': new_mode == 'true'})
    return redirect(request.referrer or url_for('main.index'))


@bp.route('/toggle_verbose_mode', methods=['POST'])
def toggle_verbose_mode():
    from flask import jsonify
    if request.args.get('temp') == 'true':
        session['override_verbose_mode'] = not session.get('override_verbose_mode', False)
        return jsonify({'success': True, 'verbose_mode': session.get('override_verbose_mode')})
    current = db.get_setting('verbose_mode', 'false')
    new_value = 'false' if current == 'true' else 'true'
    db.set_setting('verbose_mode', new_value)
    return jsonify({'success': True, 'verbose_mode': new_value == 'true'})


@bp.route('/settings')
def settings():
    dev_mode = db.get_setting('dev_mode', 'false') == 'true'
    dark_mode = db.get_setting('dark_mode', 'false') == 'true'
    verbose_mode = db.get_setting('verbose_mode', 'false') == 'true'
    user_name = db.get_setting('user_name', 'User')
    assistant_name = db.get_setting('assistant_name', 'Assistant')
    return render_template('settings.html',
                         dev_mode=dev_mode,
                         dark_mode=dark_mode,
                         verbose_mode=verbose_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)


@bp.route('/update_names', methods=['POST'])
def update_names():
    user_name = request.form.get('user_name', 'User')
    assistant_name = request.form.get('assistant_name', 'Assistant')

    conn = db.get_db()
    conn.execute('UPDATE settings SET value = ? WHERE key = ?', (user_name, 'user_name'))
    conn.execute('UPDATE settings SET value = ? WHERE key = ?', (assistant_name, 'assistant_name'))
    conn.commit()
    flash('Settings saved.')
    return redirect(url_for('main.settings'))
