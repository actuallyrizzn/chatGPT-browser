# ChatGPT Browser - Database Schema Documentation

## Overview

The ChatGPT Browser application uses SQLite3 as its database engine. The database is designed to store ChatGPT conversation data in a normalized structure that supports both simple conversation viewing and complex conversation tree analysis.

## Database File

- **File**: `chatgpt.db`
- **Engine**: SQLite3
- **Location**: Application root directory
- **Initialization**: Created by `init_db()` function in `app.py`

## Schema Overview

The database consists of 5 main tables:

1. **`conversations`** - Stores conversation metadata
2. **`messages`** - Stores individual messages
3. **`message_metadata`** - Stores technical metadata for messages
4. **`message_children`** - Manages parent-child relationships
5. **`settings`** - Stores application configuration

## Table Definitions

### 1. Conversations Table

**Purpose**: Stores high-level conversation information and metadata.

```sql
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,           -- ChatGPT conversation ID
    create_time TEXT,              -- Creation timestamp
    update_time TEXT,              -- Last update timestamp
    title TEXT                     -- Conversation title
);
```

**Columns**:
- `id`: Unique identifier from ChatGPT (Primary Key)
- `create_time`: Unix timestamp when conversation was created
- `update_time`: Unix timestamp when conversation was last updated
- `title`: Human-readable conversation title

**Data Types**:
- All timestamps are stored as TEXT to preserve precision
- IDs are stored as TEXT to maintain ChatGPT's ID format

**Sample Data**:
```sql
INSERT INTO conversations VALUES (
    'abc123-def456-ghi789',
    '1640995200.0',
    '1640995800.0',
    'How to implement a REST API'
);
```

### 2. Messages Table

**Purpose**: Stores individual messages within conversations.

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

**Columns**:
- `id`: Unique message identifier (Primary Key)
- `conversation_id`: References conversations.id (Foreign Key)
- `role`: Message author role ('user' or 'assistant')
- `content`: JSON-encoded message content parts
- `create_time`: Unix timestamp when message was created
- `update_time`: Unix timestamp when message was updated
- `parent_id`: ID of parent message for conversation threading

**Content Format**:
The `content` field stores JSON-encoded message parts:
```json
[
  {
    "type": "text",
    "text": "Hello, how can I help you today?"
  }
]
```

**Sample Data**:
```sql
INSERT INTO messages VALUES (
    'msg_123',
    'abc123-def456-ghi789',
    'assistant',
    '[{"type":"text","text":"Hello! How can I help you?"}]',
    '1640995200.0',
    '1640995200.0',
    NULL
);
```

### 3. Message Metadata Table

**Purpose**: Stores technical metadata and AI model information for messages.

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

**Columns**:
- `message_id`: References messages.id (Primary Key, Foreign Key)
- `message_type`: Type of message (e.g., 'text', 'code', 'image')
- `model_slug`: AI model identifier (e.g., 'gpt-4', 'gpt-3.5-turbo')
- `citations`: JSON array of citations and references
- `content_references`: JSON array of content references
- `finish_details`: JSON object with completion details
- `is_complete`: Boolean indicating if message generation is complete
- `request_id`: Unique request identifier
- `timestamp_`: Technical timestamp (note the underscore to avoid SQL keyword)
- `message_source`: Source of the message
- `serialization_metadata`: Additional serialization information

**Sample Data**:
```sql
INSERT INTO message_metadata VALUES (
    'msg_123',
    'text',
    'gpt-4',
    '[]',
    '[]',
    '{"type":"stop","stop_tokens":["<|endoftext|>"]}',
    1,
    'req_456',
    '1640995200.0',
    'chat.completion',
    '{}'
);
```

### 4. Message Children Table

**Purpose**: Manages parent-child relationships between messages for conversation threading.

```sql
CREATE TABLE message_children (
    parent_id TEXT,                -- Parent message ID
    child_id TEXT,                 -- Child message ID
    PRIMARY KEY (parent_id, child_id),
    FOREIGN KEY (parent_id) REFERENCES messages(id),
    FOREIGN KEY (child_id) REFERENCES messages(id)
);
```

