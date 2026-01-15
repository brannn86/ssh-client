"""Simple SQLite logger for sessions and events."""
import sqlite3

import os
from datetime import datetime, UTC


DB_PATH = 'zt_ssh.db'


def _now_iso():
    return datetime.now(UTC).isoformat()


def init_db():
    """Create DB and tables if missing and return a connection object."""
    created = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
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
        c.execute('''
            CREATE TABLE login_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user TEXT,
                host TEXT,
                port INTEGER,
                timestamp TEXT,
                status TEXT,
                reason TEXT
            )
        ''')
        conn.commit()
    else:
        # DB already exists; check if login_attempts table is missing and create it
        c = conn.cursor()
        try:
            c.execute('SELECT 1 FROM login_attempts LIMIT 1')
        except sqlite3.OperationalError:
            # Table doesn't exist, create it
            c.execute('''
                CREATE TABLE login_attempts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    host TEXT,
                    port INTEGER,
                    timestamp TEXT,
                    status TEXT,
                    reason TEXT
                )
            ''')
            conn.commit()
    return conn


def log_session_start(user, host):
    """Insert a new session row and return the session id."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    start = _now_iso()
    c.execute(
        'INSERT INTO sessions (user, host, start_time, status) VALUES (?, ?, ?, ?)',
        (user, host, start, 'active')
    )
    conn.commit()
    sid = c.lastrowid
    conn.close()
    return sid


def log_session_end(session_id, status='closed'):
    """Mark session end time and status."""
    if session_id is None:
        return
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    end = _now_iso()
    c.execute('UPDATE sessions SET end_time = ?, status = ? WHERE id = ?', (end, status, session_id))
    conn.commit()
    conn.close()


def log_event(session_id, event_text):
    """Insert an event (e.g., executed command) for a session."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ts = _now_iso()
    c.execute('INSERT INTO events (session_id, timestamp, event) VALUES (?, ?, ?)', (session_id, ts, event_text))
    conn.commit()
    conn.close()


def get_recent_sessions(limit=50):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, user, host, start_time, end_time, status FROM sessions ORDER BY start_time DESC LIMIT ?', (limit,))
    rows = c.fetchall()
    conn.close()
    return rows


def get_events_for_session(session_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, timestamp, event FROM events WHERE session_id = ? ORDER BY timestamp ASC', (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows


def log_login_attempt(user, host, port=22, status='success', reason=None):
    """Log a login attempt (success or failure) with optional reason."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    ts = _now_iso()
    c.execute(
        'INSERT INTO login_attempts (user, host, port, timestamp, status, reason) VALUES (?, ?, ?, ?, ?, ?)',
        (user, host, port, ts, status, reason)
    )
    conn.commit()
    conn.close()


def get_recent_login_attempts(limit=100):
    """Retrieve recent login attempts (successful and failed)."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'SELECT id, user, host, port, timestamp, status, reason FROM login_attempts ORDER BY timestamp DESC LIMIT ?',
        (limit,)
    )
    rows = c.fetchall()
    conn.close()
    return rows