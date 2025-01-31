import json
import sqlite3

# Load the JSON file
with open("C:/Users/guess/Downloads/Athena-01-30-25/conversations.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Connect to SQLite database
conn = sqlite3.connect("athena.db")
cursor = conn.cursor()

# Insert into conversations table
def insert_conversation(convo):
    cursor.execute("""
        INSERT OR IGNORE INTO conversations 
        (id, title, create_time, update_time, conversation_id, is_archived, is_starred, default_model_slug)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        convo.get("id"),
        convo.get("title"),
        convo.get("create_time"),
        convo.get("update_time"),
        convo.get("id"),  # Ensuring we're using the correct unique identifier
        convo.get("is_archived"),
        convo.get("is_starred"),
        convo.get("default_model_slug"),
    ))

# Insert into messages table
def insert_message(msg_id, convo_id, message):
    cursor.execute("""
        INSERT OR IGNORE INTO messages 
        (id, conversation_id, message_id, author_role, author_name, content_type, content, status, 
        end_turn, weight, recipient, channel, create_time, update_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        msg_id,
        convo_id,
        message.get("id", f"msg_{msg_id}"),  # Ensure an ID exists
        message.get("author", {}).get("role", "unknown"),
        message.get("author", {}).get("name", "anonymous"),
        message.get("content", {}).get("content_type", "text"),
        " ".join(
            part if isinstance(part, str) else json.dumps(part) 
            for part in message.get("content", {}).get("parts", [])
        ),  # Ensuring lists with dicts are stored as JSON
        message.get("status", "unknown"),
        message.get("end_turn"),
        message.get("weight", 0.0),  # Default to 0.0 if missing
        message.get("recipient", "unknown"),
        message.get("channel"),
        message.get("create_time", 0),
        message.get("update_time", 0),
    ))

# Insert into metadata table
def insert_metadata(msg_id, metadata):
    if metadata:
        cursor.execute("""
            INSERT OR IGNORE INTO message_metadata 
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
            json.dumps(metadata.get("finish_details", {})),  # Store as JSON
            json.dumps(metadata.get("citations", [])),  # Store as JSON
            json.dumps(metadata.get("content_references", [])),  # Store as JSON
        ))

# Insert into message_children table
def insert_children(parent_id, children):
    if children:
        for child_id in children:
            cursor.execute("""
                INSERT OR IGNORE INTO message_children 
                (parent_id, child_id) VALUES (?, ?)
            """, (parent_id, child_id))

# Process the JSON data
for convo in data:
    insert_conversation(convo)

    for msg_id, msg_data in convo.get("mapping", {}).items():
        message_data = msg_data.get("message")

        if isinstance(message_data, dict):  # Ensure message is valid
            insert_message(msg_id, convo.get("id"), message_data)
            insert_metadata(msg_id, message_data.get("metadata", {}))

        insert_children(msg_id, msg_data.get("children", []))  # Always process children

# Commit and close
conn.commit()
conn.close()

print("✅ Data successfully inserted into athena.db!")
