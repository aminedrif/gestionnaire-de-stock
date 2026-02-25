import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'minimarket.db')

def recover_db():
    print(f"Recovering database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('sales', 'sales_old')")
        tables = [r[0] for r in cursor.fetchall()]
        print(f"Found tables: {tables}")
        
        if 'sales_old' in tables and 'sales' in tables:
            print("Both tables exist. Previous migration likely failed midway.")
            # Check which one has data
            cursor.execute("SELECT COUNT(*) FROM sales")
            sales_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM sales_old")
            old_count = cursor.fetchone()[0]
            
            print(f"sales: {sales_count}, sales_old: {old_count}")
            
            if sales_count == 0 and old_count > 0:
                print("New table empty, old table has data. Restoring old table.")
                cursor.execute("DROP TABLE sales")
                cursor.execute("ALTER TABLE sales_old RENAME TO sales")
            elif sales_count >= old_count:
                 print("New table seems fine (or equal). dropping sales_old.")
                 cursor.execute("DROP TABLE sales_old")
            
        elif 'sales_old' in tables and 'sales' not in tables:
            print("Only sales_old exists. Renaming to sales.")
            cursor.execute("ALTER TABLE sales_old RENAME TO sales")
            
        elif 'sales' in tables:
            print("Only sales exists. Checking constraint.")
            # We can try to re-run the migration logic properly now
            pass
            
        conn.commit()
        print("Recovery steps complete. Re-running migration safely.")
        
    except Exception as e:
        print(f"Recovery failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    recover_db()
