-- SPDX-License-Identifier: AGPL-3.0-only
-- ChatGPT Browser - https://github.com/actuallyrizzn/chatGPT-browser
-- Single source of truth for schema. Executed by app.init_db(). conversations.id is TEXT.

CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    create_time TEXT,
    update_time TEXT,
    title TEXT
);

CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT,
    role TEXT,
    content TEXT,
    create_time TEXT,
    update_time TEXT,
    parent_id TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id)
);

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
);

CREATE TABLE IF NOT EXISTS message_children (
    parent_id TEXT,
    child_id TEXT,
    PRIMARY KEY (parent_id, child_id),
    FOREIGN KEY (parent_id) REFERENCES messages(id),
    FOREIGN KEY (child_id) REFERENCES messages(id)
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT
);

INSERT OR IGNORE INTO settings (key, value) VALUES ('user_name', 'User');
INSERT OR IGNORE INTO settings (key, value) VALUES ('assistant_name', 'Assistant');
INSERT OR IGNORE INTO settings (key, value) VALUES ('dev_mode', 'false');
INSERT OR IGNORE INTO settings (key, value) VALUES ('dark_mode', 'false');
INSERT OR IGNORE INTO settings (key, value) VALUES ('verbose_mode', 'false');

DELETE FROM settings WHERE key = 'nice_mode';
