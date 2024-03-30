CREATE TABLE IF NOT EXISTS assistant (
    id TEXT PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    instructions TEXT,
    llmsource: TEXT,
    model TEXT,
);

INSERT INTO assistant (id, name, created_at, instructions, llmsource, model)
VALUES ('asst_TODO', 'Sample Alex Assistant', CURRENT_TIMESTAMP, 'Your a great assistant!', 'openai', 'gpt-4');
