from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from markupsafe import Markup
import sqlite3
import json
from datetime import datetime
import markdown
from markdown.extensions import fenced_code, tables
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Initialize markdown with extensions
md = markdown.Markdown(extensions=['fenced_code', 'tables'])

# Add Jinja filters
@app.template_filter('fromjson')
def fromjson(value):
    try:
        return json.loads(value)
    except:
        return []

@app.template_filter('tojson')
def tojson(value, indent=None):
    try:
        return json.dumps(value, indent=indent)
    except:
        return str(value)

def get_db():
    conn = sqlite3.connect('chatgpt.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    
    # Create conversations table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            create_time TEXT,
            update_time TEXT,
            title TEXT
        )
    ''')
    
    # Create messages table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            conversation_id TEXT,
            role TEXT,
            content TEXT,
            create_time TEXT,
            update_time TEXT,
            parent_id TEXT,
            FOREIGN KEY (conversation_id) REFERENCES conversations(id)
        )
    ''')
    
    # Create message metadata table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS message_metadata (
            message_id TEXT PRIMARY KEY,
            message_type TEXT,
            model_slug TEXT,
            citations TEXT,
            content_references TEXT,
            finish_details TEXT,
            is_complete BOOLEAN,
            request_id TEXT,
            timestamp_ TEXT,
            message_source TEXT,
            serialization_metadata TEXT,
            FOREIGN KEY (message_id) REFERENCES messages(id)
        )
    ''')
    
    # Create message children relationships table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS message_children (
            parent_id TEXT,
            child_id TEXT,
            PRIMARY KEY (parent_id, child_id),
            FOREIGN KEY (parent_id) REFERENCES messages(id),
            FOREIGN KEY (child_id) REFERENCES messages(id)
        )
    ''')
    
    # Create settings table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Insert default settings if they don't exist
    conn.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('user_name', 'User'))
    conn.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('assistant_name', 'Assistant'))
    conn.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('dev_mode', 'false'))
    conn.execute('INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)', ('dark_mode', 'false'))
    
    conn.commit()
    conn.close()

def get_setting(key, default=None):
    conn = get_db()
    setting = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
    conn.close()
    return setting['value'] if setting else default

def set_setting(key, value):
    conn = get_db()
    conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

@app.template_filter('datetime')
def format_datetime(timestamp):
    try:
        # Handle both string and float timestamps
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return timestamp

@app.template_filter('json_loads')
def json_loads_filter(value):
    if value is None:
        return []
    try:
        return json.loads(value)
    except (ValueError, TypeError):
        return []

@app.template_filter('markdown')
def markdown_filter(text):
    if text is None:
        return ""
    return Markup(md.convert(text))

@app.route('/')
def index():
    conn = get_db()
    conversations = conn.execute('''
        SELECT id, title, create_time, update_time 
        FROM conversations 
        ORDER BY update_time DESC
    ''').fetchall()
    conn.close()
    dev_mode = get_setting('dev_mode', 'false') == 'true'
    dark_mode = get_setting('dark_mode', 'false') == 'true'
    user_name = get_setting('user_name', 'User')
    assistant_name = get_setting('assistant_name', 'Assistant')
    return render_template('index.html', 
                         conversations=conversations,
                         dev_mode=dev_mode,
                         dark_mode=dark_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)

