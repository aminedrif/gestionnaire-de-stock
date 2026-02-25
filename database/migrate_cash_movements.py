import sqlite3
import os

def migrate():
    print("Migrating database: Adding cash_movements and settings tables...")
    
    # Correct path resolution to data/minimarket.db
    base_dir = os.path.dirname(os.path.abspath(__file__)) # database/
    project_root = os.path.dirname(base_dir) # root
    db_path = os.path.join(project_root, "data", "minimarket.db")

    print(f"Target DB: {db_path}")

    if not os.path.exists(db_path):
        print("Error: Database file not found!")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Create cash_movements table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cash_movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            transaction_type VARCHAR(50) NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES cash_sessions(id)
        )
        """)
        print("Table 'cash_movements' checked/created.")

        # Create settings table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)
        print("Table 'settings' checked/created.")
        
        conn.commit()
        print("Migration successful.")
        
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
