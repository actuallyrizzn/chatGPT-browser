import sqlite3
from datetime import datetime
import json

def connect_db():
    """Connect to the SQLite database."""
    return sqlite3.connect('chatgpt.db')

def find_canonical_endpoint(conversation_id):
    """
    Find the canonical endpoint of a conversation by:
    1. Finding all messages that have no children (leaf nodes)
    2. Among these, selecting the one with the latest timestamp
    """
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # First, find all messages in this conversation
        cursor.execute("""
            WITH RECURSIVE
            -- First, get all messages that are not parents (leaf nodes)
            leaf_nodes AS (
                SELECT m.id, m.create_time, m.update_time
                FROM messages m
                LEFT JOIN message_children mc ON m.id = mc.parent_id
                WHERE m.conversation_id = ?
                AND mc.parent_id IS NULL
            )
            -- Select the leaf node with the latest timestamp
            SELECT id, create_time, update_time
            FROM leaf_nodes
            ORDER BY update_time DESC, create_time DESC
            LIMIT 1
        """, (conversation_id,))
        
        result = cursor.fetchone()
        
        if result:
            message_id, create_time, update_time = result
            print(f"\nCanonical endpoint found:")
            print(f"Message ID: {message_id}")
            print(f"Create time: {create_time}")
            print(f"Update time: {update_time}")
            return message_id
        else:
            print("No messages found in conversation")
            return None
            
    finally:
        conn.close()

if __name__ == "__main__":
    # Test with the specific conversation
    CONVERSATION_ID = "67d1b5ea-1b48-8001-add4-5ee148c7aaf0"
    
    print(f"Finding canonical endpoint for conversation: {CONVERSATION_ID}")
    canonical_endpoint = find_canonical_endpoint(CONVERSATION_ID)
    
    if canonical_endpoint:
        print("\nSuccess! Found canonical endpoint.")
    else:
        print("\nFailed to find canonical endpoint.") 