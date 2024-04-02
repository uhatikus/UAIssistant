CREATE TABLE IF NOT EXISTS assistant_thread (
    id TEXT PRIMARY KEY,
    name TEXT,
    assistant_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
