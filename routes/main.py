# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
"""Main routes: index, conversations, import, settings, toggles."""

import json

from flask import Blueprint, flash, make_response, redirect, render_template, request, session, url_for

import db
from csrf import validate_csrf
from content_helpers import (
    _attach_content_parts,
    _message_has_displayable_content,
    message_row_to_dict,
)

bp = Blueprint('main', __name__)


MESSAGE_PAGE_SIZE = 50  # full conversation view pagination (#29)


@bp.route('/')
def index():
    per_page = min(max(int(request.args.get('per_page', 50)), 1), 100)
    page = max(int(request.args.get('page', 1)), 1)
    q = (request.args.get('q') or '').strip()
    conn = db.get_db()
    if q:
        total = conn.execute(
            'SELECT COUNT(*) FROM conversations WHERE title LIKE ?',
            ('%' + q + '%',),
        ).fetchone()[0]
        offset = (page - 1) * per_page
        conversations = conn.execute('''
            SELECT c.id, c.title, c.create_time, c.update_time,
                   (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) AS message_count
            FROM conversations c
            WHERE c.title LIKE ?
            ORDER BY CAST(c.update_time AS REAL) DESC
            LIMIT ? OFFSET ?
        ''', ('%' + q + '%', per_page, offset)).fetchall()
    else:
        total = conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0]
        offset = (page - 1) * per_page
        conversations = conn.execute('''
            SELECT c.id, c.title, c.create_time, c.update_time,
                   (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) AS message_count
            FROM conversations c
            ORDER BY CAST(c.update_time AS REAL) DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
    total_pages = max(1, (total + per_page - 1) // per_page) if total else 1
    page = min(page, total_pages)
    dev_mode = db.get_setting('dev_mode', 'false') == 'true'
    dark_mode = db.get_setting('dark_mode', 'false') == 'true'
    user_name = db.get_setting('user_name', 'User')
    assistant_name = db.get_setting('assistant_name', 'Assistant')
    try:
        pinned_ids = json.loads(db.get_setting('pinned_conversation_ids', '[]'))
    except (TypeError, ValueError, json.JSONDecodeError):
        pinned_ids = []
    return render_template('index.html',
                         conversations=conversations,
                         page=page,
                         per_page=per_page,
                         total=total,
                         total_pages=total_pages,
                         q=q,
                         pinned_ids=pinned_ids,
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
    total_messages = conn.execute(
        'SELECT COUNT(*) FROM messages WHERE conversation_id = ?',
        (conversation_id,),
    ).fetchone()[0]
    msg_page = max(int(request.args.get('page', 1)), 1)
    msg_per_page = MESSAGE_PAGE_SIZE
    msg_total_pages = max(1, (total_messages + msg_per_page - 1) // msg_per_page) if total_messages else 1
    msg_page = min(msg_page, msg_total_pages)
    offset = (msg_page - 1) * msg_per_page
    messages = conn.execute('''
        SELECT m.*,
               mm.message_type, mm.model_slug, mm.citations, mm.content_references,
               mm.finish_details, mm.is_complete, mm.request_id, mm.timestamp_,
               mm.message_source, mm.serialization_metadata
        FROM messages m
        LEFT JOIN message_metadata mm ON m.id = mm.message_id
        WHERE m.conversation_id = ?
        ORDER BY m.create_time
        LIMIT ? OFFSET ?
    ''', (conversation_id, msg_per_page, offset)).fetchall()

    message_list = [message_row_to_dict(msg) for msg in messages]
    _attach_content_parts(message_list)

    dev_mode = db.get_setting('dev_mode', 'false') == 'true'
    dark_mode = db.get_setting('dark_mode', 'false') == 'true'
    user_name = db.get_setting('user_name', 'User')
    assistant_name = db.get_setting('assistant_name', 'Assistant')

    msg_start = (msg_page - 1) * msg_per_page + 1
    msg_end = min(msg_page * msg_per_page, total_messages) if total_messages else 0
    return render_template('conversation.html',
                         conversation=conversation,
                         messages=message_list,
                         total_messages=total_messages,
                         message_page=msg_page,
                         message_total_pages=msg_total_pages,
                         message_per_page=msg_per_page,
                         message_start=msg_start,
                         message_end=msg_end,
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
    err = validate_csrf()
    if err:
        return err[0], err[1]
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
        n = db.import_conversations_data(data)
        flash(f'Imported {n} conversation{"s" if n != 1 else ""}.')
        return redirect(url_for('main.index'))
    except json.JSONDecodeError:
        return 'Invalid JSON file', 400
    except Exception as e:
        return f'Error importing file: {str(e)}', 400


@bp.route('/conversation/<conversation_id>/pin', methods=['POST'])
def toggle_pin(conversation_id):
    """Toggle pinned/favorite state for a conversation (#61). Stored in settings as JSON array."""
    err = validate_csrf()
    if err:
        return err[0], err[1]
    conn = db.get_db()
    if conn.execute('SELECT id FROM conversations WHERE id = ?', (conversation_id,)).fetchone() is None:
        return "Conversation not found", 404
    try:
        pinned = json.loads(db.get_setting('pinned_conversation_ids', '[]'))
    except (TypeError, ValueError, json.JSONDecodeError):
        pinned = []
    if conversation_id in pinned:
        pinned = [x for x in pinned if x != conversation_id]
    else:
        pinned = list(pinned) + [conversation_id]
    db.set_setting('pinned_conversation_ids', json.dumps(pinned))
    return redirect(request.referrer or url_for('main.index'))


@bp.route('/conversation/<conversation_id>/delete', methods=['POST'])
def delete_conversation(conversation_id):
    err = validate_csrf()
    if err:
        return err[0], err[1]
    conn = db.get_db()
    conversation = conn.execute('SELECT id FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
    if not conversation:
        return "Conversation not found", 404
    conn.execute('DELETE FROM message_metadata WHERE message_id IN (SELECT id FROM messages WHERE conversation_id = ?)', (conversation_id,))
    conn.execute('DELETE FROM message_children WHERE parent_id IN (SELECT id FROM messages WHERE conversation_id = ?) OR child_id IN (SELECT id FROM messages WHERE conversation_id = ?)', (conversation_id, conversation_id))
    conn.execute('DELETE FROM messages WHERE conversation_id = ?', (conversation_id,))
    conn.execute('DELETE FROM conversations WHERE id = ?', (conversation_id,))
    conn.commit()
    flash('Conversation deleted.')
    return redirect(url_for('main.index'))


def _build_export_mapping(conn, conversation_id):
    """Build ChatGPT-style mapping for one conversation (id -> { message, parent, children })."""
    messages = conn.execute('''
        SELECT m.id, m.role, m.content, m.create_time, m.update_time, m.parent_id,
               mm.message_type, mm.model_slug, mm.citations, mm.content_references,
               mm.finish_details, mm.is_complete, mm.request_id, mm.timestamp_,
               mm.message_source, mm.serialization_metadata
        FROM messages m
        LEFT JOIN message_metadata mm ON m.id = mm.message_id
        WHERE m.conversation_id = ?
        ORDER BY m.create_time
    ''', (conversation_id,)).fetchall()
    children_map = {}
    for cr in conn.execute(
        'SELECT parent_id, child_id FROM message_children WHERE parent_id IN (SELECT id FROM messages WHERE conversation_id = ?)',
        (conversation_id,),
    ).fetchall():
        cr = dict(cr)
        children_map.setdefault(cr['parent_id'], []).append(cr['child_id'])
    mapping = {}
    for row in messages:
        m = dict(row)
        mid = m['id']
        try:
            parts = json.loads(m['content']) if m['content'] else []
        except (TypeError, ValueError, json.JSONDecodeError):
            parts = []
        meta = {}
        if m.get('message_type') is not None:
            meta = {
                'message_type': m.get('message_type') or '',
                'model_slug': m.get('model_slug') or '',
                'citations': json.loads(m['citations']) if m.get('citations') else [],
                'content_references': json.loads(m['content_references']) if m.get('content_references') else [],
                'finish_details': json.loads(m['finish_details']) if m.get('finish_details') else {},
                'is_complete': bool(m.get('is_complete')),
                'request_id': m.get('request_id') or '',
                'timestamp': m.get('timestamp_') or '',
                'message_source': m.get('message_source') or '',
                'serialization_metadata': json.loads(m['serialization_metadata']) if m.get('serialization_metadata') else {},
            }
        mapping[mid] = {
            'message': {
                'author': {'role': m['role'] or ''},
                'content': {'parts': parts},
                'create_time': m['create_time'],
                'update_time': m['update_time'],
                **({'metadata': meta} if meta else {}),
            },
            'parent': m['parent_id'] or '',
            'children': children_map.get(mid, []),
        }
    return mapping


@bp.route('/conversation/<conversation_id>/export/json')
def export_conversation_json(conversation_id):
    conn = db.get_db()
    conversation = conn.execute('SELECT id, create_time, update_time, title FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
    if not conversation:
        return "Conversation not found", 404
    payload = {
        'id': conversation['id'],
        'create_time': conversation['create_time'],
        'update_time': conversation['update_time'],
        'title': conversation['title'],
        'mapping': _build_export_mapping(conn, conversation_id),
    }
    resp = make_response(json.dumps(payload, indent=2))
    resp.headers['Content-Type'] = 'application/json; charset=utf-8'
    resp.headers['Content-Disposition'] = f'attachment; filename="conversation-{conversation_id[:20]}.json"'
    return resp


@bp.route('/conversation/<conversation_id>/export/markdown')
def export_conversation_markdown(conversation_id):
    conn = db.get_db()
    conversation = conn.execute('SELECT id, title FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
    if not conversation:
        return "Conversation not found", 404
    messages = conn.execute('''
        SELECT role, content, create_time
        FROM messages
        WHERE conversation_id = ?
        ORDER BY create_time
    ''', (conversation_id,)).fetchall()
    lines = [f"# {conversation['title']}", ""]
    for m in messages:
        role = (m['role'] or 'user').capitalize()
        try:
            parts = json.loads(m['content']) if m['content'] else []
        except (TypeError, ValueError, json.JSONDecodeError):
            parts = [m['content'] or '']
        text_parts = []
        for p in parts:
            if isinstance(p, str):
                text_parts.append(p)
            elif isinstance(p, dict) and (p.get('content_type') or p.get('type')) == 'text':
                text_parts.append(p.get('text') or '')
        body = '\n'.join(text_parts).strip()
        if body:
            lines.append(f"**{role}:**")
            lines.append("")
            lines.append(body)
            lines.append("")
    md = '\n'.join(lines)
    resp = make_response(md)
    resp.headers['Content-Type'] = 'text/markdown; charset=utf-8'
    resp.headers['Content-Disposition'] = f'attachment; filename="conversation-{conversation_id[:20]}.md"'
    return resp


@bp.route('/toggle_view_mode', methods=['POST'])
def toggle_view_mode():
    from flask import jsonify
    err = validate_csrf()
    if err:
        return err[0], err[1]
    current = db.get_setting('dev_mode', 'false')
    new_value = 'false' if current == 'true' else 'true'
    db.set_setting('dev_mode', new_value)
    if request.args.get('redirect'):
        return redirect(request.referrer or url_for('main.index'))
    return jsonify({'success': True, 'dev_mode': new_value == 'true'})


@bp.route('/toggle_dark_mode', methods=['POST'])
def toggle_dark_mode():
    from flask import jsonify
    err = validate_csrf()
    if err:
        return err[0], err[1]
    current_mode = db.get_setting('dark_mode', 'false')
    new_mode = 'true' if current_mode == 'false' else 'false'
    db.set_setting('dark_mode', new_mode)
    if request.accept_mimetypes.best_match(['application/json', 'text/html']) == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'dark_mode': new_mode == 'true'})
    return redirect(request.referrer or url_for('main.index'))


@bp.route('/toggle_verbose_mode', methods=['POST'])
def toggle_verbose_mode():
    from flask import jsonify
    err = validate_csrf()
    if err:
        return err[0], err[1]
    if request.args.get('temp') == 'true':
        session['override_verbose_mode'] = not session.get('override_verbose_mode', False)
        return jsonify({'success': True, 'verbose_mode': session.get('override_verbose_mode')})
    current = db.get_setting('verbose_mode', 'false')
    new_value = 'false' if current == 'true' else 'true'
    db.set_setting('verbose_mode', new_value)
    return jsonify({'success': True, 'verbose_mode': new_value == 'true'})


@bp.route('/stats')
def stats():
    """Conversation statistics dashboard (#58)."""
    conn = db.get_db()
    total_conversations = conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0]
    total_messages = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
    avg_messages = (total_messages / total_conversations) if total_conversations else 0
    # Conversations per week (by update_time as Unix week)
    by_week = conn.execute('''
        SELECT CAST(CAST(update_time AS REAL) / 604800 AS INTEGER) AS week_key,
               COUNT(*) AS cnt
        FROM conversations
        WHERE update_time IS NOT NULL AND update_time != ''
        GROUP BY week_key
        ORDER BY week_key DESC
        LIMIT 20
    ''').fetchall()
    dev_mode = db.get_setting('dev_mode', 'false') == 'true'
    dark_mode = db.get_setting('dark_mode', 'false') == 'true'
    return render_template('stats.html',
                         total_conversations=total_conversations,
                         total_messages=total_messages,
                         avg_messages=avg_messages,
                         by_week=by_week,
                         dev_mode=dev_mode,
                         dark_mode=dark_mode)


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
    err = validate_csrf()
    if err:
        return err[0], err[1]
    user_name = request.form.get('user_name', 'User')
    assistant_name = request.form.get('assistant_name', 'Assistant')

    conn = db.get_db()
    conn.execute('UPDATE settings SET value = ? WHERE key = ?', (user_name, 'user_name'))
    conn.execute('UPDATE settings SET value = ? WHERE key = ?', (assistant_name, 'assistant_name'))
    conn.commit()
    flash('Settings saved.')
    return redirect(url_for('main.settings'))
