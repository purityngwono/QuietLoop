import sqlite3
import datetime

DB_NAME = "quietloop.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Journal table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_number TEXT,
            entry_type TEXT,
            message TEXT,
            timestamp TEXT,
            topic TEXT,
            matched INTEGER DEFAULT 0
        )
    """)
    
    # User states table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_states (
            user_number TEXT PRIMARY KEY,
            state TEXT,
            updated_at TEXT
        )
    """)
    
    # User moods table (for returning user greeting)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_moods (
            user_number TEXT PRIMARY KEY,
            mood TEXT,
            updated_at TEXT
        )
    """)
    
    # Matches table (for anonymous connection)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_number TEXT,
            matched_user TEXT,
            their_message TEXT,
            reply TEXT,
            replied INTEGER DEFAULT 0,
            created_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database tables created successfully!")

# ===== JOURNAL FUNCTIONS =====
def save_entry(user_number, entry_type, message, dedupe_window=30):
    """Save entry with deduplication check"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check for duplicate within the last X seconds
    cursor.execute("""
        SELECT COUNT(*) FROM journal 
        WHERE user_number = ? 
        AND message = ? 
        AND timestamp > datetime('now', ?)
    """, (user_number, message, f"-{dedupe_window} seconds"))
    
    count = cursor.fetchone()[0]
    if count > 0:
        conn.close()
        return False # Duplicate, skip saving
    
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO journal (user_number, entry_type, message, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_number, entry_type, message, timestamp))
    conn.commit()
    conn.close()
    return True

def save_entry_with_topic(user_number, entry_type, message, topic):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO journal (user_number, entry_type, message, timestamp, topic)
        VALUES (?, ?, ?, ?, ?)
    """, (user_number, entry_type, message, timestamp, topic))
    conn.commit()
    conn.close()

def get_entries(user_number, days=None, specific_date=None):
    conn = get_connection()
    cursor = conn.cursor()
    
    if specific_date:
        cursor.execute("""
            SELECT timestamp, entry_type, message FROM journal
            WHERE user_number = ? AND DATE(timestamp) = ?
            ORDER BY timestamp DESC
        """, (user_number, specific_date))
    elif days is not None:
        cursor.execute("""
            SELECT timestamp, entry_type, message FROM journal
            WHERE user_number = ? AND DATE(timestamp) >= DATE('now', ?)
            ORDER BY timestamp DESC
        """, (user_number, f"-{days} days"))
    else:
        cursor.execute("""
            SELECT timestamp, entry_type, message FROM journal
            WHERE user_number = ?
            ORDER BY timestamp DESC
        """, (user_number,))
    
    entries = cursor.fetchall()
    conn.close()
    return entries

# ===== MATCHING FUNCTIONS =====
def find_match(user_number, topic):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_number, message FROM journal
        WHERE topic = ? AND user_number != ? AND matched = 0
        ORDER BY timestamp DESC LIMIT 1
    """, (topic, user_number))
    match = cursor.fetchone()
    conn.close()
    return match

def mark_matched(user_number, match_user):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE journal SET matched = 1
        WHERE user_number IN (?, ?)
    """, (user_number, match_user))
    conn.commit()
    conn.close()

# ===== USER STATE FUNCTIONS =====
def save_user_state(user_number, state):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_states (user_number, state, updated_at)
        VALUES (?, ?, ?)
    """, (user_number, state, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_user_state(user_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT state FROM user_states WHERE user_number = ?
    """, (user_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "start"

def get_all_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT user_number FROM user_states")
    users = cursor.fetchall()
    conn.close()
    return [u[0] for u in users]

# ===== MOOD FUNCTIONS (for returning user greeting) =====
def save_mood(user_number, mood_keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO user_moods (user_number, mood, updated_at)
        VALUES (?, ?, ?)
    """, (user_number, mood_keyword, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_mood(user_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT mood FROM user_moods WHERE user_number = ?
    """, (user_number,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

# ===== MATCH STORAGE FUNCTIONS =====
def save_match_sent(user_number, matched_user, their_message):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO matches (user_number, matched_user, their_message, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_number, matched_user, their_message, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    return cursor.lastrowid

def get_match(user_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, matched_user, their_message FROM matches
        WHERE user_number = ? AND replied = 0
        ORDER BY id DESC LIMIT 1
    """, (user_number,))
    result = cursor.fetchone()
    conn.close()
    return result

def save_reply(match_id, reply_text):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE matches SET reply = ?, replied = 1 WHERE id = ?
    """, (reply_text, match_id))
    conn.commit()
    conn.close()

    return [u[0] for u in users]
