CREATE TABLE IF NOT EXISTS assistant_message (
    id TEXT PRIMARY KEY,
    assistant_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role TEXT NOT NULL,
    type TEXT NOT NULL,
    content JSON
);
