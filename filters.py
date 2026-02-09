# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
"""Jinja template filters and content-part rendering. Registered on the Flask app by app.py."""

import json
import re
from datetime import datetime, timezone

import bleach
import markdown
from markupsafe import Markup

ALLOWED_MD_TAGS = [
    'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'code', 'pre', 'ul', 'ol', 'li', 'a',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'blockquote', 'span', 'div', 'hr',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
]
ALLOWED_MD_ATTRS = {'a': ['href', 'title']}


def fromjson(value):
    try:
        return json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def tojson(value, indent=None):
    try:
        return json.dumps(value, indent=indent)
    except (TypeError, ValueError):
        return str(value)


def format_datetime(timestamp):
    if timestamp is None:
        return '—'
    try:
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')
    except (ValueError, TypeError):
        return '—'


def relativetime(timestamp):
    """Format timestamp as relative time (e.g. '2 hours ago', 'Yesterday') for #52."""
    if timestamp is None:
        return '—'
    try:
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        now = datetime.now(tz=timezone.utc).timestamp()
        diff = now - timestamp
        if diff < 0:
            diff = 0
        if diff < 60:
            return 'just now'
        if diff < 3600:
            m = int(diff / 60)
            return f'{m} min ago' if m != 1 else '1 min ago'
        if diff < 86400:
            h = int(diff / 3600)
            return f'{h} hour{"s" if h != 1 else ""} ago'
        if diff < 2 * 86400:
            return 'Yesterday'
        if diff < 7 * 86400:
            d = int(diff / 86400)
            return f'{d} days ago'
        return format_datetime(timestamp)
    except (ValueError, TypeError):
        return '—'


def json_loads_filter(value):
    if value is None:
        return []
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []


def markdown_filter(text):
    if text is None:
        return ""
    md_instance = markdown.Markdown(extensions=['fenced_code', 'tables'])
    raw_html = md_instance.convert(text)
    safe_html = bleach.clean(raw_html, tags=ALLOWED_MD_TAGS, attributes=ALLOWED_MD_ATTRS, strip=True)
    return Markup(safe_html)


def _render_content_part(part, dev_mode=False):
    """Render a single message content part (string or dict) as safe HTML. Content-type dispatch for #35, #39."""
    if part is None:
        return Markup('')
    if isinstance(part, str):
        if not dev_mode and part:
            part = re.sub(r'turn0news(\d+)', r'[\1]', part)
        return markdown_filter(part)
    if not isinstance(part, dict):
        return Markup(bleach.clean(str(part), tags=[], strip=True)) if str(part) else Markup('')
    ct = part.get('content_type') or part.get('type') or ''
    if ct == 'text':
        return markdown_filter(part.get('text') or '')
    if ct == 'image_asset_pointer':
        w, h = part.get('width'), part.get('height')
        size = f'{w}×{h}' if (w is not None and h is not None) else ''
        return Markup(f'<span class="content-placeholder content-placeholder-image">[Image{(": " + size) if size else ""}]</span>')
    if ct == 'audio_transcription':
        text = part.get('text') or ''
        out = markdown_filter(text)
        if text.strip():
            return Markup('<span class="content-placeholder content-placeholder-voice" aria-label="Voice">🎤 </span>') + out
        return out
    if ct == 'audio_asset_pointer':
        return Markup('<span class="content-placeholder content-placeholder-audio">[Audio]</span>')
    if ct in ('real_time_user_audio_video_asset_pointer', 'video_container_asset_pointer'):
        return Markup('<span class="content-placeholder content-placeholder-video">[Video]</span>')
    if ct in ('navlist', 'citation', 'search_result') or 'navlist' in str(part.get('type', '')):
        return Markup('<span class="content-placeholder content-placeholder-citation">[Citation]</span>')
    if dev_mode:
        try:
            raw = json.dumps(part, indent=2)
            safe = bleach.clean(raw, tags=[], strip=True)
            return Markup(f'<pre class="content-json"><code>{safe}</code></pre>')
        except (TypeError, ValueError):
            return Markup('<span class="content-placeholder">[Content]</span>')
    return Markup('<span class="content-placeholder">[Content]</span>')


def render_part_filter(part, dev_mode=False):
    """Template filter: render one message content part (string or dict) with content-type dispatch."""
    return _render_content_part(part, dev_mode=bool(dev_mode))


def register_filters(app):
    """Register all template filters on the Flask app."""
    app.template_filter('fromjson')(fromjson)
    app.template_filter('tojson')(tojson)
    app.template_filter('datetime')(format_datetime)
    app.template_filter('relativetime')(relativetime)
    app.template_filter('json_loads')(json_loads_filter)
    app.template_filter('markdown')(markdown_filter)
    app.template_filter('render_part')(render_part_filter)
