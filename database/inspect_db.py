import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'minimarket.db')

def inspect_db():
    print(f"Inspecting database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tables found:")
        for t in tables:
            print(f"- {t[0]}")
            
            if t[0] in ['sales', 'sales_old']:
                cursor.execute(f"PRAGMA table_info({t[0]})")
                cols = cursor.fetchall()
                print(f"  Columns in {t[0]}:")
                for c in cols:
                    print(f"    - {c[1]} ({c[2]})")
                    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    inspect_db()
