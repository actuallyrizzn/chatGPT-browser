from typing import List, Optional, Dict, Any
import json
from datetime import datetime
from .connection import get_db
from .models import Conversation, Message

def get_conversation(conversation_id: str) -> Optional[Conversation]:
    """Get a conversation by ID."""
    db = get_db()
    row = db.execute(
        "SELECT * FROM conversations WHERE id = ?",
        (conversation_id,)
    ).fetchone()
    
    if row:
        return Conversation(**dict(row))
    return None

def get_conversations() -> List[Conversation]:
    """Get all conversations."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM conversations ORDER BY create_time DESC"
    ).fetchall()
    return [Conversation(**dict(row)) for row in rows]

def get_messages_for_conversation(conversation_id: str) -> List[Message]:
    """Get all messages for a conversation with their relationships."""
    db = get_db()
    
    messages = db.execute("""
        SELECT 
            m.id,
            m.conversation_id,
            m.author_role,
            m.content,
            m.create_time,
            mm.parent_id,
            (
                SELECT json_group_array(child_id)
                FROM message_children mc
                WHERE mc.parent_id = m.id
            ) as children,
            json_object(
                'model', mm.model_slug,
                'finish_details', mm.finish_details,
                'citations', mm.citations,
                'content_references', mm.content_references,
                'message_type', mm.message_type,
                'request_id', mm.request_id,
                'message_source', mm.message_source,
                'timestamp', mm.timestamp
            ) as metadata
        FROM messages m
        LEFT JOIN message_metadata mm ON m.id = mm.id
        WHERE m.conversation_id = ?
        AND m.author_role != 'system'
        AND m.content IS NOT NULL
        AND m.content != ''
        GROUP BY m.id
        ORDER BY m.create_time ASC
    """, (conversation_id,)).fetchall()

    result = []
    for msg in messages:
        msg_dict = dict(msg)
        
        # Parse children array
        children_str = msg_dict.pop('children')
        try:
            children = json.loads(children_str) if children_str else []
            children = [c for c in children if c is not None]
        except json.JSONDecodeError:
            children = []
        msg_dict['children'] = children

        # Parse metadata
        metadata_str = msg_dict.pop('metadata')
        try:
            metadata = json.loads(metadata_str) if metadata_str else {}
            for key in ['finish_details', 'citations', 'content_references']:
                if key in metadata and metadata[key]:
                    try:
                        metadata[key] = json.loads(metadata[key])
                    except (json.JSONDecodeError, TypeError):
                        metadata[key] = None
        except json.JSONDecodeError:
            metadata = {}
        msg_dict['metadata'] = metadata

        result.append(Message(**msg_dict))

    return result

def insert_message(msg: Message) -> bool:
    """Insert or update a message in the database."""
    db = get_db()
    try:
        # Insert message
        db.execute("""
            INSERT OR REPLACE INTO messages 
            (id, conversation_id, author_role, content, create_time)
            VALUES (?, ?, ?, ?, ?)
        """, (
            msg.id,
            msg.conversation_id,
            msg.author_role,
            msg.content,
            msg.create_time
        ))

        # Insert metadata if exists
        if msg.metadata:
            db.execute("""
                INSERT OR REPLACE INTO message_metadata 
                (id, parent_id, model_slug, finish_details, citations, content_references)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                msg.id,
                msg.parent_id,
                msg.metadata.get('model'),
                json.dumps(msg.metadata.get('finish_details')),
                json.dumps(msg.metadata.get('citations')),
                json.dumps(msg.metadata.get('content_references'))
            ))

        # Insert children relationships
        if msg.children:
            for child_id in msg.children:
                db.execute("""
                    INSERT OR REPLACE INTO message_children 
                    (parent_id, child_id) VALUES (?, ?)
                """, (msg.id, child_id))

        db.commit()
        return True
    except Exception as e:
        print(f"Error inserting message {msg.id}: {e}")
        db.rollback()
        return False 

def get_message_details(message_id: str) -> Optional[Dict]:
    """Get detailed message information including all metadata."""
    db = get_db()
    
    try:
        message = db.execute("""
            SELECT m.*, 
                   mm.request_id, 
                   mm.message_source, 
                   mm.timestamp,
                   mm.message_type, 
                   mm.model_slug, 
                   mm.parent_id,
                   mm.finish_details, 
                   mm.citations, 
                   mm.content_references,
                   (SELECT GROUP_CONCAT(child_id) FROM message_children WHERE parent_id = m.id) as children
            FROM messages m
            LEFT JOIN message_metadata mm ON m.id = mm.id
            WHERE m.id = ?
        """, (message_id,)).fetchone()
        
        if message:
            result = dict(message)
            # Convert timestamps to readable format
            if result.get('create_time'):
                result['create_time'] = datetime.fromtimestamp(result['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            if result.get('timestamp'):
                result['timestamp'] = datetime.fromtimestamp(result['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            # Parse JSON fields
            for field in ['finish_details', 'citations', 'content_references']:
                if result.get(field):
                    try:
                        result[field] = json.loads(result[field])
                    except json.JSONDecodeError:
                        result[field] = None
            # Split children into list if present
            if result.get('children'):
                result['children'] = result['children'].split(',')
            return result
        return None
        
    except Exception as e:
        print(f"Error getting message details for {message_id}: {e}")
        return None 