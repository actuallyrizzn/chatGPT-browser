import json
import glob
import os
import sqlite3
from flask import Flask, render_template, g, jsonify, request, send_from_directory

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

# Register custom Jinja filters
app.jinja_env.filters["is_json"] = is_json
app.jinja_env.filters["parse_json"] = parse_json
app.jinja_env.filters["resolve_file"] = resolve_file_path

# Homepage - Show Conversations
@app.route("/")
def index():
    return render_template("index.html")

# Get messages in a conversation
@app.route("/messages/<conversation_id>")
def messages(conversation_id):
    db = get_db()
    messages = db.execute(
        "SELECT id, author_role, content, strftime('%Y-%m-%d %H:%M:%S', create_time, 'unixepoch') AS create_time "
        "FROM messages WHERE conversation_id = ? ORDER BY create_time ASC",
        (conversation_id,)
    ).fetchall()
    
    return render_template("messages.html", messages=messages, conversation_id=conversation_id)

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

if __name__ == "__main__":
    app.run(debug=True)