import sqlite3
from typing import List, Tuple, Optional

def get_message(message_id: str) -> Optional[Tuple]:
    """Get message details by ID"""
    conn = sqlite3.connect('chatgpt.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, role, content, create_time, parent_id
            FROM messages
            WHERE id = ?
        """, (message_id,))
        return cursor.fetchone()
    finally:
        conn.close()

def find_path_to_root(message_id: str, conversation_id: str) -> List[Tuple]:
    """Find path from message to root of conversation"""
    path = []
    current_id = message_id
    
    while current_id:
        message = get_message(current_id)
        if not message:
            break
            
        path.append(message)
        
        # If this is the root (no parent), we're done
        if not message[4]:  # parent_id is None
            break
            
        current_id = message[4]
    
    return path

def print_path(path: List[Tuple]):
    """Print the path in a readable format"""
    print("\nPath from canonical endpoint to root:")
    print("-" * 80)
    
    for msg in reversed(path):  # Print from root to endpoint
        print(f"ID: {msg[0]}")
        print(f"Role: {msg[1]}")
        print(f"Create time: {msg[3]}")
        print(f"Parent ID: {msg[4]}")
        print("-" * 80)

if __name__ == "__main__":
    CONVERSATION_ID = "678743d8-7910-8001-8b6f-056364b32f3f"
    CANONICAL_ENDPOINT = "3e0189c6-b894-4cbb-bf95-cae033e50b20"
    
    path = find_path_to_root(CANONICAL_ENDPOINT, CONVERSATION_ID)
    print_path(path) 