**Columns**:
- `parent_id`: References messages.id (Part of Primary Key, Foreign Key)
- `child_id`: References messages.id (Part of Primary Key, Foreign Key)

**Purpose**:
This table enables the application to:
- Build conversation trees
- Find all branches of a conversation
- Identify canonical conversation paths
- Support conversation threading

**Sample Data**:
```sql
INSERT INTO message_children VALUES ('msg_123', 'msg_124');
INSERT INTO message_children VALUES ('msg_123', 'msg_125');
```

### 5. Settings Table

**Purpose**: Stores application configuration and user preferences.

```sql
CREATE TABLE settings (
    key TEXT PRIMARY KEY,          -- Setting key
    value TEXT                     -- Setting value
);
```

**Columns**:
- `key`: Setting identifier (Primary Key)
- `value`: Setting value as string

**Default Settings**:
```sql
INSERT OR IGNORE INTO settings (key, value) VALUES 
    ('user_name', 'User'),
    ('assistant_name', 'Assistant'),
    ('dev_mode', 'false'),         -- false = nice mode, true = dev mode
    ('dark_mode', 'false'),
    ('verbose_mode', 'false');
```

## Relationships

### Entity Relationship Diagram

```
conversations (1) ←→ (N) messages (1) ←→ (1) message_metadata
       ↑                                    ↑
       │                                    │
       └────────── (N) ←→ (N) ─────────────┘
              message_children
```

### Foreign Key Relationships

1. **messages.conversation_id** → **conversations.id**
   - Each message belongs to exactly one conversation
   - Cascade delete not implemented (manual cleanup required)

2. **message_metadata.message_id** → **messages.id**
   - Each message can have optional metadata
   - One-to-one relationship

3. **message_children.parent_id** → **messages.id**
   - Many-to-many relationship between messages
   - Enables conversation threading

4. **message_children.child_id** → **messages.id**
   - Many-to-many relationship between messages
   - Enables conversation threading

## Indexes

### Performance Indexes

```sql
-- Index on messages.conversation_id for fast conversation queries
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);

-- Index on messages.parent_id for fast parent-child queries
CREATE INDEX IF NOT EXISTS idx_messages_parent_id ON messages(parent_id);

-- Index on message_children.parent_id for fast child lookups
CREATE INDEX IF NOT EXISTS idx_message_children_parent_id ON message_children(parent_id);

-- Index on message_children.child_id for fast parent lookups
CREATE INDEX IF NOT EXISTS idx_message_children_child_id ON message_children(child_id);
```

### Index Usage

- **idx_messages_conversation_id**: Used when loading all messages for a conversation
- **idx_messages_parent_id**: Used when building conversation trees
- **idx_message_children_parent_id**: Used when finding all children of a message
- **idx_message_children_child_id**: Used when finding all parents of a message

## Data Flow

### Import Process

1. **File Upload**: JSON file uploaded via web interface
2. **Validation**: File content validated as valid JSON
3. **Conversation Processing**: Each conversation extracted and stored
4. **Message Processing**: Messages processed and relationships established
5. **Metadata Extraction**: Technical metadata extracted and stored
6. **Database Commit**: All changes committed to database

### Query Patterns

#### 1. Conversation List
```sql
SELECT id, title, create_time, update_time 
FROM conversations 
ORDER BY update_time DESC
```

#### 2. Full Conversation (Dev Mode)
```sql
SELECT m.*, 
       mm.message_type, mm.model_slug, mm.citations, mm.content_references,
       mm.finish_details, mm.is_complete, mm.request_id, mm.timestamp_,
       mm.message_source, mm.serialization_metadata
FROM messages m
LEFT JOIN message_metadata mm ON m.id = mm.message_id
WHERE m.conversation_id = ?
ORDER BY m.create_time
```

#### 3. Canonical Path (Nice Mode)
```sql
-- Find endpoint (message with no children)
SELECT m.id, m.role, m.content, m.create_time, m.parent_id
FROM messages m
LEFT JOIN messages child ON m.id = child.parent_id
WHERE m.conversation_id = ? AND child.id IS NULL
ORDER BY m.create_time DESC
LIMIT 1
```

