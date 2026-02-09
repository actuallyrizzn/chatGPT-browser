# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser tests - See LICENSE (AGPL-3.0).
"""Unit tests for import_conversations_data and init_db."""

import pytest

import app as app_module

# Batch size used in app.import_conversations_data for commit frequency
IMPORT_BATCH_SIZE = getattr(app_module, "IMPORT_BATCH_SIZE", 50)


class TestImportConversationsData:
    """Tests for import_conversations_data with test_db."""

    def test_import_single_conversation_list(self, client_with_db, sample_chatgpt_export):
        app_module.import_conversations_data(sample_chatgpt_export)
        conn = app_module.get_db()
        row = conn.execute(
            "SELECT id, title FROM conversations WHERE id = ?",
            ("test-conversation-123",),
        ).fetchone()
        conn.close()
        assert row is not None
        assert row["title"] == "Test Conversation"

    def test_import_single_dict_wrapped_in_list(self, client_with_db, sample_chatgpt_export):
        # import_conversations_data does: if not isinstance(data, list): data = [data]
        single = sample_chatgpt_export[0]
        app_module.import_conversations_data(single)
        conn = app_module.get_db()
        row = conn.execute(
            "SELECT id FROM conversations WHERE id = ?",
            ("test-conversation-123",),
        ).fetchone()
        conn.close()
        assert row is not None

    def test_import_skips_missing_id(self, client_with_db):
        data = [{"title": "No ID", "mapping": {}}]  # no 'id'
        app_module.import_conversations_data(data)
        conn = app_module.get_db()
        count = conn.execute("SELECT COUNT(*) as c FROM conversations").fetchone()["c"]
        conn.close()
        assert count == 0

    def test_import_skips_empty_message_in_mapping(self, client_with_db):
        """Mapping entry with empty or missing message is skipped (covers continue branch)."""
        data = [
            {
                "id": "conv-empty-msg",
                "title": "With empty message",
                "create_time": 1640995200.0,
                "update_time": 1640995800.0,
                "mapping": {
                    "msg-1": {"message": {}, "parent": None, "children": []},
                    "msg-2": {
                        "message": {
                            "id": "msg-2",
                            "author": {"role": "user"},
                            "create_time": 1640995200.0,
                            "update_time": 1640995200.0,
                            "content": {"parts": [{"type": "text", "text": "Hi"}]},
                        },
                        "parent": None,
                        "children": [],
                    },
                },
            }
        ]
        app_module.import_conversations_data(data)
        conn = app_module.get_db()
        messages = conn.execute(
            "SELECT id FROM messages WHERE conversation_id = ?", ("conv-empty-msg",)
        ).fetchall()
        conn.close()
        assert len(messages) == 1
        assert messages[0]["id"] == "msg-2"

    def test_import_inserts_messages_and_children(self, client_with_db, sample_chatgpt_export):
        app_module.import_conversations_data(sample_chatgpt_export)
        conn = app_module.get_db()
        messages = conn.execute(
            "SELECT id, role, content FROM messages WHERE conversation_id = ?",
            ("test-conversation-123",),
        ).fetchall()
        conn.close()
        assert len(messages) >= 2
        roles = {m["role"] for m in messages}
        assert "user" in roles and "assistant" in roles

    def test_import_with_metadata(self, client_with_db):
        data = [
            {
                "id": "conv-meta",
                "title": "With metadata",
                "create_time": 1640995200.0,
                "update_time": 1640995800.0,
                "mapping": {
                    "msg-1": {
                        "message": {
                            "id": "msg-1",
                            "author": {"role": "user"},
                            "create_time": 1640995200.0,
                            "update_time": 1640995200.0,
                            "content": {"parts": [{"type": "text", "text": "Hi"}]},
                            "metadata": {
                                "message_type": "message",
                                "model_slug": "gpt-4",
                                "is_complete": True,
                            },
                        },
                        "parent": None,
                        "children": [],
                    }
                },
            }
        ]
        app_module.import_conversations_data(data)
        conn = app_module.get_db()
        meta = conn.execute(
            "SELECT message_type, model_slug, is_complete FROM message_metadata WHERE message_id = ?",
            ("msg-1",),
        ).fetchone()
        conn.close()
        assert meta is not None
        assert meta["model_slug"] == "gpt-4"
        assert meta["is_complete"] == 1

    def test_import_commits_in_batches(self, client_with_db):
        """Import commits every IMPORT_BATCH_SIZE and at end so partial progress is persisted (fixes #18)."""
        from unittest.mock import patch

        n = IMPORT_BATCH_SIZE + 5
        data = [
            {
                "id": f"conv-batch-{i}",
                "title": f"Conv {i}",
                "create_time": 1640995200.0,
                "update_time": 1640995200.0,
                "mapping": {},
            }
            for i in range(n)
        ]
        commit_count = [0]

        with app_module.app.app_context():
            conn = app_module.get_db()
            # Wrap connection so commit is counted (sqlite3.Connection.commit is read-only)
            class CommitCountingConn:
                def __getattr__(self, name):
                    return getattr(conn, name)
                def commit(self):
                    commit_count[0] += 1
                    conn.commit()
            wrapper = CommitCountingConn()
            with patch.object(app_module, "get_db", return_value=wrapper):
                app_module.import_conversations_data(data)

        assert commit_count[0] >= 2, "Expected at least batch commit and final commit"
        conn = app_module.get_db()
        count = conn.execute("SELECT COUNT(*) as c FROM conversations").fetchone()["c"]
        conn.close()
        assert count == n


class TestInitDb:
    """Tests for init_db schema and defaults."""

    def test_init_db_creates_tables(self, test_db):
        conn = app_module.get_db()
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        ).fetchall()
        conn.close()
        names = [t["name"] for t in tables]
        assert "conversations" in names
        assert "messages" in names
        assert "message_metadata" in names
        assert "message_children" in names
        assert "settings" in names

    def test_init_db_inserts_default_settings(self, test_db):
        conn = app_module.get_db()
        settings = conn.execute("SELECT key, value FROM settings").fetchall()
        conn.close()
        keys = {s["key"] for s in settings}
        assert "user_name" in keys
        assert "assistant_name" in keys
        assert "dev_mode" in keys
        assert "dark_mode" in keys
        assert "verbose_mode" in keys
