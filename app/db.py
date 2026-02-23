from pathlib import Path
import sqlite3
import os

DB_PATH = Path(os.getenv("DATABASE_URL", "cars.db"))

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS brands (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS car_models (
        id TEXT PRIMARY KEY,
        brand_id TEXT NOT NULL,
        name TEXT NOT NULL,
        year INTEGER,
        FOREIGN KEY(brand_id) REFERENCES brands(id)
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS cars (
        id TEXT PRIMARY KEY,
        model_id TEXT NOT NULL,
        vin TEXT UNIQUE,
        color TEXT,
        price REAL,
        status TEXT,
        FOREIGN KEY(model_id) REFERENCES car_models(id)
    )
    """)
    conn.commit()
    conn.close()
