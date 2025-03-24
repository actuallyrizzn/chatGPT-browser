import json
import sqlite3
from collections import defaultdict
from typing import Dict, List, Set, Any
import sys

def load_json_data(file_path: str) -> List[Dict]:
    """Load and parse the JSON file."""
    print(f"Loading JSON data from {file_path}...")
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Create a connection to the SQLite database."""
    print(f"Connecting to database at {db_path}...")
    return sqlite3.connect(db_path)

def get_table_counts(cursor: sqlite3.Cursor) -> Dict[str, int]:
    """Get record counts for all tables in the database."""
    tables = ['conversations', 'messages', 'message_metadata', 'message_children']
    counts = {}
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        counts[table] = cursor.fetchone()[0]
    return counts

def analyze_conversations(json_data: List[Dict], cursor: sqlite3.Cursor) -> Dict[str, Any]:
    """Analyze conversations data between JSON and DB."""
    # Get DB conversations
    cursor.execute("SELECT id, title, create_time, update_time, is_archived, is_starred, default_model_slug FROM conversations")
    db_conversations = {row[0]: row[1:] for row in cursor.fetchall()}
    
    # Get JSON conversations
    json_conversations = {conv['id']: (
        conv.get('title'),
        conv.get('create_time'),
        conv.get('update_time'),
        conv.get('is_archived'),
        conv.get('is_starred'),
        conv.get('default_model_slug')
    ) for conv in json_data}
    
    # Compare
    missing_in_db = set(json_conversations.keys()) - set(db_conversations.keys())
    missing_in_json = set(db_conversations.keys()) - set(json_conversations.keys())
    
    mismatches = []
    for conv_id in set(json_conversations.keys()) & set(db_conversations.keys()):
        if json_conversations[conv_id] != db_conversations[conv_id]:
            mismatches.append(conv_id)
    
    return {
        'total_json': len(json_conversations),
        'total_db': len(db_conversations),
        'missing_in_db': len(missing_in_db),
        'missing_in_json': len(missing_in_json),
        'mismatches': len(mismatches),
        'missing_in_db_ids': list(missing_in_db),
        'missing_in_json_ids': list(missing_in_json),
        'mismatch_ids': mismatches
    }

def analyze_messages(json_data: List[Dict], cursor: sqlite3.Cursor) -> Dict[str, Any]:
    """Analyze messages data between JSON and DB."""
    # Get DB messages
    cursor.execute("SELECT id, conversation_id, message_id, author_role, author_name, content_type, status FROM messages")
    db_messages = {row[0]: row[1:] for row in cursor.fetchall()}
    
    # Get JSON messages
    json_messages = {}
    for conv in json_data:
        for msg_id, msg_data in conv.get('mapping', {}).items():
            if 'message' in msg_data and isinstance(msg_data['message'], dict):
                msg = msg_data['message']
                json_messages[msg_id] = (
                    conv['id'],
                    msg.get('id'),
                    msg.get('author', {}).get('role'),
                    msg.get('author', {}).get('name'),
                    msg.get('content', {}).get('content_type'),
                    msg.get('status')
                )
    
    # Compare
    missing_in_db = set(json_messages.keys()) - set(db_messages.keys())
    missing_in_json = set(db_messages.keys()) - set(json_messages.keys())
    
    mismatches = []
    for msg_id in set(json_messages.keys()) & set(db_messages.keys()):
        if json_messages[msg_id] != db_messages[msg_id]:
            mismatches.append(msg_id)
    
    return {
        'total_json': len(json_messages),
        'total_db': len(db_messages),
        'missing_in_db': len(missing_in_db),
        'missing_in_json': len(missing_in_json),
        'mismatches': len(mismatches),
        'missing_in_db_ids': list(missing_in_db),
        'missing_in_json_ids': list(missing_in_json),
        'mismatch_ids': mismatches
    }

def analyze_metadata(json_data: List[Dict], cursor: sqlite3.Cursor) -> Dict[str, Any]:
    """Analyze metadata between JSON and DB."""
    # Get DB metadata
    cursor.execute("SELECT id, request_id, message_source, timestamp, message_type, model_slug FROM message_metadata")
    db_metadata = {row[0]: row[1:] for row in cursor.fetchall()}
    
    # Get JSON metadata
    json_metadata = {}
    for conv in json_data:
        for msg_id, msg_data in conv.get('mapping', {}).items():
            if 'message' in msg_data and isinstance(msg_data['message'], dict):
                metadata = msg_data['message'].get('metadata', {})
                if metadata:
                    json_metadata[msg_id] = (
                        metadata.get('request_id'),
                        metadata.get('message_source'),
                        metadata.get('timestamp'),
                        metadata.get('message_type'),
                        metadata.get('model_slug')
                    )
    
    # Compare
    missing_in_db = set(json_metadata.keys()) - set(db_metadata.keys())
    missing_in_json = set(db_metadata.keys()) - set(json_metadata.keys())
    
    mismatches = []
    for msg_id in set(json_metadata.keys()) & set(db_metadata.keys()):
        if json_metadata[msg_id] != db_metadata[msg_id]:
            mismatches.append(msg_id)
    
    return {
        'total_json': len(json_metadata),
        'total_db': len(db_metadata),
        'missing_in_db': len(missing_in_db),
        'missing_in_json': len(missing_in_json),
        'mismatches': len(mismatches),
        'missing_in_db_ids': list(missing_in_db),
        'missing_in_json_ids': list(missing_in_json),
        'mismatch_ids': mismatches
    }

def analyze_message_children(json_data: List[Dict], cursor: sqlite3.Cursor) -> Dict[str, Any]:
    """Analyze message children relationships between JSON and DB."""
    # Get DB children
    cursor.execute("SELECT parent_id, child_id FROM message_children")
    db_children = set((row[0], row[1]) for row in cursor.fetchall())
    
    # Get JSON children
    json_children = set()
    for conv in json_data:
        for msg_id, msg_data in conv.get('mapping', {}).items():
            for child_id in msg_data.get('children', []):
                json_children.add((msg_id, child_id))
    
    # Compare
    missing_in_db = json_children - db_children
    missing_in_json = db_children - json_children
    
    return {
        'total_json': len(json_children),
        'total_db': len(db_children),
        'missing_in_db': len(missing_in_db),
        'missing_in_json': len(missing_in_json),
        'missing_in_db_relationships': list(missing_in_db),
        'missing_in_json_relationships': list(missing_in_json)
    }

def main():
    # Load data
    json_data = load_json_data('conversations.json')
    conn = get_db_connection('athena.db')
    cursor = conn.cursor()
    
    # Get table counts
    table_counts = get_table_counts(cursor)
    print("\nDatabase Table Counts:")
    for table, count in table_counts.items():
        print(f"{table}: {count}")
    
    # Analyze each aspect
    print("\nAnalyzing conversations...")
    conv_analysis = analyze_conversations(json_data, cursor)
    
    print("\nAnalyzing messages...")
    msg_analysis = analyze_messages(json_data, cursor)
    
    print("\nAnalyzing metadata...")
    metadata_analysis = analyze_metadata(json_data, cursor)
    
    print("\nAnalyzing message children...")
    children_analysis = analyze_message_children(json_data, cursor)
    
    # Generate report
    print("\n=== Analysis Report ===")
    print("\nConversations:")
    print(f"Total in JSON: {conv_analysis['total_json']}")
    print(f"Total in DB: {conv_analysis['total_db']}")
    print(f"Missing in DB: {conv_analysis['missing_in_db']}")
    print(f"Missing in JSON: {conv_analysis['missing_in_json']}")
    print(f"Mismatches: {conv_analysis['mismatches']}")
    
    print("\nMessages:")
    print(f"Total in JSON: {msg_analysis['total_json']}")
    print(f"Total in DB: {msg_analysis['total_db']}")
    print(f"Missing in DB: {msg_analysis['missing_in_db']}")
    print(f"Missing in JSON: {msg_analysis['missing_in_json']}")
    print(f"Mismatches: {msg_analysis['mismatches']}")
    
    print("\nMetadata:")
    print(f"Total in JSON: {metadata_analysis['total_json']}")
    print(f"Total in DB: {metadata_analysis['total_db']}")
    print(f"Missing in DB: {metadata_analysis['missing_in_db']}")
    print(f"Missing in JSON: {metadata_analysis['missing_in_json']}")
    print(f"Mismatches: {metadata_analysis['mismatches']}")
    
    print("\nMessage Children:")
    print(f"Total in JSON: {children_analysis['total_json']}")
    print(f"Total in DB: {children_analysis['total_db']}")
    print(f"Missing in DB: {children_analysis['missing_in_db']}")
    print(f"Missing in JSON: {children_analysis['missing_in_json']}")
    
    # Save detailed report to file
    with open('data_analysis_report.txt', 'w') as f:
        f.write("=== Detailed Data Analysis Report ===\n\n")
        
        f.write("Database Table Counts:\n")
        for table, count in table_counts.items():
            f.write(f"{table}: {count}\n")
        
        f.write("\nConversations Analysis:\n")
        f.write(f"Total in JSON: {conv_analysis['total_json']}\n")
        f.write(f"Total in DB: {conv_analysis['total_db']}\n")
        f.write(f"Missing in DB: {conv_analysis['missing_in_db']}\n")
        f.write(f"Missing in JSON: {conv_analysis['missing_in_json']}\n")
        f.write(f"Mismatches: {conv_analysis['mismatches']}\n")
        if conv_analysis['missing_in_db_ids']:
            f.write("\nMissing in DB IDs:\n")
            for id in conv_analysis['missing_in_db_ids']:
                f.write(f"{id}\n")
        
        f.write("\nMessages Analysis:\n")
        f.write(f"Total in JSON: {msg_analysis['total_json']}\n")
        f.write(f"Total in DB: {msg_analysis['total_db']}\n")
        f.write(f"Missing in DB: {msg_analysis['missing_in_db']}\n")
        f.write(f"Missing in JSON: {msg_analysis['missing_in_json']}\n")
        f.write(f"Mismatches: {msg_analysis['mismatches']}\n")
        if msg_analysis['missing_in_db_ids']:
            f.write("\nMissing in DB IDs:\n")
            for id in msg_analysis['missing_in_db_ids']:
                f.write(f"{id}\n")
        
        f.write("\nMetadata Analysis:\n")
        f.write(f"Total in JSON: {metadata_analysis['total_json']}\n")
        f.write(f"Total in DB: {metadata_analysis['total_db']}\n")
        f.write(f"Missing in DB: {metadata_analysis['missing_in_db']}\n")
        f.write(f"Missing in JSON: {metadata_analysis['missing_in_json']}\n")
        f.write(f"Mismatches: {metadata_analysis['mismatches']}\n")
        if metadata_analysis['missing_in_db_ids']:
            f.write("\nMissing in DB IDs:\n")
            for id in metadata_analysis['missing_in_db_ids']:
                f.write(f"{id}\n")
        
        f.write("\nMessage Children Analysis:\n")
        f.write(f"Total in JSON: {children_analysis['total_json']}\n")
        f.write(f"Total in DB: {children_analysis['total_db']}\n")
        f.write(f"Missing in DB: {children_analysis['missing_in_db']}\n")
        f.write(f"Missing in JSON: {children_analysis['missing_in_json']}\n")
        if children_analysis['missing_in_db_relationships']:
            f.write("\nMissing in DB Relationships:\n")
            for parent, child in children_analysis['missing_in_db_relationships']:
                f.write(f"{parent} -> {child}\n")
    
    print("\nDetailed report has been saved to 'data_analysis_report.txt'")
    conn.close()

if __name__ == "__main__":
    main() 