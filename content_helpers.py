# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
"""Message content helpers: row-to-dict conversion and content_parts attachment. Used by routes."""

import json


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
            return True
    return False
