import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'posthog.db'))


def get_connection():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            user_id   INTEGER PRIMARY KEY,
            login     TEXT NOT NULL,
            type      TEXT,
            is_bot    BOOLEAN DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS pull_requests (
            pr_id          INTEGER PRIMARY KEY,
            pr_number      INTEGER UNIQUE,
            author_user_id INTEGER,
            created_at     TEXT,
            merged_at      TEXT,
            closed_at      TEXT,
            state          TEXT,
            is_merged      BOOLEAN DEFAULT 0
        );
    ''')
    conn.commit()
    conn.close()
    print("Database initialized.")
