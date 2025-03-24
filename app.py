import json
import glob
import os
import sqlite3
import markdown
import re
import html
from flask import Flask, render_template, g, jsonify, request, send_from_directory, flash, redirect
from markupsafe import Markup
from datetime import datetime
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from collections import defaultdict

DATABASE = "athena.db"
UPLOAD_FOLDER = "./"  # Adjust if files are stored elsewhere

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.secret_key = 'your-secret-key-here'  # Add this line for flash messages

@dataclass
class Message:
    id: str
    role: str
    content: str
    create_time: int
    parent_id: Optional[str]
    children: List[str]
    metadata: dict

# Get database connection
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # Enables dict-like row access
    return g.db

# Close DB connection
@app.teardown_appcontext
def close_connection(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Custom Jinja filter to check if a string is JSON
def is_json(value):
    try:
        json.loads(value)  # Try parsing it
        return True
    except (ValueError, TypeError):
        return False

# Custom Jinja filter to parse JSON safely
def parse_json(value):
    try:
        return json.loads(value)  # Convert to Python dict
    except (ValueError, TypeError):
        return {}

# Helper function to resolve file-service paths using glob wildcard matching
def resolve_file_path(asset_pointer):
    """Finds a matching file for the given file-service path."""
    filename = asset_pointer.replace("file-service://", "")  # Strip prefix
    matching_files = glob.glob(os.path.join(app.config["UPLOAD_FOLDER"], f"{filename}-*.jpg"))

    if matching_files:
        return os.path.basename(matching_files[0])  # Return just the filename
    return None  # No matching file found

def strip_html(text):
    """Remove HTML tags and special control characters while preserving content"""
    if isinstance(text, dict):
        return str(text)
    
    # Debug: Log original text
    print(f"Original text: {repr(text)}")
    
    # Convert text to string and handle encoding
    text = str(text).encode('utf-8', 'ignore').decode('utf-8')
    print(f"After encoding: {repr(text)}")
    
    # Remove special Unicode control characters (e200-e206)
    control_chars = [chr(0xe200 + i) for i in range(7)]
    for char in control_chars:
        text = text.replace(char, '')
    
    # Replace common special characters
    text = text.replace('□', '')  # Remove square boxes
    text = text.replace('\u2028', '\n')  # Line separator
    text = text.replace('\u2029', '\n\n')  # Paragraph separator
    
    # Clean up citation markers
    text = re.sub(r'cite(?:turn\d+)?(?:search|news)\d+', '', text)
    text = re.sub(r'turn\d+(?:search|news)\d+', '', text)
    
    # Clean up navigation markers
    text = re.sub(r'navlist.*?(?=\n|$)', '', text)
    
    print(f"After special char replacement: {repr(text)}")
    
    # Replace </p> with newlines to maintain paragraph structure
    text = re.sub(r'</p>\s*<p>', '\n\n', text)
    
    # Remove all HTML tags while preserving content
    text = re.sub(r'<[^>]+>', '', text)
    
    # Unescape HTML entities
    text = html.unescape(text)
    
    # Clean up excessive whitespace
    text = re.sub(r'\n\s*\n', '\n\n', text)  # Normalize multiple newlines
    text = re.sub(r' +', ' ', text)  # Remove multiple spaces
    text = re.sub(r'^\s+', '', text, flags=re.MULTILINE)  # Remove leading whitespace
    text = re.sub(r'\s+$', '', text, flags=re.MULTILINE)  # Remove trailing whitespace
    
    result = text.strip()
    print(f"Final result: {repr(result)}")
    return result

# Custom Jinja filter to render markdown
def render_markdown(value):
    if not value:
        return ""
    # First strip HTML tags while preserving structure
    cleaned_text = strip_html(value)
    # Convert markdown to HTML and mark as safe
    html_content = markdown.markdown(cleaned_text, extensions=['fenced_code', 'tables', 'nl2br'])
    return Markup(html_content)

# Custom filter to safely get dict attribute
def safe_get(value, key, default=""):
    if isinstance(value, dict):
        return value.get(key, default)
    return default

# Custom Jinja filter to format timestamps
def format_timestamp(value):
    """Format a Unix timestamp into a readable string."""
    if not value:
        return ""
    try:
        return datetime.fromtimestamp(value).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return str(value)

# Register custom Jinja filters
app.jinja_env.filters["is_json"] = is_json
app.jinja_env.filters["parse_json"] = parse_json
app.jinja_env.filters["resolve_file"] = resolve_file_path
app.jinja_env.filters["markdown"] = render_markdown
app.jinja_env.filters["safe_get"] = safe_get
app.jinja_env.filters["format_timestamp"] = format_timestamp

# Homepage - Show Conversations
@app.route("/")
def index():
    """Show conversations list"""
    db = get_db()
    conversations = db.execute(
        "SELECT id, title, strftime('%Y-%m-%d %H:%M:%S', create_time, 'unixepoch') AS create_time "
        "FROM conversations ORDER BY create_time DESC"
    ).fetchall()
    return render_template("index.html", conversations=conversations)

# Get messages in a conversation
@app.route("/messages/<conversation_id>")
def messages(conversation_id):
    try:
        # Get the conversation details
        conversation = get_conversation(conversation_id)
        if not conversation:
            flash('Conversation not found', 'error')
            return redirect('/')
        
        # Get all messages for the conversation
        all_messages = get_messages_for_conversation(conversation_id)
        
        # Create a dictionary for easier message lookup
        messages_dict = {msg.id: msg for msg in all_messages}
        
        # Find root messages (messages with no parent)
        root_messages = [msg for msg in all_messages if not msg.parent_id]
        
        # Sort root messages by creation time
        root_messages.sort(key=lambda x: x.create_time)
        
        # Build canonical chains from each root message
        canonical_messages = []
        processed_ids = set()  # Track which messages we've already included
        
        for root in root_messages:
            if root.id in processed_ids:
                continue
                
            # Start a new chain with this root
            chain = []
            current = root
            
            while True:
                if current.id not in processed_ids:
                    chain.append(current)
                    processed_ids.add(current.id)
                
                # Look for the next message in the chain
                next_message = None
                
                # First try to find a child that hasn't been processed
                if current.children:
                    for child_id in current.children:
                        if child_id in messages_dict and child_id not in processed_ids:
                            next_message = messages_dict[child_id]
                            break
                
                # If no unprocessed child found, try to find a message that has this as parent
                if not next_message:
                    for msg in all_messages:
                        if msg.parent_id == current.id and msg.id not in processed_ids:
                            next_message = msg
                            break
                
                if next_message:
                    current = next_message
                else:
                    # No more messages to add to this chain
                    break
            
            # Only add chains that have at least one message
            if chain:
                canonical_messages.extend(chain)
        
        # If no canonical messages were found, fall back to chronological order
        if not canonical_messages:
            canonical_messages = sorted(all_messages, key=lambda x: x.create_time)
        
        # Ensure we have messages to display
        if not canonical_messages:
            flash('No messages found in this conversation', 'warning')
            return redirect('/')
        
        return render_template('messages.html',
                             conversation=conversation,
                             messages=canonical_messages,
                             all_messages=all_messages,
                             dev_view=True)  # Enable dev view by default for now
                             
    except Exception as e:
        app.logger.error(f"Error displaying messages for conversation {conversation_id}: {str(e)}")
        flash('An error occurred while loading the conversation', 'error')
        return redirect('/')

# API Endpoint for Server-Side Paginated Conversations
@app.route("/api/conversations")
def api_conversations():
    db = get_db()

    # Get pagination parameters from DataTables request
    start = int(request.args.get("start", 0))  # Offset (default = 0)
    length = int(request.args.get("length", 50))  # Number of records per page (default = 50)

    # Fetch total count of conversations
    total_count = db.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]

    # Fetch only the requested chunk with formatted timestamps
    conversations = db.execute(
        "SELECT id, title, strftime('%Y-%m-%d %H:%M:%S', create_time, 'unixepoch') AS create_time "
        "FROM conversations ORDER BY create_time DESC LIMIT ? OFFSET ?",
        (length, start)
    ).fetchall()

    # Format response in DataTables format
    return jsonify({
        "recordsTotal": total_count,
        "recordsFiltered": total_count,
        "data": [dict(row) for row in conversations]
    })

