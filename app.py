# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
"""Flask app: creation, config, blueprint and filter registration."""

import os

from flask import Flask, has_request_context, request
from werkzeug.exceptions import RequestEntityTooLarge

import db
from csrf import get_csrf_token
from filters import register_filters
from routes.main import bp as main_bp


def _load_secret_key():
    key = os.environ.get("SECRET_KEY")
    if key:
        return key.encode("utf-8") if isinstance(key, str) else key
    secret_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".secret_key")
    if os.path.isfile(secret_file):
        with open(secret_file, "rb") as f:
            return f.read().strip()
    import warnings
    warnings.warn(
        "SECRET_KEY not set; using random key. Sessions will be invalidated on restart. Set SECRET_KEY or create .secret_key.",
        UserWarning,
    )
    return os.urandom(24)


app = Flask(__name__)
app.secret_key = _load_secret_key()
app.config["MAX_CONTENT_LENGTH"] = int(os.environ.get("MAX_UPLOAD_MB", "100")) * 1024 * 1024

app.teardown_appcontext(db.close_db)
register_filters(app)
app.register_blueprint(main_bp)


@app.context_processor
def inject_csrf_token():
    """Inject csrf_token into all templates for forms and AJAX (#4, #10)."""
    in_request = has_request_context()
    return {
        "csrf_token": get_csrf_token() if in_request else "",
        # Avoid templates directly depending on `request` (LocalProxy) when rendering
        # outside a request context (e.g. scripts, offline rendering).
        "active_endpoint": request.endpoint if in_request else None,
    }


@app.errorhandler(RequestEntityTooLarge)
def handle_413(e):
    return "Upload exceeds maximum allowed size (set MAX_UPLOAD_MB env to change limit).", 413


@app.after_request
def add_static_cache_headers(response):
    """Set Cache-Control for static assets (#30)."""
    if request.path.startswith('/static/'):
        response.cache_control.max_age = 3600
        response.cache_control.public = True
    return response


# Re-export for CLI and tests that import from app
get_db = db.get_db
init_db = db.init_db
get_setting = db.get_setting
set_setting = db.set_setting
import_conversations_data = db.import_conversations_data
DATABASE_PATH = db.DATABASE_PATH

# Re-export for tests that assert on app module (e.g. test_filters, test_content_render, test_helpers)
from filters import (  # noqa: E402
    _render_content_part,
    format_datetime,
    fromjson,
    json_loads_filter,
    markdown_filter,
    relativetime,
    tojson,
)
from db import _parse_timestamp  # noqa: E402

if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(debug=True)
