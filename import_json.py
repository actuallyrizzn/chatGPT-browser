import json
import sqlite3
from datetime import datetime
import os

def init_db():
    """Initialize the database with the schema"""
    conn = sqlite3.connect('chatgpt.db')
    with open('schema.sql', 'r') as f:
        conn.executescript(f.read())
    return conn

def insert_conversation(conn, conversation):
    """Insert a conversation and return its ID"""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO conversations (title, update_time, voice, plugin_ids, safe_urls, moderation_results)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        conversation.get('title'),
        conversation.get('update_time'),
        conversation.get('voice'),
        json.dumps(conversation.get('plugin_ids', [])),
        json.dumps(conversation.get('safe_urls', [])),
        json.dumps(conversation.get('moderation_results', []))
    ))
    return cursor.lastrowid

def insert_message(conn, message, conversation_id):
    """Insert a message and its metadata"""
    cursor = conn.cursor()
    
    # Insert main message data
    cursor.execute('''
        INSERT INTO messages (
            id, conversation_id, author_name, author_role, author_metadata,
            content_type, content_parts, create_time, update_time,
            status, channel, weight, end_turn, parent_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        message.get('id'),
        conversation_id,
        message.get('author', {}).get('name'),
        message.get('author', {}).get('role'),
        json.dumps(message.get('author', {}).get('metadata', {})),
        message.get('content', {}).get('content_type'),
        json.dumps(message.get('content', {}).get('parts', [])),
        message.get('create_time'),
        message.get('update_time'),
        message.get('status'),
        message.get('channel'),
        message.get('weight'),
        message.get('end_turn'),
        message.get('parent')
    ))
    
    # Insert message metadata
    metadata = message.get('metadata', {})
    cursor.execute('''
        INSERT INTO message_metadata (
            message_id, citations, content_references, default_model_slug,
            finish_details, is_complete, message_type, model_slug,
            parent_id, request_id, timestamp_, message_source,
            serialization_metadata
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        message.get('id'),
        json.dumps(metadata.get('citations', [])),
        json.dumps(metadata.get('content_references', [])),
        metadata.get('default_model_slug'),
        json.dumps(metadata.get('finish_details', {})),
        metadata.get('is_complete'),
        metadata.get('message_type'),
        metadata.get('model_slug'),
        metadata.get('parent_id'),
        metadata.get('request_id'),
        metadata.get('timestamp_'),
        metadata.get('message_source'),
        json.dumps(metadata.get('serialization_metadata', {}))
    ))

def insert_message_children(conn, message):
    """Insert message children relationships"""
    cursor = conn.cursor()
    children = message.get('children', [])
    for child_id in children:
        cursor.execute('''
            INSERT INTO message_children (parent_id, child_id)
            VALUES (?, ?)
        ''', (message.get('id'), child_id))

def import_json_to_db(json_file_path):
    """Import JSON data into the database"""
    conn = init_db()
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for conversation in data:
            # Insert conversation and get its ID
            conversation_id = insert_conversation(conn, conversation)
            
            # Process messages in the mapping
            mapping = conversation.get('mapping', {})
            for message_id, message_data in mapping.items():
                if isinstance(message_data, dict):
                    message = message_data.get('message', {})
                    if message:
                        message['id'] = message_id
                        insert_message(conn, message, conversation_id)
                        insert_message_children(conn, message_data)
        
        conn.commit()
        print("Data import completed successfully!")
        
    except Exception as e:
        print(f"Error during import: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    json_file_path = "conversations.json"
    if not os.path.exists(json_file_path):
        print(f"Error: {json_file_path} not found!")
    else:
        import_json_to_db(json_file_path) 