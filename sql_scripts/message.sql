CREATE TABLE IF NOT EXISTS assistant_message (
    id TEXT PRIMARY KEY,
    assistant_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    role TEXT NOT NULL,
    type TEXT NOT NULL,
    content JSON
);

INSERT INTO assistant_message (id, assistant_id, thread_id, created_at, role, type, content)
VALUES
  ('1', 'asst_TODO', 'thread_TODO', CURRENT_TIMESTAMP, 'assistant', 'text', '{"message": "Hello, user! I am your assistant. What is your name?"}'),
  ('2', 'asst_TODO', 'thread_TODO', CURRENT_TIMESTAMP, 'user', 'text', '{"message": "Hello, Assistant! I am Alex."}'),
  ('3', 'asst_TODO', 'thread_TODO', CURRENT_TIMESTAMP, 'assistant', 'text', '{"message": "What would you like to do today?"}');
