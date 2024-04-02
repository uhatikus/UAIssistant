CREATE TABLE IF NOT EXISTS assistant (
    id TEXT PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    instructions TEXT,
    llmsource TEXT,
    model TEXT
);
