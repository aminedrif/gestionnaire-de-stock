import sqlite3
import os

db_path = 'database/store.db'
if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE name='sale_items'")
    result = cursor.fetchone()
    if result:
        print(result[0])
    else:
        print("Table sale_items not found in sqlite_master")
except Exception as e:
    print(f"Error: {e}")
