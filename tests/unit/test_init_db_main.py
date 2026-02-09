# SPDX-License-Identifier: AGPL-3.0-only
# ChatGPT Browser tests - See LICENSE (AGPL-3.0).
"""Unit tests for init_db.py main()."""

import pytest


def test_init_db_main_creates_db(tmp_path, monkeypatch):
    """Running init_db.main() with a temp dir creates and inits the DB."""
    import app as app_module
    db_path = tmp_path / "chatgpt.db"
    monkeypatch.setattr(app_module, "DATABASE_PATH", str(db_path))
    db_path.unlink(missing_ok=True)
    import init_db as init_db_module
    init_db_module.main()
    assert db_path.exists()
    import sqlite3
    conn = sqlite3.connect(db_path)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    conn.close()
    assert any(t[0] == "conversations" for t in tables)


def test_init_db_main_removes_existing_db(tmp_path, monkeypatch):
    """init_db.main() removes existing chatgpt.db and recreates it."""
    import app as app_module
    db_path = tmp_path / "chatgpt.db"
    monkeypatch.setattr(app_module, "DATABASE_PATH", str(db_path))
    import init_db as init_db_module
    db_path.write_bytes(b"garbage")
    init_db_module.main()
    # Should be a valid SQLite DB, not our garbage
    import sqlite3
    conn = sqlite3.connect(db_path)
    conn.execute("SELECT 1 FROM conversations LIMIT 1")
    conn.close()
