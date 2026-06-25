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
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

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