# API route to serve image files
@app.route("/files/<filename>")
def serve_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

def get_conversation(conversation_id):
    """Get a conversation by ID."""
    db = get_db()
    conversation = db.execute(
        """
        SELECT 
            id, 
            title, 
            create_time,
            update_time,
            is_archived,
            is_starred,
            default_model_slug
        FROM conversations 
        WHERE id = ?
        """,
        (conversation_id,)
    ).fetchone()
    
    if conversation:
        return dict(conversation)
    return None

def get_messages(conversation_id):
    """Get messages for a conversation, properly threaded"""
    db = get_db()
    
    try:
        # Get all messages with their metadata
        messages = db.execute("""
            SELECT m.id, m.author_role, m.content, 
                   strftime('%Y-%m-%d %H:%M:%S', m.create_time, 'unixepoch') AS create_time,
                   COALESCE(mm.parent_id, '') as parent_id,
                   COALESCE(mm.request_id, '') as request_id,
                   COALESCE(mm.message_type, '') as message_type,
                   COALESCE(mm.model_slug, '') as model_slug,
                   COALESCE(mm.finish_details, '') as finish_details,
                   COALESCE(mm.citations, '') as citations,
                   COALESCE((SELECT GROUP_CONCAT(child_id) FROM message_children WHERE parent_id = m.id), '') as children
            FROM messages m
            LEFT JOIN message_metadata mm ON m.id = mm.id
            WHERE m.conversation_id = ? 
            AND m.content != ''
            AND m.author_role != 'system'
            ORDER BY m.create_time ASC
        """, (conversation_id,)).fetchall()
        
        # Group messages by role and content similarity
        user_groups = []  # List of groups of similar user messages
        current_user_group = []
        assistant_responses = []  # List of assistant responses
        
        for msg in messages:
            msg_dict = dict(msg)
            
            # Add metadata to message dictionary
            msg_dict['has_metadata'] = bool(msg_dict.get('parent_id') or msg_dict.get('children'))
            msg_dict['model'] = msg_dict.get('model_slug', '').split(':')[-1] if msg_dict.get('model_slug') else ''
            
            if msg_dict['author_role'] == 'user':
                # If this is a new topic (not similar to previous messages), start a new group
                if not current_user_group or not is_similar_content(msg_dict['content'], current_user_group[0]['content']):
                    if current_user_group:
                        user_groups.append(current_user_group)
                    current_user_group = [msg_dict]
                else:
                    # Add to current group (it's a variation)
                    current_user_group.append(msg_dict)
            else:  # assistant message
                assistant_responses.append(msg_dict)
        
        # Add the final user group
        if current_user_group:
            user_groups.append(current_user_group)
        
        # Build canonical thread
        canonical_thread = []
        
        for group in user_groups:
            # Add the most complete user message from the group
            best_user_msg = max(group, key=lambda m: len(m['content']))
            canonical_thread.append(best_user_msg)
            
            # Find and add the corresponding assistant response
            msg_time = best_user_msg['create_time']
            next_responses = [r for r in assistant_responses if r['create_time'] > msg_time]
            if next_responses:
                canonical_thread.append(next_responses[0])
                assistant_responses.remove(next_responses[0])
        
        return canonical_thread
        
    except sqlite3.Error as e:
        print(f"Database error in get_messages: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error in get_messages: {e}")
        return []

