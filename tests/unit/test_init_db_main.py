"""Unit tests for init_db.py main()."""

import pytest


def test_init_db_main_creates_db(tmp_path, monkeypatch):
    """Running init_db.main() with a temp dir creates and inits the DB."""
    import init_db as init_db_module
    monkeypatch.chdir(tmp_path)
    # Ensure no existing chatgpt.db
    (tmp_path / "chatgpt.db").unlink(missing_ok=True)
    init_db_module.main()
    assert (tmp_path / "chatgpt.db").exists()
    import sqlite3
    conn = sqlite3.connect(tmp_path / "chatgpt.db")
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    conn.close()
    assert any(t[0] == "conversations" for t in tables)


def test_init_db_main_removes_existing_db(tmp_path, monkeypatch):
    """init_db.main() removes existing chatgpt.db and recreates it."""
    import init_db as init_db_module
    monkeypatch.chdir(tmp_path)
    (tmp_path / "chatgpt.db").write_bytes(b"garbage")
    init_db_module.main()
    # Should be a valid SQLite DB, not our garbage
    import sqlite3
    conn = sqlite3.connect(tmp_path / "chatgpt.db")
    conn.execute("SELECT 1 FROM conversations LIMIT 1")
    conn.close()
