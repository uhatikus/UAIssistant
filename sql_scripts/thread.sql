CREATE TABLE IF NOT EXISTS assistant_thread (
    id TEXT PRIMARY KEY,
    name TEXT,
    assistant_id TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
);

INSERT INTO assistant_thread (id, name, company_id, account_id, assistant_id, created_at)
VALUES ('thread_FJ0QyP5rbFd27XtlYyV2W6Za', 'Good Alex Chat', '15', '39', 'asst_3PmwJH8RiGCL908HrgZMh3x5', CURRENT_TIMESTAMP);
