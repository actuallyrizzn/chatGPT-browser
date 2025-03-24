import json
import glob
import os
import sqlite3
import markdown
import re
import html
from flask import Flask, render_template, g, jsonify, request, send_from_directory
from markupsafe import Markup
from datetime import datetime

DATABASE = "athena.db"
UPLOAD_FOLDER = "./"  # Adjust if files are stored elsewhere

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Get database connection
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Enables dict-like row access
    return db

# Close DB connection
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
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

# Register custom Jinja filters
app.jinja_env.filters["is_json"] = is_json
app.jinja_env.filters["parse_json"] = parse_json
app.jinja_env.filters["resolve_file"] = resolve_file_path
app.jinja_env.filters["markdown"] = render_markdown
app.jinja_env.filters["safe_get"] = safe_get

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
    """Show messages in a conversation"""
    messages = get_messages(conversation_id)
    conversation = get_conversation(conversation_id)
    
    # For dev mode, get all messages
    db = get_db()
    all_messages = db.execute(
        "SELECT id, author_role as role, content, strftime('%Y-%m-%d %H:%M:%S', create_time, 'unixepoch') AS create_time "
        "FROM messages WHERE conversation_id = ? ORDER BY create_time ASC",
        (conversation_id,)
    ).fetchall()
    
    return render_template(
        "messages.html",
        messages=messages,  # Canonical thread for nice view
        all_messages=all_messages,  # All messages for dev view
        conversation=conversation,
        conversation_id=conversation_id
    )

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
    """Get conversation details"""
    db = get_db()
    return db.execute(
        "SELECT id, title, strftime('%Y-%m-%d %H:%M:%S', create_time, 'unixepoch') AS create_time "
        "FROM conversations WHERE id = ?",
        (conversation_id,)
    ).fetchone()

def get_messages(conversation_id):
    """Get messages for a conversation, properly threaded"""
    db = get_db()
    
    # Get all messages with their metadata
    messages = db.execute("""
        SELECT m.id, m.author_role, m.content, 
               strftime('%Y-%m-%d %H:%M:%S', m.create_time, 'unixepoch') AS create_time,
               mm.parent_id,
               (SELECT GROUP_CONCAT(child_id) FROM message_children WHERE parent_id = m.id) as children
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
        # Get the latest user message from this group
        latest_user = max(group, key=lambda m: m['create_time'])
        canonical_thread.append(latest_user)
        
        # Find the first assistant response that came after this user message
        possible_responses = [
            r for r in assistant_responses
            if r['create_time'] > latest_user['create_time']
        ]
        
        if possible_responses:
            # Take the first response after this user message
            response = min(possible_responses, key=lambda r: r['create_time'])
            canonical_thread.append(response)
            # Remove this response so it's not used again
            assistant_responses.remove(response)
    
    return canonical_thread

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

if __name__ == "__main__":
    app.run(debug=True)