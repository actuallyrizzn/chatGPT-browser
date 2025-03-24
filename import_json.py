import json
import sqlite3
import os
from typing import Dict, Any
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('import.log'),
        logging.StreamHandler()
    ]
)

def load_json_data(file_path: str) -> list:
    """Load and parse the JSON file."""
    logging.info(f"Loading JSON data from {file_path}...")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logging.info(f"Successfully loaded {len(data)} conversations from JSON")
        return data
    except Exception as e:
        logging.error(f"Error loading JSON file: {e}")
        raise

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    logging.info(f"Connecting to database at {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logging.error(f"Error connecting to database: {e}")
        raise

def create_tables(cursor: sqlite3.Cursor):
    """Create the database tables if they don't exist."""
    logging.info("Creating database tables...")
    
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

def insert_conversation(cursor: sqlite3.Cursor, convo: Dict[str, Any]) -> bool:
    """Insert or update a conversation in the database."""
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO conversations 
            (id, title, create_time, update_time, conversation_id, is_archived, is_starred, default_model_slug)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            convo.get("id"),
            convo.get("title"),
            convo.get("create_time"),
            convo.get("update_time"),
            convo.get("id"),
            convo.get("is_archived"),
            convo.get("is_starred"),
            convo.get("default_model_slug"),
        ))
        return True
    except Exception as e:
        logging.error(f"Error inserting conversation {convo.get('id')}: {e}")
        return False

def insert_message(cursor: sqlite3.Cursor, msg_id: str, convo_id: str, message: Dict[str, Any]) -> bool:
    """Insert or update a message in the database."""
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO messages 
            (id, conversation_id, message_id, author_role, author_name, content_type, content, status, 
            end_turn, weight, recipient, channel, create_time, update_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            msg_id,
            convo_id,
            message.get("id", f"msg_{msg_id}"),
            message.get("author", {}).get("role", "unknown"),
            message.get("author", {}).get("name", "anonymous"),
            message.get("content", {}).get("content_type", "text"),
            " ".join(
                part if isinstance(part, str) else json.dumps(part) 
                for part in message.get("content", {}).get("parts", [])
            ),
            message.get("status", "unknown"),
            message.get("end_turn"),
            message.get("weight", 0.0),
            message.get("recipient", "unknown"),
            message.get("channel"),
            message.get("create_time", 0),
            message.get("update_time", 0),
        ))
        return True
    except Exception as e:
        logging.error(f"Error inserting message {msg_id} in conversation {convo_id}: {e}")
        return False

def insert_metadata(cursor: sqlite3.Cursor, msg_id: str, metadata: Dict[str, Any]) -> bool:
    """Insert or update message metadata in the database."""
    if not metadata:
        return True
        
    try:
        cursor.execute("""
            INSERT OR REPLACE INTO message_metadata 
            (id, request_id, message_source, timestamp, message_type, model_slug, parent_id, 
            finish_details, citations, content_references)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            msg_id,
            metadata.get("request_id"),
            metadata.get("message_source"),
            metadata.get("timestamp"),
            metadata.get("message_type"),
            metadata.get("model_slug"),
            metadata.get("parent_id"),
            json.dumps(metadata.get("finish_details", {})),
            json.dumps(metadata.get("citations", [])),
            json.dumps(metadata.get("content_references", [])),
        ))
        return True
    except Exception as e:
        logging.error(f"Error inserting metadata for message {msg_id}: {e}")
        return False

def insert_children(cursor: sqlite3.Cursor, parent_id: str, children: list) -> bool:
    """Insert message children relationships in the database."""
    if not children:
        return True
        
    try:
        for child_id in children:
            cursor.execute("""
                INSERT OR REPLACE INTO message_children 
                (parent_id, child_id) VALUES (?, ?)
            """, (parent_id, child_id))
        return True
    except Exception as e:
        logging.error(f"Error inserting children for message {parent_id}: {e}")
        return False

def process_conversation(cursor: sqlite3.Cursor, convo: Dict[str, Any]) -> Dict[str, int]:
    """Process a single conversation and its messages."""
    stats = {
        'messages_processed': 0,
        'messages_failed': 0,
        'metadata_processed': 0,
        'metadata_failed': 0,
        'children_processed': 0,
        'children_failed': 0,
        'conversations_processed': 0,
        'conversations_failed': 0
    }
    
    try:
        # Insert conversation
        if not insert_conversation(cursor, convo):
            logging.error(f"Failed to process conversation {convo.get('id')}")
            stats['conversations_failed'] += 1
            return stats
        
        stats['conversations_processed'] += 1
        
        # Process messages
        for msg_id, msg_data in convo.get("mapping", {}).items():
            message_data = msg_data.get("message")
            
            if isinstance(message_data, dict):
                if insert_message(cursor, msg_id, convo.get("id"), message_data):
                    stats['messages_processed'] += 1
                else:
                    stats['messages_failed'] += 1
                    
                metadata = message_data.get("metadata", {})
                if insert_metadata(cursor, msg_id, metadata):
                    stats['metadata_processed'] += 1
                else:
                    stats['metadata_failed'] += 1
            
            children = msg_data.get("children", [])
            if insert_children(cursor, msg_id, children):
                stats['children_processed'] += 1
            else:
                stats['children_failed'] += 1
        
        return stats
    except Exception as e:
        logging.error(f"Error processing conversation {convo.get('id')}: {str(e)}")
        stats['conversations_failed'] += 1
        return stats

def main():
    start_time = datetime.now()
    logging.info("Starting import process...")
    
    try:
        # Load JSON data
        json_data = load_json_data('conversations.json')
        
        # Connect to database
        conn = get_db_connection('athena.db')
        cursor = conn.cursor()
        
        # Create tables
        create_tables(cursor)
        
        # Process conversations
        total_stats = {
            'conversations_processed': 0,
            'conversations_failed': 0,
            'messages_processed': 0,
            'messages_failed': 0,
            'metadata_processed': 0,
            'metadata_failed': 0,
            'children_processed': 0,
            'children_failed': 0
        }
        
        for i, convo in enumerate(json_data, 1):
            logging.info(f"Processing conversation {i}/{len(json_data)} (ID: {convo.get('id')})")
            stats = process_conversation(cursor, convo)
            
            # Update total stats
            for key in total_stats:
                total_stats[key] += stats.get(key, 0)
            
            # Commit after each conversation
            conn.commit()
        
        # Log final statistics
        end_time = datetime.now()
        duration = end_time - start_time
        
        logging.info("\n=== Import Statistics ===")
        logging.info(f"Duration: {duration}")
        logging.info(f"Total conversations processed: {total_stats['conversations_processed']}")
        logging.info(f"Total conversations failed: {total_stats['conversations_failed']}")
        logging.info(f"Total messages processed: {total_stats['messages_processed']}")
        logging.info(f"Total messages failed: {total_stats['messages_failed']}")
        logging.info(f"Total metadata processed: {total_stats['metadata_processed']}")
        logging.info(f"Total metadata failed: {total_stats['metadata_failed']}")
        logging.info(f"Total children processed: {total_stats['children_processed']}")
        logging.info(f"Total children failed: {total_stats['children_failed']}")
        
        logging.info("\nImport completed successfully!")
        
    except Exception as e:
        logging.error(f"Fatal error during import: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
