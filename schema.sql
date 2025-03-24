-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    update_time TIMESTAMP,
    voice TEXT,
    plugin_ids TEXT,
    safe_urls TEXT,
    moderation_results TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id INTEGER,
    author_name TEXT,
    author_role TEXT,
    author_metadata TEXT,
    content_type TEXT,
    content_parts TEXT,
    create_time TIMESTAMP,
    update_time TIMESTAMP,
    status TEXT,
    channel TEXT,
    weight REAL,
    end_turn BOOLEAN,
    parent_id TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id),
    FOREIGN KEY (parent_id) REFERENCES messages(id)
);

-- Create message metadata table
CREATE TABLE IF NOT EXISTS message_metadata (
    message_id TEXT PRIMARY KEY,
    citations TEXT,
    content_references TEXT,
    default_model_slug TEXT,
    finish_details TEXT,
    is_complete BOOLEAN,
    message_type TEXT,
    model_slug TEXT,
    parent_id TEXT,
    request_id TEXT,
    timestamp_ TEXT,
    message_source TEXT,
    serialization_metadata TEXT,
    FOREIGN KEY (message_id) REFERENCES messages(id)
);

-- Create message children relationships table
CREATE TABLE IF NOT EXISTS message_children (
    parent_id TEXT,
    child_id TEXT,
    PRIMARY KEY (parent_id, child_id),
    FOREIGN KEY (parent_id) REFERENCES messages(id),
    FOREIGN KEY (child_id) REFERENCES messages(id)
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_parent_id ON messages(parent_id);
CREATE INDEX IF NOT EXISTS idx_message_children_parent_id ON message_children(parent_id);
CREATE INDEX IF NOT EXISTS idx_message_children_child_id ON message_children(child_id); 