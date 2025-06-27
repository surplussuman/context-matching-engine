# DB connection & queries (placeholder for now)

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Setup DB connection
def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "edumatch"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASS", "password"),
        port=os.getenv("DB_PORT", "5432")
    )

# Initialize DB (create table if not exists)
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS transcripts (
            id SERIAL PRIMARY KEY,
            video_name TEXT NOT NULL,
            transcript TEXT,
            upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

# Insert transcript
def insert_transcript(video_name, transcript):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO transcripts (video_name, transcript, upload_time)
        VALUES (%s, %s, %s)
    """, (video_name, transcript, datetime.now()))
    conn.commit()
    cur.close()
    conn.close()


# Fetch all uploaded transcripts
def fetch_all_transcripts():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT video_name, transcript, upload_time FROM transcripts ORDER BY upload_time DESC")
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results