#### 4. Message Tree Building
```sql
-- Get all children of a message
SELECT child_id FROM message_children WHERE parent_id = ?

-- Get all parents of a message
SELECT parent_id FROM message_children WHERE child_id = ?
```

## Data Types and Constraints

### Text Fields
- **IDs**: Stored as TEXT to preserve ChatGPT's ID format
- **Timestamps**: Stored as TEXT to maintain precision
- **JSON Data**: Stored as TEXT, parsed in application layer
- **Settings**: Stored as TEXT, converted to appropriate types in application

### Boolean Fields
- **is_complete**: Stored as INTEGER (0/1) in SQLite, converted to boolean in application

### Constraints
- **Primary Keys**: All tables have primary keys
- **Foreign Keys**: Proper foreign key relationships defined
- **NOT NULL**: Implicit for primary keys
- **UNIQUE**: Primary keys are unique by definition

## Database Operations

### Connection Management

```python
def get_db():
    """Create and return a database connection with Row factory."""
    conn = sqlite3.connect('chatgpt.db')
    conn.row_factory = sqlite3.Row
    return conn
```

### Transaction Management

```python
# Example transaction pattern
conn = get_db()
try:
    # Database operations
    conn.commit()
except:
    conn.rollback()
    raise
finally:
    conn.close()
```

### Parameterized Queries

All database queries use parameterized statements to prevent SQL injection:

```python
# Good: Parameterized query
conn.execute('SELECT * FROM messages WHERE conversation_id = ?', (conversation_id,))

# Bad: String formatting (vulnerable to SQL injection)
conn.execute(f'SELECT * FROM messages WHERE conversation_id = "{conversation_id}"')
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
cp chatgpt.db chatgpt.db.backup

# Restore from backup
cp chatgpt.db.backup chatgpt.db
```

### Database Reset

```python
# Reset database (removes all data)
import os
if os.path.exists('chatgpt.db'):
    os.remove('chatgpt.db')
init_db()
```

## Performance Considerations

### Query Optimization

1. **Use Indexes**: All frequently queried columns are indexed
2. **Limit Results**: Use LIMIT clauses for large result sets
3. **Efficient Joins**: Use LEFT JOIN only when necessary
4. **Connection Pooling**: Proper connection management

### Memory Management

1. **Row Factory**: Use sqlite3.Row for efficient data access
2. **Streaming**: Process large datasets in chunks
3. **Cleanup**: Always close database connections

### Storage Optimization

1. **JSON Compression**: Consider compressing large JSON fields
2. **Data Archival**: Archive old conversations if needed
3. **Database Vacuum**: Periodically run VACUUM to reclaim space

## Migration Strategy

### Schema Changes

When making schema changes:

1. **Backup Database**: Always backup before changes
2. **Version Tracking**: Track schema versions
3. **Migration Scripts**: Create migration scripts for schema changes
4. **Data Validation**: Validate data after migrations

### Example Migration

```python
def migrate_schema():
    conn = get_db()
    try:
        # Add new column
        conn.execute('ALTER TABLE messages ADD COLUMN new_field TEXT')
        conn.commit()
    except sqlite3.OperationalError:
        # Column might already exist
        pass
    finally:
        conn.close()
```

## Monitoring and Maintenance

### Database Health Checks

```python
def check_database_health():
    conn = get_db()
    try:
        # Check table integrity
        result = conn.execute('PRAGMA integrity_check').fetchone()
        return result[0] == 'ok'
    finally:
        conn.close()
```

### Performance Monitoring

```python
def get_database_stats():
    conn = get_db()
    try:
        stats = {
            'conversations': conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0],
            'messages': conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0],
            'metadata': conn.execute('SELECT COUNT(*) FROM message_metadata').fetchone()[0],
            'relationships': conn.execute('SELECT COUNT(*) FROM message_children').fetchone()[0]
        }
        return stats
    finally:
        conn.close()
```

---

*This database schema documentation provides comprehensive information about the data structure and relationships in the ChatGPT Browser application.* 