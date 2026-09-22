import sqlite3
import os

DB_PATH = "schedule.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assignments (
            hebrew_year INTEGER,
            hebrew_month INTEGER,
            hebrew_day INTEGER,
            event_name TEXT,
            friday_night TEXT,
            shabbat_morning TEXT,
            seuda_shlishit TEXT,
            PRIMARY KEY (hebrew_year, hebrew_month, hebrew_day)
        )
    ''')
    conn.commit()
    conn.close()

def get_assignment(year, month, day):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT friday_night, shabbat_morning, seuda_shlishit 
        FROM assignments 
        WHERE hebrew_year=? AND hebrew_month=? AND hebrew_day=?
    ''', (year, month, day))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"friday_night": row[0], "shabbat_morning": row[1], "seuda_shlishit": row[2]}
    return None

def save_assignment(year, month, day, event_name, friday_night, shabbat_morning, seuda_shlishit):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO assignments 
        (hebrew_year, hebrew_month, hebrew_day, event_name, friday_night, shabbat_morning, seuda_shlishit) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (year, month, day, event_name, friday_night, shabbat_morning, seuda_shlishit))
    conn.commit()
    conn.close()
