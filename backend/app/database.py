import sqlite3
from datetime import datetime

DB_NAME = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            date TEXT,
            time TEXT
        )
    """)

    conn.commit()
    conn.close()


# ✅ FIXED FUNCTION (auto time + duplicate prevention)
def mark_attendance(name):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    from datetime import datetime
    now = datetime.now()

    today = now.strftime("%Y-%m-%d")
    current_time = now.strftime("%H:%M:%S")

    # ✅ Check if already marked today
    c.execute("""
        SELECT * FROM attendance
        WHERE name=? AND date=?
    """, (name, today))

    exists = c.fetchone()

    if not exists:
        c.execute("""
            INSERT INTO attendance (name, date, time)
            VALUES (?, ?, ?)
        """, (name, today, current_time))

    conn.commit()
    conn.close()