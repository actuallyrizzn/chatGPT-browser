# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser tests - See LICENSE (AGPL-3.0).
"""Integration tests for Flask routes with test database."""

import io
import json
from unittest.mock import patch

import pytest

import app as app_module


@pytest.fixture
def seeded_db(client_with_db, sample_chatgpt_export):
    """Client with test DB and one conversation imported."""
    app_module.import_conversations_data(sample_chatgpt_export)
    return client_with_db


class TestIndexRoute:
    def test_index_returns_200(self, client_with_db):
        r = client_with_db.get("/")
        assert r.status_code == 200
        assert b"ChatGPT Browser" in r.data or b"chatgpt" in r.data.lower()

    def test_index_lists_conversations_after_import(self, seeded_db):
        r = seeded_db.get("/")
        assert r.status_code == 200
        assert b"Test Conversation" in r.data or b"test-conversation" in r.data


class TestConversationRoutes:
    def test_conversation_404_when_not_found(self, client_with_db):
        # When dev_mode is false, /conversation/id redirects to /nice; nice returns 404
        r = client_with_db.get("/conversation/nonexistent-id", follow_redirects=True)
        assert r.status_code == 404
        assert b"not found" in r.data.lower()

    def test_conversation_nice_404_when_not_found(self, client_with_db):
        r = client_with_db.get("/conversation/nonexistent-id/nice")
        assert r.status_code == 404

    def test_conversation_nice_200_with_data(self, seeded_db):
        r = seeded_db.get("/conversation/test-conversation-123/nice")
        assert r.status_code == 200
        assert b"Hello" in r.data or b"how are you" in r.data.lower()

    def test_full_conversation_redirects_and_sets_session(self, seeded_db):
        # Dev mode is false by default, so /conversation/id redirects to /nice.
        # /conversation/id/full sets override and redirects to /conversation/id
        r = seeded_db.get("/conversation/test-conversation-123/full", follow_redirects=True)
        assert r.status_code == 200
        # After redirect we get the dev conversation view
        assert b"conversation" in r.data.lower() or b"message" in r.data.lower()

    def test_conversation_dev_view_when_dev_mode_on(self, seeded_db):
        app_module.set_setting("dev_mode", "true")
        try:
            r = seeded_db.get("/conversation/test-conversation-123")
            assert r.status_code == 200
        finally:
            app_module.set_setting("dev_mode", "false")

    def test_conversation_dev_view_with_message_metadata(self, client_with_db):
        """Dev view renders messages with metadata (covers metadata dict branch)."""
        app_module.import_conversations_data(
            [
                {
                    "id": "conv-meta",
                    "title": "Meta",
                    "create_time": 1640995200.0,
                    "update_time": 1640995800.0,
                    "mapping": {
                        "m1": {
                            "message": {
                                "id": "m1",
                                "author": {"role": "user"},
                                "create_time": 1640995200.0,
                                "update_time": 1640995200.0,
                                "content": {"parts": [{"type": "text", "text": "Hi"}]},
                                "metadata": {
                                    "message_type": "message",
                                    "model_slug": "gpt-4",
                                },
                            },
                            "parent": None,
                            "children": [],
                        }
                    },
                }
            ]
        )
        app_module.set_setting("dev_mode", "true")
        try:
            r = client_with_db.get("/conversation/conv-meta")
            assert r.status_code == 200
            assert b"Hi" in r.data or b"meta" in r.data.lower()
        finally:
            app_module.set_setting("dev_mode", "false")

    def test_conversation_dev_view_404_when_not_found(self, client_with_db):
        """Dev view returns 404 directly when conversation does not exist (line 191)."""
        app_module.set_setting("dev_mode", "true")
        try:
            r = client_with_db.get("/conversation/nonexistent-id", follow_redirects=False)
            assert r.status_code == 404
            assert b"not found" in r.data.lower()
        finally:
            app_module.set_setting("dev_mode", "false")

    def test_conversation_nice_404_no_canonical_endpoint(self, client_with_db):
        """Nice view returns 404 when conversation has no messages (line 259)."""
        conn = app_module.get_db()
        conn.execute(
            "INSERT INTO conversations (id, title, create_time, update_time) VALUES (?, ?, ?, ?)",
            ("empty-conv", "Empty", "1640995200.0", "1640995800.0"),
        )
        conn.commit()
        conn.close()
        r = client_with_db.get("/conversation/empty-conv/nice")
        assert r.status_code == 404
        assert b"canonical" in r.data.lower() or b"endpoint" in r.data.lower()

    def test_nice_conversation_with_message_metadata(self, client_with_db):
        """Nice view builds path with message metadata (covers metadata branch in path loop)."""
        app_module.import_conversations_data(
            [
                {
                    "id": "nice-meta",
                    "title": "Nice Meta",
                    "create_time": 1640995200.0,
                    "update_time": 1640995800.0,
                    "mapping": {
                        "m1": {
                            "message": {
                                "id": "m1",
                                "author": {"role": "user"},
                                "create_time": 1640995200.0,
                                "update_time": 1640995200.0,
                                "content": {"parts": [{"type": "text", "text": "Hello"}]},
                                "metadata": {
                                    "message_type": "message",
                                    "model_slug": "gpt-4",
                                },
                            },
                            "parent": None,
                            "children": [],
                        }
                    },
                }
            ]
        )
        r = client_with_db.get("/conversation/nice-meta/nice")
        assert r.status_code == 200
        assert b"Hello" in r.data or b"nice" in r.data.lower()


