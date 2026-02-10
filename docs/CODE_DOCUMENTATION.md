# ChatGPT Browser - Code Documentation

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Database Schema](#database-schema)
4. [Core Application (`app.py`)](#core-application-apppy)
5. [Database Management](#database-management)
6. [Templates and Frontend](#templates-and-frontend)
7. [Static Assets](#static-assets)
8. [API Endpoints](#api-endpoints)
9. [Data Import System](#data-import-system) — including [What we exclude (for nerds)](#what-we-exclude-for-nerds)
10. [Settings Management](#settings-management)
11. [View Modes](#view-modes)
12. [Error Handling](#error-handling)
13. [Security Considerations](#security-considerations)
14. [Performance Optimizations](#performance-optimizations)
15. [Development Guidelines](#development-guidelines)

## Project Overview

ChatGPT Browser is a Flask-based web application designed to import, store, and browse ChatGPT conversation history. The application provides two distinct viewing modes:

- **Nice Mode**: Clean, focused view showing only the canonical conversation path
- **Dev Mode**: Full technical view with metadata and all conversation branches

### Key Features

- Import ChatGPT JSON export files
- Dual viewing modes (Nice/Dev)
- Dark/Light theme support
- Markdown rendering
- Conversation tree navigation
- Metadata inspection
- Customizable user/assistant names

## Architecture

### Technology Stack

- **Backend**: Flask 3.0.2
- **Database**: SQLite3
- **Template Engine**: Jinja2 3.1.3
- **Markdown Processing**: markdown 3.5.2
- **Date Handling**: python-dateutil 2.8.2

### Project Structure

```
chatGPT-browser/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization script
├── schema.sql            # Database schema definition
├── requirements.txt      # Python dependencies
├── templates/            # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── conversation.html
│   ├── nice_conversation.html
│   └── settings.html
├── static/               # Static assets
│   └── style.css
├── docs/                 # Documentation
│   └── CODE_DOCUMENTATION.md
└── diag-tools/           # Diagnostic tools (empty)
```

## Database Schema

### Core Tables

#### 1. `conversations` Table
Stores conversation metadata and basic information.

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,           -- ChatGPT conversation ID
    create_time TEXT,              -- Creation timestamp
    update_time TEXT,              -- Last update timestamp
    title TEXT                     -- Conversation title
);
```

#### 2. `messages` Table
Stores individual messages within conversations.

```sql
CREATE TABLE messages (
    id TEXT PRIMARY KEY,           -- Message ID
    conversation_id TEXT,          -- Foreign key to conversations
    role TEXT,                     -- 'user' or 'assistant'
    content TEXT,                  -- JSON-encoded message content
    create_time TEXT,              -- Message creation timestamp
    update_time TEXT,              -- Message update timestamp
    parent_id TEXT,                -- Parent message ID for threading
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);
```

#### 3. `message_metadata` Table
Stores technical metadata for messages.

```sql
CREATE TABLE message_metadata (
    message_id TEXT PRIMARY KEY,   -- Foreign key to messages
    message_type TEXT,             -- Type of message
    model_slug TEXT,               -- AI model used
    citations TEXT,                -- JSON-encoded citations
    content_references TEXT,       -- JSON-encoded content references
    finish_details TEXT,           -- JSON-encoded finish details
    is_complete BOOLEAN,           -- Whether message is complete
    request_id TEXT,               -- Request identifier
    timestamp_ TEXT,               -- Technical timestamp
    message_source TEXT,           -- Message source
    serialization_metadata TEXT,   -- JSON-encoded serialization metadata
    FOREIGN KEY (message_id) REFERENCES messages(id)
);
```

#### 4. `message_children` Table
Manages parent-child relationships between messages for conversation threading.

```sql
CREATE TABLE message_children (
    parent_id TEXT,                -- Parent message ID
    child_id TEXT,                 -- Child message ID
    PRIMARY KEY (parent_id, child_id),
    FOREIGN KEY (parent_id) REFERENCES messages(id),
    FOREIGN KEY (child_id) REFERENCES messages(id)
);
```

#### 5. `settings` Table
Stores application configuration settings.

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,          -- Setting key
    value TEXT                     -- Setting value
);
```

### Default Settings

```sql
INSERT OR IGNORE INTO settings (key, value) VALUES 
    ('user_name', 'User'),
    ('assistant_name', 'Assistant'),
    ('dev_mode', 'false'),         -- false = nice mode, true = dev mode
    ('dark_mode', 'false'),
    ('verbose_mode', 'false');
```

## Core Application (`app.py`)

### Application Initialization

```python
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Required for session management

# Initialize markdown with extensions
md = markdown.Markdown(extensions=['fenced_code', 'tables'])
```

### Database Connection Management

```python
def get_db():
    """Create and return a database connection with Row factory."""
    conn = sqlite3.connect('chatgpt.db')
    conn.row_factory = sqlite3.Row
    return conn
```

### Database Initialization

The `init_db()` function:
- Creates all necessary tables if they don't exist
- Sets up foreign key relationships
- Inserts default settings
- Handles database schema migrations

### Jinja2 Template Filters

#### JSON Filters
```python
@app.template_filter('fromjson')
def fromjson(value):
    """Convert JSON string to Python object."""
    try:
        return json.loads(value)
    except:
        return []

@app.template_filter('tojson')
def tojson(value, indent=None):
    """Convert Python object to JSON string."""
    try:
        return json.dumps(value, indent=indent)
    except:
        return str(value)
```

#### DateTime Filter
```python
@app.template_filter('datetime')
def format_datetime(timestamp):
    """Format timestamp for display."""
    try:
        if isinstance(timestamp, str):
            timestamp = float(timestamp)
        return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError):
        return timestamp
```

#### Markdown Filter
```python
@app.template_filter('markdown')
def markdown_filter(text):
    """Convert markdown text to HTML."""
    if text is None:
        return ""
    return Markup(md.convert(text))
```

## Database Management

### Settings Management

```python
def get_setting(key, default=None):
    """Retrieve a setting value from the database."""
    conn = get_db()
    setting = conn.execute('SELECT value FROM settings WHERE key = ?', (key,)).fetchone()
    conn.close()
    return setting['value'] if setting else default

def set_setting(key, value):
    """Store a setting value in the database."""
    conn = get_db()
    conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()
```

### Database Initialization Script (`init_db.py`)

```python
def main():
    # Remove existing database if it exists
    if os.path.exists('chatgpt.db'):
        os.remove('chatgpt.db')
    
    # Initialize fresh database
    init_db()
    print("Database initialized successfully!")
```

## Templates and Frontend

### Template Hierarchy

1. **`base.html`**: Base template with common layout and navigation
2. **`index.html`**: Conversation list page
3. **`conversation.html`**: Full conversation view (Dev mode)
4. **`nice_conversation.html`**: Clean conversation view (Nice mode)
5. **`settings.html`**: Application settings page

### Template Features

- **Theme Support**: Dark/light mode toggle
- **Responsive Design**: Mobile-friendly layout
- **Markdown Rendering**: Code highlighting and formatting
- **Dynamic Content**: Real-time settings updates
- **Navigation**: Breadcrumb-style navigation

## Static Assets

### CSS Styling (`static/style.css`)

The stylesheet provides:
- **Theme System**: Dark and light mode styles
- **Responsive Layout**: Mobile-first design
- **Typography**: Readable font choices and spacing
- **Interactive Elements**: Hover effects and transitions
- **Code Highlighting**: Syntax highlighting for code blocks

## API Endpoints

### Main Routes

#### 1. Index Page (`/`)
```python
@app.route('/')
def index():
    """Display conversation list with current settings."""
```
- **Method**: GET
- **Purpose**: Shows all conversations in chronological order
- **Template**: `index.html`

#### 2. Conversation View (`/conversation/<conversation_id>`)
```python
@app.route('/conversation/<conversation_id>')
def conversation(conversation_id):
    """Display full conversation in dev mode."""
```
- **Method**: GET
- **Purpose**: Shows complete conversation with all metadata
- **Template**: `conversation.html`
- **Redirects**: To nice view if dev mode is disabled

#### 3. Nice Conversation View (`/conversation/<conversation_id>/nice`)
```python
@app.route('/conversation/<conversation_id>/nice')
def nice_conversation(conversation_id):
    """Display canonical conversation path."""
```
- **Method**: GET
- **Purpose**: Shows only the canonical conversation path
- **Template**: `nice_conversation.html`

#### 4. Full Conversation View (`/conversation/<conversation_id>/full`)
```python
@app.route('/conversation/<conversation_id>/full')
def full_conversation(conversation_id):
    """Force dev mode for conversation view."""
```
- **Method**: GET
- **Purpose**: Temporarily enables dev mode for viewing
- **Behavior**: Sets session override and redirects

### Settings Routes

#### 5. Settings Page (`/settings`)
```python
@app.route('/settings')
def settings():
    """Display settings page."""
```
- **Method**: GET
- **Purpose**: Shows application settings
- **Template**: `settings.html`

#### 6. Update Names (`/update_names`)
```python
@app.route('/update_names', methods=['POST'])
def update_names():
    """Update user and assistant display names."""
```
- **Method**: POST
- **Purpose**: Updates display names in database
- **Redirects**: To index page

### Toggle Routes

#### 7. Toggle View Mode (`/toggle_view_mode`)
```python
@app.route('/toggle_view_mode')
def toggle_view_mode():
    """Toggle between nice and dev modes."""
```
- **Method**: GET
- **Purpose**: Switches between nice and dev viewing modes
- **Response**: JSON with new mode status

#### 8. Toggle Dark Mode (`/toggle_dark_mode`)
```python
@app.route('/toggle_dark_mode')
def toggle_dark_mode():
    """Toggle between dark and light themes."""
```
- **Method**: GET
- **Purpose**: Switches between dark and light themes
- **Redirects**: To previous page

#### 9. Toggle Verbose Mode (`/toggle_verbose_mode`)
```python
@app.route('/toggle_verbose_mode')
def toggle_verbose_mode():
    """Toggle verbose mode for additional details."""
```
- **Method**: GET
- **Purpose**: Shows/hides additional technical details
- **Response**: JSON with new verbose status

### Import Route

#### 10. Import JSON (`/import`)
```python
@app.route('/import', methods=['POST'])
def import_json():
    """Import ChatGPT conversation data from JSON file."""
```
- **Method**: POST
- **Purpose**: Processes ChatGPT export files
- **File Handling**: Accepts JSON file uploads
- **Redirects**: To index page after import

## Data Import System

### Import Process Flow

1. **File Validation**: Check for uploaded file and valid JSON
2. **Data Parsing**: Parse ChatGPT export format
3. **Conversation Processing**: Extract conversation metadata
4. **Message Processing**: Process individual messages and relationships
5. **Metadata Extraction**: Extract technical metadata
6. **Database Storage**: Store all data in SQLite database

### ChatGPT Export Format

The import system expects ChatGPT's JSON export format:

```json
[
  {
    "id": "conversation_id",
    "create_time": "timestamp",
    "update_time": "timestamp",
    "title": "Conversation Title",
    "mapping": {
      "message_id": {
        "id": "message_id",
        "message": {
          "id": "message_id",
          "author": {"role": "user|assistant"},
          "content": {"parts": ["message content"]},
          "create_time": "timestamp",
          "update_time": "timestamp",
          "metadata": {...}
        },
        "parent": "parent_message_id",
        "children": ["child_message_ids"]
      }
    }
  }
]
```

### Import Error Handling

- **File Validation**: Checks for empty files and valid JSON
- **Conversation Processing**: Skips conversations with missing IDs
- **Message Processing**: Continues processing even if individual messages fail
- **Database Transactions**: Uses transactions for data consistency

### What we exclude (for nerds)

This section is for anyone who cares exactly what data the importer does *not* store.

**1. Other files in the export**

Only `conversations.json` is read. Everything else in the ChatGPT export zip is ignored: `chat.html`, `group_chats.json`, `message_feedback.json`, `shared_conversations.json`, `shopping.json`, `user.json`. So group chats, feedback, shared conversations, and user profile are not imported.

**2. Whole conversations**

Any conversation with a missing or empty `id` is skipped (logged as "Skipping conversation: missing ID").

**3. Messages**

Any mapping entry whose `message` is missing or an empty dict is skipped. That message is never inserted and its id is not added to the set of "inserted" ids for that conversation.

**4. Message content**

Only `content.parts` is stored (as JSON). Other keys on `content` in the export are not persisted.

**5. Metadata**

Only a fixed set of metadata fields is stored: `message_type`, `model_slug`, `citations`, `content_references`, `finish_details`, `is_complete`, `request_id`, `timestamp`, `message_source`, `serialization_metadata`. Any other metadata keys are dropped.

**6. Parent–child links (`message_children`)**

We insert a row `(parent_id, child_id)` only when *both* the parent and the child message were successfully inserted for that conversation. We skip a link when:

- The **child** was not inserted (e.g. no `message` key, or exception during insert) — we don't add that child link.
- The **parent** was not inserted — we skip the entire block of children for that parent, so no links from that parent are added.

Sampling real export data shows:

- **Excluded "child" links** (parent inserted, child not): In practice **0** in sampled conversations. We are not dropping links because the child message was missing.
- **Excluded "parent" blocks**: Typically **one per conversation**. These are mapping entries that have a `children` array but **no `message` key** (or an empty message). They are structural/synthetic nodes, for example:
  - **`client-created-root`** — synthetic root; no content; its single child is the real first message of the thread (which we do import).
  - **Other UUIDs with no `message`** — branch/structure-only nodes in the export with no displayable content.

So the only excluded links are from these synthetic nodes to real messages. We do **not** lose any user or assistant content. The app's canonical path walks `parent_id` on `messages` (leaf → root), not the children table, so display and threading still work. The script `scripts/sample_excluded_children.py` can be run against your export to reproduce these counts and sample excluded entries (set `MAX_CONV` and `MAX_SAMPLES` if needed).

**7. Custom instructions and memories**

The app does **not** import or display ChatGPT’s **custom instructions** or **memories** as first-class data. Reason:

- The **official ChatGPT export** (the zip you get from Settings → Data Controls → Export) does not appear to include a dedicated file for custom instructions or memories. The zip typically contains `conversations.json`, `chat.html`, `user.json`, `group_chats.json`, `message_feedback.json`, `shared_conversations.json`, `shopping.json`, etc. None of these are a dedicated “custom instructions” or “memories” export.
- We only read **`conversations.json`**. So even if OpenAI added a `custom_instructions.json` or `memories.json` in a future export, the current app would not load it unless we added support.
- If custom instructions or memory-like text are **embedded inside a conversation** (e.g. as a system message or a special message type in `conversations.json`), they would be imported as normal messages (we store all roles, including `system`, and `content.parts`). We don’t treat them as a separate “custom instructions” or “memories” section in the UI.

So: **custom instructions and memories are not exported by the system in a way we consume**, and we don’t have a dedicated place to show them. Any such content that appears inside a conversation’s messages will still be in the DB and visible in the thread.

**Limitation.** Custom instructions and memories are important user data and are worth exporting. The app would support importing and displaying them if OpenAI included them in the data export (e.g. a `custom_instructions.json` or `memories.json` in the zip). Until then, users who want this data preserved can request that OpenAI add it to the export format (e.g. via in-product feedback or support).

## Settings Management

### Available Settings

| Setting Key | Default Value | Description |
|-------------|---------------|-------------|
| `user_name` | "User" | Display name for user messages |
| `assistant_name` | "Assistant" | Display name for assistant messages |
| `dev_mode` | "false" | View mode (false=nice, true=dev) |
| `dark_mode` | "false" | Theme mode (false=light, true=dark) |
| `verbose_mode` | "false" | Show additional technical details |

### Settings Persistence

- Settings are stored in SQLite database
- Changes persist across application restarts
- Session overrides available for temporary changes

## View Modes

### Nice Mode (Default)

**Purpose**: Clean, focused conversation viewing

**Features**:
- Shows only canonical conversation path
- Hides technical metadata
- Clean, distraction-free interface
- Optimized for conversation review

**Implementation**:
```python
# Find canonical endpoint (message with no children)
canonical_endpoint = conn.execute('''
    SELECT m.id, m.role, m.content, m.create_time, m.parent_id
    FROM messages m
    LEFT JOIN messages child ON m.id = child.parent_id
    WHERE m.conversation_id = ? AND child.id IS NULL
    ORDER BY m.create_time DESC
    LIMIT 1
''', (conversation_id,)).fetchone()
```

### Dev Mode

**Purpose**: Full technical conversation analysis

**Features**:
- Shows all messages and branches
- Displays technical metadata
- Message IDs and timestamps
- Conversation tree structure
- Debugging information

**Implementation**:
```python
# Get all messages with metadata
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
```

## Error Handling

### Database Errors

- **Connection Management**: Proper connection cleanup
- **Transaction Rollback**: Automatic rollback on errors
- **Graceful Degradation**: Continue processing on partial failures

### Import Errors

- **File Validation**: Comprehensive file format checking
- **Data Validation**: Skip invalid records, continue processing
- **Error Logging**: Console output for debugging

### Web Errors

- **404 Handling**: Proper "not found" responses
- **400 Handling**: Bad request responses for invalid data
- **500 Handling**: Internal server error handling

## Security Considerations

### File Upload Security

- **File Type Validation**: Only accepts JSON files
- **Content Validation**: Validates JSON structure
- **Size Limits**: Implicit size limits through Flask configuration

### Session Security

- **Random Secret Key**: Generated using `os.urandom(24)`
- **Session Management**: Proper session cleanup
- **CSRF Protection**: Form-based protection

### Database Security

- **Parameterized Queries**: Prevents SQL injection
- **Input Validation**: Validates all user inputs
- **Error Information**: Limited error details in production

## Performance Optimizations

### Database Optimizations

- **Indexes**: Created on frequently queried columns
- **Connection Pooling**: Efficient database connection management
- **Query Optimization**: Optimized SQL queries for large datasets

### Frontend Optimizations

- **CSS Minification**: Optimized stylesheet delivery
- **Template Caching**: Jinja2 template caching
- **Static Asset Caching**: Browser caching for static files

### Memory Management

- **Connection Cleanup**: Proper database connection handling
- **Large File Handling**: Streaming file processing
- **Memory-Efficient Processing**: Processing large datasets in chunks

## Development Guidelines

### Code Style

- **PEP 8 Compliance**: Follow Python style guidelines
- **Docstrings**: Comprehensive function documentation
- **Type Hints**: Consider adding type hints for better IDE support

### Testing

- **Unit Tests**: Test individual functions and components
- **Integration Tests**: Test database operations and API endpoints
- **Manual Testing**: Test import functionality with real data

### Deployment

- **Production Configuration**: Disable debug mode
- **Database Backup**: Regular database backups
- **Logging**: Implement proper logging for production

### Future Enhancements

- **Search Functionality**: Full-text search across conversations
- **Export Features**: Export conversations in various formats
- **User Authentication**: Multi-user support
- **API Endpoints**: RESTful API for external integrations
- **Advanced Analytics**: Conversation analysis and insights

### Maintenance

- **Database Migrations**: Schema versioning and migration system
- **Dependency Updates**: Regular security and feature updates
- **Performance Monitoring**: Monitor application performance
- **Error Tracking**: Implement error tracking and alerting

---

*This documentation covers the complete technical implementation of the ChatGPT Browser application. For user-facing documentation, see the main README.md file.* 