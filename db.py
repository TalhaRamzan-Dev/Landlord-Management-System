import sqlite3
import os
DB_FILE = "landlord.db"
SCHEMA_FILE = "schema.sql"

def init_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            with open(SCHEMA_FILE, 'r') as f:
                conn.executescript(f.read())
        print("Database initialized.")
    else:
        print("Database already exists.")

if __name__ == "__main__":
    init_db()