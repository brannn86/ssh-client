"""Simple SQLite logger for sessions and events."""
import sqlite3
import os
from datetime import datetime


DB_PATH = 'zt_ssh.db'


def init_db():
    created = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    if created:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                host TEXT,
                start_time TEXT,
                end_time TEXT,
                status TEXT
            )
        ''')
        c.execute('''
            CREATE TABLE events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER,
                timestamp TEXT,
                event TEXT
            )
        ''')
        conn.commit()
    return conn


def log_session_start(user, host):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    start = datetime.utcnow().isoformat()
    c.execute('INSERT INTO sessions (user, host, start_time, status) VALUES (?, ?, ?, ?)', (user, host, start, 'active'))
    conn.commit()
    return c.lastrowid


def log_event(session_id, event_text):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ts = datetime.utcnow().isoformat()
    c.execute('INSERT INTO events (session_id, timestamp, event) VALUES (?, ?, ?)', (session_id, ts, event_text))
    conn.commit()