def is_similar_content(content1, content2, threshold=0.7):
    """Check if two messages are similar based on content"""
    # Convert to lowercase and get first 100 chars
    c1 = content1.lower()[:100]
    c2 = content2.lower()[:100]
    
    # If one is a prefix of the other, they're similar
    if c1.startswith(c2[:50]) or c2.startswith(c1[:50]):
        return True
        
    # If they share a lot of words, they're similar
    words1 = set(c1.split())
    words2 = set(c2.split())
    if len(words1) == 0 or len(words2) == 0:
        return False
    
    common_words = words1.intersection(words2)
    similarity = len(common_words) / max(len(words1), len(words2))
    return similarity >= threshold

def get_message_details(message_id):
    """Get detailed message information including all metadata"""
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
        
    except sqlite3.Error as e:
        print(f"Database error in get_message_details: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_message_details: {e}")
        return None

def get_paginated_messages(conversation_id, page=1, per_page=50):
    """Get paginated messages for a conversation"""
    db = get_db()
    offset = (page - 1) * per_page
    
    try:
        # Get total count
        total_count = db.execute(
            "SELECT COUNT(*) FROM messages WHERE conversation_id = ?",
            (conversation_id,)
        ).fetchone()[0]
        
        # Get messages for current page
        messages = db.execute("""
            SELECT m.id, m.author_role, m.content, 
                   strftime('%Y-%m-%d %H:%M:%S', m.create_time, 'unixepoch') AS create_time,
                   COALESCE(mm.parent_id, '') as parent_id,
                   COALESCE(mm.model_slug, '') as model_slug
            FROM messages m
            LEFT JOIN message_metadata mm ON m.id = mm.id
            WHERE m.conversation_id = ?
            ORDER BY m.create_time ASC
            LIMIT ? OFFSET ?
        """, (conversation_id, per_page, offset)).fetchall()
        
        return {
            'messages': [dict(msg) for msg in messages],
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'total_pages': (total_count + per_page - 1) // per_page
        }
        
    except sqlite3.Error as e:
        print(f"Database error in get_paginated_messages: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error in get_paginated_messages: {e}")
        return None

