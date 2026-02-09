# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
# Copyright (C) 2024-2025. Licensed under the GNU AGPLv3. See LICENSE.
"""
Pytest configuration and fixtures for ChatGPT Browser tests.
"""

import os
import sqlite3
import tempfile
import threading
import time

import pytest

# Import module so we can patch get_db on the module (app.get_db is module-level)
import app as app_module
from app import app, g, get_db, init_db


@pytest.fixture
def client():
    """Create a test client (uses default DB unless test_db is also used)."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


@pytest.fixture
def test_db():
    """Create a temporary test database and patch app module get_db."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    original_get_db = app_module.get_db

    def get_test_db():
        try:
            if "db" not in g:
                conn = sqlite3.connect(db_path)
                conn.row_factory = sqlite3.Row
                g.db = conn
            return g.db
        except RuntimeError:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn

    app_module.get_db = get_test_db
    with app.app_context():
        init_db()

    yield db_path

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass
    app_module.get_db = original_get_db


@pytest.fixture
def client_with_db(test_db):
    """Test client that uses the temporary test database."""
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as c:
        yield c


@pytest.fixture
def sample_conversation():
    """Provide sample conversation data for testing."""
    return {
        "id": "test-conversation-123",
        "title": "Test Conversation",
        "create_time": "1640995200.0",
        "update_time": "1640995800.0",
    }


@pytest.fixture
def sample_message():
    """Provide sample message data for testing."""
    return {
        "id": "test-message-123",
        "conversation_id": "test-conversation-123",
        "role": "user",
        "content": '[{"type":"text","text":"Hello, how are you?"}]',
        "create_time": "1640995200.0",
        "update_time": "1640995200.0",
        "parent_id": None,
    }


@pytest.fixture
def sample_chatgpt_export():
    """Provide sample ChatGPT export data: list of conversations (as import_conversations_data expects)."""
    return [
        {
            "id": "test-conversation-123",
            "title": "Test Conversation",
            "create_time": 1640995200.0,
            "update_time": 1640995800.0,
            "mapping": {
                "test-message-123": {
                    "id": "test-message-123",
                    "message": {
                        "id": "test-message-123",
                        "author": {"role": "user"},
                        "create_time": 1640995200.0,
                        "update_time": 1640995200.0,
                        "content": {
                            "parts": [{"type": "text", "text": "Hello, how are you?"}]
                        },
                    },
                    "parent": None,
                    "children": ["test-message-124"],
                },
                "test-message-124": {
                    "id": "test-message-124",
                    "message": {
                        "id": "test-message-124",
                        "author": {"role": "assistant"},
                        "create_time": 1640995260.0,
                        "update_time": 1640995260.0,
                        "content": {
                            "parts": [
                                {
                                    "type": "text",
                                    "text": "I'm doing well, thank you for asking!",
                                }
                            ]
                        },
                    },
                    "parent": "test-message-123",
                    "children": [],
                },
            },
        }
    ]


@pytest.fixture
def app_context():
    """Provide application context for testing."""
    with app.app_context():
        yield app


@pytest.fixture
def mock_settings():
    """Provide mock settings for testing."""
    return {
        "user_name": "Test User",
        "assistant_name": "Test Assistant",
        "dev_mode": "false",
        "dark_mode": "false",
        "verbose_mode": "false",
    }


# --- E2E: live server with test DB ---

@pytest.fixture(scope="module")
def live_server_url():
    """Start Flask app in a background thread with a temp DB and return base URL."""
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    original_get_db = app_module.get_db

    def get_test_db():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    app_module.get_db = get_test_db
    init_db()

    # Insert minimal data for E2E
    conn = get_test_db()
    conn.execute(
        "INSERT INTO conversations (id, title, create_time, update_time) VALUES (?, ?, ?, ?)",
        ("e2e-conv-1", "E2E Conversation", "1640995200.0", "1640995800.0"),
    )
    conn.execute(
        """INSERT INTO messages (id, conversation_id, role, content, create_time, update_time, parent_id)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (
            "e2e-msg-1",
            "e2e-conv-1",
            "user",
            '[{"type":"text","text":"Hello"}]',
            "1640995200.0",
            "1640995200.0",
            None,
        ),
    )
    conn.commit()
    conn.close()

    app.config["TESTING"] = False
    app.config["WTF_CSRF_ENABLED"] = False

    _e2e_port = 5764

    def run_app():
        app.run(host="127.0.0.1", port=_e2e_port, use_reloader=False, threaded=True)

    thread = threading.Thread(target=run_app)
    thread.daemon = True
    thread.start()

    # Wait for server to be reachable
    import socket
    for _ in range(30):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex(("127.0.0.1", _e2e_port)) == 0:
                    break
        except Exception:
            pass
        time.sleep(0.2)
    else:
        pytest.skip("E2E server did not start in time")

    yield f"http://127.0.0.1:{_e2e_port}"

    os.close(db_fd)
    try:
        os.unlink(db_path)
    except OSError:
        pass
    app_module.get_db = original_get_db
