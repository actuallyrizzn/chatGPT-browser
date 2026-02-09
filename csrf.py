# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# CSRF token generation and validation (#4, #10).

import hmac
import secrets

from flask import request, session


def get_csrf_token():
    """Return session-bound CSRF token; create if missing."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']


def validate_csrf():
    """Validate CSRF from form (csrf_token) or header (X-CSRFToken). Returns None or (body, status_code)."""
    token = session.get('csrf_token')
    if not token:
        return ('CSRF token missing.', 403)
    provided = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
    if not provided or not hmac.compare_digest(token, provided):
        return ('Invalid CSRF token.', 403)
    return None
