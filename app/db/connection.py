import sqlite3
from flask import g
from typing import Optional

DATABASE = "athena.db"

def get_db() -> sqlite3.Connection:
    """Get database connection, creating it if necessary."""
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e: Optional[BaseException] = None) -> None:
    """Close database connection if it exists."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db(app) -> None:
    """Initialize database tables."""
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT,
                create_time INTEGER,
                update_time INTEGER,
                conversation_id TEXT,
                is_archived BOOLEAN,
                is_starred BOOLEAN,
                default_model_slug TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id TEXT PRIMARY KEY,
                conversation_id TEXT,
                message_id TEXT,
                author_role TEXT,
                author_name TEXT,
                content_type TEXT,
                content TEXT,
                status TEXT,
                end_turn BOOLEAN,
                weight REAL,
                recipient TEXT,
                channel TEXT,
                create_time INTEGER,
                update_time INTEGER,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_metadata (
                id TEXT PRIMARY KEY,
                request_id TEXT,
                message_source TEXT,
                timestamp INTEGER,
                message_type TEXT,
                model_slug TEXT,
                parent_id TEXT,
                finish_details TEXT,
                citations TEXT,
                content_references TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_children (
                parent_id TEXT,
                child_id TEXT,
                PRIMARY KEY (parent_id, child_id)
            )
        """)

        db.commit() 