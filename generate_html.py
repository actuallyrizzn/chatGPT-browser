import sqlite3
from typing import List, Tuple
from datetime import datetime

def get_message(message_id: str) -> Tuple:
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

def find_path_to_root(message_id: str) -> List[Tuple]:
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

def format_timestamp(create_time: float) -> str:
    """Format timestamp to human-readable string"""
    try:
        return datetime.fromtimestamp(create_time).strftime('%Y-%m-%d %H:%M:%S')
    except (TypeError, ValueError):
        return "Unknown"

def generate_html(path: List[Tuple], conversation_id: str, canonical_endpoint: str):
    """Generate HTML visualization of the conversation path"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Conversation Path Visualization</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            .message {{
                background-color: white;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .user {{
                background-color: #e3f2fd;
                margin-left: 20px;
            }}
            .assistant {{
                background-color: #f5f5f5;
                margin-right: 20px;
            }}
            .system {{
                background-color: #fff3e0;
                margin-left: 40px;
            }}
            .metadata {{
                font-size: 0.8em;
                color: #666;
                margin-top: 5px;
            }}
            .content {{
                white-space: pre-wrap;
                margin-top: 10px;
            }}
            .canonical {{
                border: 2px solid #4caf50;
            }}
            .root {{
                border: 2px solid #f44336;
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            .info {{
                background-color: #fff;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
        </style>
    </head>
    <body>
        <h1>Conversation Path Visualization</h1>
        <div class="info">
            <p><strong>Conversation ID:</strong> {conversation_id}</p>
            <p><strong>Canonical Endpoint:</strong> {canonical_endpoint}</p>
            <p><strong>Total Messages:</strong> {len(path)}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    """
    
    for msg in reversed(path):  # Print from root to endpoint
        msg_id, role, content, create_time, parent_id = msg
        timestamp = format_timestamp(create_time)
        
        # Determine message class
        msg_class = role
        if msg_id == canonical_endpoint:
            msg_class += " canonical"
        if not parent_id:
            msg_class += " root"
            
        html += f"""
        <div class="message {msg_class}">
            <div class="metadata">
                <strong>ID:</strong> {msg_id}<br>
                <strong>Role:</strong> {role}<br>
                <strong>Time:</strong> {timestamp}<br>
                <strong>Parent:</strong> {parent_id if parent_id else 'None (Root)'}
            </div>
            <div class="content">{content}</div>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    with open('conversation_path.html', 'w', encoding='utf-8') as f:
        f.write(html)

if __name__ == "__main__":
    CONVERSATION_ID = "678743d8-7910-8001-8b6f-056364b32f3f"
    CANONICAL_ENDPOINT = "3e0189c6-b894-4cbb-bf95-cae033e50b20"
    
    path = find_path_to_root(CANONICAL_ENDPOINT)
    generate_html(path, CONVERSATION_ID, CANONICAL_ENDPOINT) 