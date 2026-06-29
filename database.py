import sqlite3
import datetime

DB_NAME = "quietloop.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
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
    conn.commit()
    conn.close()
    print("✅ Database tables created successfully!")

def save_entry(user_number, entry_type, message):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO journal (user_number, entry_type, message, timestamp)
        VALUES (?, ?, ?, ?)
    """, (user_number, entry_type, message, timestamp))
    conn.commit()
    conn.close()

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

    return entries