class TestSettingsRoutes:
    def test_settings_page_200(self, client_with_db):
        r = client_with_db.get("/settings")
        assert r.status_code == 200
        assert b"Settings" in r.data or b"settings" in r.data

    def test_update_names_redirects_to_index(self, client_with_db):
        r = client_with_db.post(
            "/update_names",
            data={"user_name": "Alice", "assistant_name": "Bob"},
            follow_redirects=False,
        )
        assert r.status_code in (302, 303)
        assert r.location.endswith("/") or "/" in r.location
        assert app_module.get_setting("user_name") == "Alice"
        assert app_module.get_setting("assistant_name") == "Bob"


class TestToggleRoutes:
    def test_toggle_view_mode_returns_json(self, client_with_db):
        r = client_with_db.post("/toggle_view_mode")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert "dev_mode" in data

    def test_toggle_view_mode_get_405(self, client_with_db):
        r = client_with_db.get("/toggle_view_mode")
        assert r.status_code == 405

    def test_toggle_dark_mode_redirects(self, client_with_db):
        r = client_with_db.post("/toggle_dark_mode", follow_redirects=False)
        assert r.status_code in (302, 303)

    def test_toggle_dark_mode_get_405(self, client_with_db):
        r = client_with_db.get("/toggle_dark_mode")
        assert r.status_code == 405

    def test_toggle_dark_mode_redirects_to_referrer(self, client_with_db):
        r = client_with_db.post(
            "/toggle_dark_mode",
            headers={"Referer": "http://localhost/settings"},
            follow_redirects=False,
        )
        assert r.status_code in (302, 303)
        assert r.location == "http://localhost/settings" or "settings" in r.location

    def test_toggle_verbose_mode_permanent(self, client_with_db):
        r = client_with_db.post("/toggle_verbose_mode")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True
        assert "verbose_mode" in data

    def test_toggle_verbose_mode_temp(self, client_with_db):
        r = client_with_db.post("/toggle_verbose_mode?temp=true")
        assert r.status_code == 200
        data = r.get_json()
        assert data["success"] is True

    def test_toggle_verbose_mode_get_405(self, client_with_db):
        r = client_with_db.get("/toggle_verbose_mode")
        assert r.status_code == 405


class TestImportRoute:
    def test_import_no_file_400(self, client_with_db):
        r = client_with_db.post("/import", data={})
        assert r.status_code == 400
        assert b"file" in r.data.lower() or b"upload" in r.data.lower()

    def test_import_empty_filename_400(self, client_with_db):
        r = client_with_db.post("/import", data={"file": (io.BytesIO(b""), "")})
        assert r.status_code == 400

    def test_import_empty_file_content_400(self, client_with_db):
        r = client_with_db.post(
            "/import",
            data={"file": (io.BytesIO(b""), "data.json")},
        )
        assert r.status_code == 400
        assert b"empty" in r.data.lower()

    def test_import_invalid_json_400(self, client_with_db):
        r = client_with_db.post(
            "/import",
            data={"file": (io.BytesIO(b"not json"), "data.json")},
        )
        assert r.status_code == 400

    def test_import_success_redirects_to_index(self, client_with_db, sample_chatgpt_export):
        payload = json.dumps(sample_chatgpt_export).encode("utf-8")
        r = client_with_db.post(
            "/import",
            data={"file": (io.BytesIO(payload), "conversations.json")},
            follow_redirects=False,
        )
        assert r.status_code in (302, 303)
        assert "/" in r.location
        # Check DB
        conn = app_module.get_db()
        row = conn.execute(
            "SELECT id FROM conversations WHERE id = ?",
            ("test-conversation-123",),
        ).fetchone()
        conn.close()
        assert row is not None

    def test_import_generic_exception_400(self, client_with_db, sample_chatgpt_export):
        """Import returns 400 when import_conversations_data raises (covers except Exception)."""
        with patch.object(
            app_module, "import_conversations_data", side_effect=RuntimeError("db error")
        ):
            payload = json.dumps(sample_chatgpt_export).encode("utf-8")
            r = client_with_db.post(
                "/import",
                data={"file": (io.BytesIO(payload), "conversations.json")},
            )
        assert r.status_code == 400
        assert b"error" in r.data.lower()
