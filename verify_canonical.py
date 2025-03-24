import sqlite3
from datetime import datetime

def connect_db():
    return sqlite3.connect('chatgpt.db')

def verify_endpoint(conversation_id):
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # 1. Get all messages in the conversation
        print("\n1. All messages in conversation:")
        cursor.execute("""
            SELECT id, create_time, update_time
            FROM messages
            WHERE conversation_id = ?
        """, (conversation_id,))
        all_messages = cursor.fetchall()
        print(f"Total messages: {len(all_messages)}")
        
        # 2. Find all leaf nodes (messages with no children)
        print("\n2. All leaf nodes (messages with no children):")
        cursor.execute("""
            SELECT m.id, m.create_time, m.update_time
            FROM messages m
            LEFT JOIN message_children mc ON m.id = mc.parent_id
            WHERE m.conversation_id = ?
            AND mc.parent_id IS NULL
            ORDER BY m.update_time DESC, m.create_time DESC
        """, (conversation_id,))
        leaf_nodes = cursor.fetchall()
        for node in leaf_nodes:
            print(f"ID: {node[0]}")
            print(f"Create time: {node[1]}")
            print(f"Update time: {node[2]}")
            print("---")
            
        # 3. Verify our canonical endpoint is indeed the latest
        print("\n3. Verifying latest timestamp among all messages:")
        cursor.execute("""
            SELECT id, create_time, update_time
            FROM messages
            WHERE conversation_id = ?
            ORDER BY update_time DESC, create_time DESC
            LIMIT 1
        """, (conversation_id,))
        latest_message = cursor.fetchone()
        print(f"Latest message overall:")
        print(f"ID: {latest_message[0]}")
        print(f"Create time: {latest_message[1]}")
        print(f"Update time: {latest_message[2]}")
        
    finally:
        conn.close()

if __name__ == "__main__":
    CONVERSATION_ID = "678743d8-7910-8001-8b6f-056364b32f3f"
    verify_endpoint(CONVERSATION_ID) 