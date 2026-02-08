"""Unit tests for run_ingest.py CLI."""

import json
import sys

import pytest


def test_run_ingest_file_not_found(capsys, monkeypatch):
    """run_ingest exits with error when file does not exist."""
    import run_ingest as run_ingest_module
    monkeypatch.setattr(sys, "argv", ["run_ingest.py", "nonexistent-file.json"])
    with pytest.raises(SystemExit) as exc_info:
        run_ingest_module.main()
    assert exc_info.value.code != 0
    out, err = capsys.readouterr()
    assert "not found" in err or "Error" in err


def test_run_ingest_success(tmp_path, monkeypatch, sample_chatgpt_export):
    """run_ingest loads a JSON file and imports via app.import_conversations_data."""
    import app as app_module
    import run_ingest as run_ingest_module

    json_path = tmp_path / "conversations.json"
    json_path.write_text(json.dumps(sample_chatgpt_export), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["run_ingest.py", str(json_path)])
    db_path = tmp_path / "chatgpt.db"
    original_get_db = app_module.get_db

    def get_test_db():
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    app_module.get_db = get_test_db
    app_module.init_db()

    try:
        run_ingest_module.main()
        conn = app_module.get_db()
        row = conn.execute(
            "SELECT id FROM conversations WHERE id = ?",
            ("test-conversation-123",),
        ).fetchone()
        conn.close()
        assert row is not None
    finally:
        app_module.get_db = original_get_db


def test_run_ingest_init_db_flag(tmp_path, monkeypatch, sample_chatgpt_export):
    """run_ingest --init-db initializes DB before ingest."""
    import app as app_module
    import run_ingest as run_ingest_module

    json_path = tmp_path / "conversations.json"
    json_path.write_text(json.dumps(sample_chatgpt_export), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(sys, "argv", ["run_ingest.py", "--init-db", str(json_path)])
    db_path = tmp_path / "chatgpt.db"
    original_get_db = app_module.get_db

    def get_test_db():
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn

    app_module.get_db = get_test_db

    try:
        run_ingest_module.main()
        conn = app_module.get_db()
        row = conn.execute(
            "SELECT id FROM conversations WHERE id = ?",
            ("test-conversation-123",),
        ).fetchone()
        conn.close()
        assert row is not None
    finally:
        app_module.get_db = original_get_db