@app.route("/api/messages/<conversation_id>")
def api_messages(conversation_id):
    """API endpoint for paginated messages"""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        
        result = get_paginated_messages(conversation_id, page, per_page)
        if result is None:
            return jsonify({'error': 'Failed to fetch messages'}), 500
            
        return jsonify(result)
        
    except ValueError:
        return jsonify({'error': 'Invalid page or per_page parameter'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/api/messages/<conversation_id>/<message_id>/details")
def api_message_details(conversation_id, message_id):
    """API endpoint for getting detailed message information"""
    try:
        message = get_message_details(message_id)
        if message is None:
            return jsonify({'error': 'Message not found'}), 404
            
        # Verify the message belongs to the conversation
        if str(message.get('conversation_id')) != conversation_id:
            return jsonify({'error': 'Message does not belong to this conversation'}), 403
            
        return jsonify(message)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_messages_for_conversation(conversation_id: str) -> List[Message]:
    """Get all messages for a conversation with their relationships."""
    db = get_db()
    
    # Get all messages for the conversation
    messages = db.execute("""
        SELECT 
            m.id,
            m.author_role as role,
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
        # Parse children array, removing null values that come from the LEFT JOIN
        children_str = msg['children']
        try:
            children = json.loads(children_str) if children_str else []
            children = [c for c in children if c is not None]
        except json.JSONDecodeError:
            children = []

        # Parse metadata
        try:
            metadata = json.loads(msg['metadata']) if msg['metadata'] else {}
            # Clean up null values and parse JSON strings
            for key in ['finish_details', 'citations', 'content_references']:
                if key in metadata and metadata[key]:
                    try:
                        metadata[key] = json.loads(metadata[key])
                    except (json.JSONDecodeError, TypeError):
                        metadata[key] = None
        except json.JSONDecodeError:
            metadata = {}

        # Create Message object
        message = Message(
            id=msg['id'],
            role=msg['role'],
            content=msg['content'] or '',  # Handle NULL content
            create_time=msg['create_time'],
            parent_id=msg['parent_id'],
            children=children,
            metadata=metadata
        )
        result.append(message)

    return result

def find_root_messages(messages: Dict[str, Message]) -> Set[str]:
    """Find all messages that have no parent (root nodes)."""
    return {msg_id for msg_id, msg in messages.items() 
            if not msg.parent_id and msg.role == 'user'}

def find_canonical_path(messages: Dict[str, Message], msg_id: str, direction: str = 'forward') -> List[Message]:
    """
    Find the canonical path from a message.
    direction: 'forward' to trace to leaves, 'backward' to trace to root, 'both' for full chain
    """
    path = []
    visited = set()
    
    def trace_backward(current_id):
        current_path = []
        while current_id and current_id not in visited:
            if current_id not in messages:
                break
            visited.add(current_id)
            msg = messages[current_id]
            if msg.role != 'system':
                current_path.append(msg)
            current_id = msg.parent_id
        return list(reversed(current_path))
    
    def trace_forward(current_id):
        current_path = []
        while current_id and current_id not in visited:
            if current_id not in messages:
                break
            visited.add(current_id)
            msg = messages[current_id]
            if msg.role != 'system':
                current_path.append(msg)
            # For forward tracing, we take the first child (if any)
            current_id = msg.children[0] if msg.children else None
        return current_path
    
    if direction == 'backward':
        path = trace_backward(msg_id)
    elif direction == 'forward':
        path = trace_forward(msg_id)
    else:  # both
        # First trace back to root
        root_path = trace_backward(msg_id)
        visited.clear()  # Reset visited set
        # Then trace forward from the original message
        forward_path = trace_forward(msg_id)
        # Combine paths, excluding the duplicate middle message
        path = root_path + forward_path[1:] if forward_path else root_path
    
    return path

def get_canonical_conversation(conversation_id: str) -> List[Message]:
    """Get the canonical conversation path for a given conversation ID."""
    messages = get_messages_for_conversation(conversation_id)
    if not messages:
        return []
    
    # Find all root messages
    root_nodes = find_root_messages(messages)
    if not root_nodes:
        return []
    
    # Get the first root message (chronologically)
    first_root = min(root_nodes, key=lambda msg_id: messages[msg_id].create_time)
    
    # Get the canonical path starting from this root
    return find_canonical_path(messages, first_root, 'forward')

if __name__ == "__main__":
    app.run(debug=True)