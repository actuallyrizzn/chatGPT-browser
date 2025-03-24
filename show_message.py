import sqlite3

def show_message(message_id):
    conn = sqlite3.connect('chatgpt.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, role, content, create_time, update_time
            FROM messages
            WHERE id = ?
        """, (message_id,))
        result = cursor.fetchone()
        
        if result:
            print(f"ID: {result[0]}")
            print(f"Role: {result[1]}")
            print(f"Create time: {result[3]}")
            print(f"Update time: {result[4]}")
            print("\nContent:")
            print(result[2])
        else:
            print(f"Message {message_id} not found")
            
    finally:
        conn.close()

if __name__ == "__main__":
    MESSAGE_ID = "3e0189c6-b894-4cbb-bf95-cae033e50b20"
    show_message(MESSAGE_ID) 