@app.route('/conversation/<conversation_id>')
def conversation(conversation_id):
    conn = get_db()
    conversation = conn.execute('SELECT * FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
    
    if not conversation:
        return "Conversation not found", 404
    
    # Get all messages with their metadata
    messages = conn.execute('''
        SELECT m.*, 
               mm.message_type, mm.model_slug, mm.citations, mm.content_references,
               mm.finish_details, mm.is_complete, mm.request_id, mm.timestamp_,
               mm.message_source, mm.serialization_metadata
        FROM messages m
        LEFT JOIN message_metadata mm ON m.id = mm.message_id
        WHERE m.conversation_id = ?
        ORDER BY m.create_time
    ''', (conversation_id,)).fetchall()
    
    conn.close()
    
    # Convert messages to list of dicts with metadata
    message_list = []
    for msg in messages:
        message_dict = dict(msg)
        if message_dict['message_type']:  # If metadata exists
            message_dict['metadata'] = {
                'message_type': message_dict.pop('message_type'),
                'model_slug': message_dict.pop('model_slug'),
                'citations': message_dict.pop('citations'),
                'content_references': message_dict.pop('content_references'),
                'finish_details': message_dict.pop('finish_details'),
                'is_complete': message_dict.pop('is_complete'),
                'request_id': message_dict.pop('request_id'),
                'timestamp_': message_dict.pop('timestamp_'),
                'message_source': message_dict.pop('message_source'),
                'serialization_metadata': message_dict.pop('serialization_metadata')
            }
        message_list.append(message_dict)
    
    dev_mode = get_setting('dev_mode', 'false') == 'true'
    dark_mode = get_setting('dark_mode', 'false') == 'true'
    user_name = get_setting('user_name', 'User')
    assistant_name = get_setting('assistant_name', 'Assistant')
    
    return render_template('conversation.html',
                         conversation=conversation,
                         messages=message_list,
                         dev_mode=dev_mode,
                         dark_mode=dark_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)

@app.route('/conversation/<conversation_id>/nice')
def nice_conversation(conversation_id):
    conn = get_db()
    conversation = conn.execute('SELECT * FROM conversations WHERE id = ?', (conversation_id,)).fetchone()
    
    if not conversation:
        return "Conversation not found", 404
    
    # Find the canonical endpoint
    canonical_endpoint = conn.execute('''
        SELECT m.id, m.role, m.content, m.create_time, m.parent_id
        FROM messages m
        LEFT JOIN messages child ON m.id = child.parent_id
        WHERE m.conversation_id = ? AND child.id IS NULL
        ORDER BY m.create_time DESC
        LIMIT 1
    ''', (conversation_id,)).fetchone()
    
    if not canonical_endpoint:
        return "No canonical endpoint found", 404
    
    # Get the path to root
    path = []
    current_id = canonical_endpoint['id']
    
    while current_id:
        message = conn.execute('''
            SELECT id, role, content, create_time, parent_id
            FROM messages
            WHERE id = ?
        ''', (current_id,)).fetchone()
        
        if not message:
            break
            
        path.append(message)
        
        if not message['parent_id']:
            break
            
        current_id = message['parent_id']
    
    conn.close()
    
    dev_mode = get_setting('dev_mode', 'false') == 'true'
    dark_mode = get_setting('dark_mode', 'false') == 'true'
    user_name = get_setting('user_name', 'User')
    assistant_name = get_setting('assistant_name', 'Assistant')
    
    return render_template('nice_conversation.html',
                         conversation=conversation,
                         messages=path,
                         canonical_endpoint=canonical_endpoint['id'],
                         dev_mode=dev_mode,
                         dark_mode=dark_mode,
                         user_name=user_name,
                         assistant_name=assistant_name)

@app.route('/import', methods=['POST'])
def import_json():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400
        
    try:
        content = file.read()
        if not content:
            return 'Empty file', 400
            
        data = json.loads(content)
        if not isinstance(data, list):
            data = [data]
            
        print(f"Importing {len(data)} conversations...")
        
        conn = get_db()
        
        for conversation in data:
            try:
                # Extract conversation data
                conversation_id = conversation.get('id')
                if not conversation_id:
                    print(f"Skipping conversation: missing ID")
                    continue
                    
                create_time = conversation.get('create_time', '')
                update_time = conversation.get('update_time', '')
                title = conversation.get('title', '')
                
                # Insert conversation
                conn.execute('''
                    INSERT OR REPLACE INTO conversations 
                    (id, create_time, update_time, title)
                    VALUES (?, ?, ?, ?)
                ''', (conversation_id, create_time, update_time, title))
                
                # Process messages
                messages = conversation.get('mapping', {})
                for message_id, message_data in messages.items():
                    try:
                        message = message_data.get('message', {})
                        if not message:
                            continue
                            
                        author = message.get('author', {})
                        content = message.get('content', {})
                        
                        # Extract message data
                        role = author.get('role', '')
                        content_text = json.dumps(content.get('parts', []))
                        
                        # Handle timestamps - convert to float if string, or use None if missing/invalid
                        def parse_timestamp(ts):
                            if ts is None:
                                return None
                            try:
                                if isinstance(ts, str):
                                    return float(ts)
                                return ts
                            except (ValueError, TypeError):
                                return None
                        
                        msg_create_time = parse_timestamp(message.get('create_time'))
                        msg_update_time = parse_timestamp(message.get('update_time'))
                        
                        # Get parent ID from message_data
                        parent_id = message_data.get('parent', '')
                        
                        # Insert message
                        conn.execute('''
                            INSERT OR REPLACE INTO messages
                            (id, conversation_id, role, content, create_time, update_time, parent_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        ''', (message_id, conversation_id, role, content_text, 
                              msg_create_time, msg_update_time, parent_id))
                        
                        # Process children relationships
                        children = message_data.get('children', [])
                        if children:
                            # First remove any existing relationships for this message
                            conn.execute('DELETE FROM message_children WHERE parent_id = ?', (message_id,))
                            # Then insert new relationships
                            for child_id in children:
                                conn.execute('''
                                    INSERT INTO message_children (parent_id, child_id)
                                    VALUES (?, ?)
                                ''', (message_id, child_id))
                        
                        # Extract metadata if available
                        metadata = message.get('metadata', {})
                        if metadata:
                            conn.execute('''
                                INSERT OR REPLACE INTO message_metadata
                                (message_id, message_type, model_slug, citations, 
                                 content_references, finish_details, is_complete,
                                 request_id, timestamp_, message_source, serialization_metadata)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                message_id,
                                metadata.get('message_type', ''),
                                metadata.get('model_slug', ''),
                                json.dumps(metadata.get('citations', [])),
                                json.dumps(metadata.get('content_references', [])),
                                json.dumps(metadata.get('finish_details', {})),
                                metadata.get('is_complete', False),
                                metadata.get('request_id', ''),
                                metadata.get('timestamp', ''),
                                metadata.get('message_source', ''),
                                json.dumps(metadata.get('serialization_metadata', {}))
                            ))
                            
                    except Exception as e:
                        print(f"Error processing message {message_id}: {str(e)}")
                        continue
                        
            except Exception as e:
                print(f"Error processing conversation {conversation_id}: {str(e)}")
                continue
                
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
        
    except json.JSONDecodeError:
        return 'Invalid JSON file', 400
    except Exception as e:
        return f'Error importing file: {str(e)}', 400

@app.route('/toggle_dev_mode')
def toggle_dev_mode():
    current_mode = get_setting('dev_mode', 'false')
    new_mode = 'true' if current_mode == 'false' else 'false'
    set_setting('dev_mode', new_mode)
    return redirect(request.referrer or url_for('index'))

@app.route('/toggle_dark_mode')
def toggle_dark_mode():
    current_mode = get_setting('dark_mode', 'false')
    new_mode = 'true' if current_mode == 'false' else 'false'
    set_setting('dark_mode', new_mode)
    return redirect(request.referrer or url_for('index'))

@app.route('/settings')
def settings():
    user_name = get_setting('user_name', 'User')
    assistant_name = get_setting('assistant_name', 'Assistant')
    dark_mode = get_setting('dark_mode', 'false') == 'true'
    dev_mode = get_setting('dev_mode', 'false') == 'true'
    
    return render_template('settings.html',
                         user_name=user_name,
                         assistant_name=assistant_name,
                         dark_mode=dark_mode,
                         dev_mode=dev_mode)

@app.route('/update_names', methods=['POST'])
def update_names():
    user_name = request.form.get('user_name', 'User')
    assistant_name = request.form.get('assistant_name', 'Assistant')
    
    # Update settings in database
    conn = get_db()
    conn.execute('UPDATE settings SET value = ? WHERE key = ?', (user_name, 'user_name'))
    conn.execute('UPDATE settings SET value = ? WHERE key = ?', (assistant_name, 'assistant_name'))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True) 