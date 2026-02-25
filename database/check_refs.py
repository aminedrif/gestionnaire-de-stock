import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'minimarket.db')

def check_refs():
    print(f"Checking references in: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check all sql definitions for 'sales_old'
        cursor.execute("SELECT type, name, sql FROM sqlite_master WHERE sql LIKE '%sales_old%'")
        items = cursor.fetchall()
        
        if items:
            print(f"Found {len(items)} items referencing 'sales_old':")
            for type_, name, sql in items:
                print(f"[{type_}] {name}")
                print(f"SQL: {sql}")
                print("-" * 50)
                
                # Auto-fix: Drop the offending item
                print(f"Dropping {type_} {name}...")
                cursor.execute(f"DROP {type_} IF EXISTS {name}")
                
            conn.commit()
            print("Dropped all items referencing sales_old.")
        else:
            print("No items referencing 'sales_old' found in sqlite_master.")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_refs()
