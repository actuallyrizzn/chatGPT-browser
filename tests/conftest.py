"""
Pytest configuration and fixtures for ChatGPT Browser tests.
"""

import pytest
import tempfile
import os
import sqlite3
from app import app, init_db, get_db


@pytest.fixture
def client():
    """Create a test client for the application."""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_db():
    """Create a temporary test database."""
    # Create a temporary database file
    db_fd, db_path = tempfile.mkstemp()
    
    # Override the database path for testing
    original_get_db = app.get_db
    
    def get_test_db():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    app.get_db = get_test_db
    
    # Initialize the test database
    init_db()
    
    yield db_path
    
    # Cleanup
    os.close(db_fd)
    os.unlink(db_path)
    app.get_db = original_get_db


@pytest.fixture
def sample_conversation():
    """Provide sample conversation data for testing."""
    return {
        'id': 'test-conversation-123',
        'title': 'Test Conversation',
        'create_time': '1640995200.0',
        'update_time': '1640995800.0'
    }


@pytest.fixture
def sample_message():
    """Provide sample message data for testing."""
    return {
        'id': 'test-message-123',
        'conversation_id': 'test-conversation-123',
        'role': 'user',
        'content': '[{"type":"text","text":"Hello, how are you?"}]',
        'create_time': '1640995200.0',
        'update_time': '1640995200.0',
        'parent_id': None
    }


@pytest.fixture
def sample_chatgpt_export():
    """Provide sample ChatGPT export data for testing."""
    return {
        "conversations": [
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
                            "author": {
                                "role": "user"
                            },
                            "create_time": 1640995200.0,
                            "update_time": 1640995200.0,
                            "content": {
                                "parts": [
                                    {
                                        "type": "text",
                                        "text": "Hello, how are you?"
                                    }
                                ]
                            }
                        },
                        "parent": None,
                        "children": ["test-message-124"]
                    },
                    "test-message-124": {
                        "id": "test-message-124",
                        "message": {
                            "id": "test-message-124",
                            "author": {
                                "role": "assistant"
                            },
                            "create_time": 1640995260.0,
                            "update_time": 1640995260.0,
                            "content": {
                                "parts": [
                                    {
                                        "type": "text",
                                        "text": "I'm doing well, thank you for asking!"
                                    }
                                ]
                            }
                        },
                        "parent": "test-message-123",
                        "children": []
                    }
                }
            }
        ]
    }


@pytest.fixture
def app_context():
    """Provide application context for testing."""
    with app.app_context():
        yield app


@pytest.fixture
def mock_settings():
    """Provide mock settings for testing."""
    return {
        'user_name': 'Test User',
        'assistant_name': 'Test Assistant',
        'dev_mode': 'false',
        'dark_mode': 'false',
        'verbose_mode': 'false'
    } 