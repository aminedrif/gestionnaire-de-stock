# -*- coding: utf-8 -*-
"""
Migration script for Caisse-Coffre redesign
Migrates from old user-based session model to new poste-based model
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "database" / "superette.db"

def migrate():
    print("Starting Caisse-Coffre migration...")
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        # Check if migration is needed
        cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'cash_sessions'")
        result = cursor.fetchone()
        
        if result and 'poste_id' in result[0]:
            print("Migration already completed - cash_sessions has poste_id")
            return True
        
        # 1. Create postes table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS postes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                name_ar TEXT,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert default poste
        cursor.execute("""
            INSERT OR IGNORE INTO postes (id, name, name_ar, description) VALUES 
            (1, 'Caisse Principale', 'الصندوق الرئيسي', 'Poste de caisse principal')
        """)
        
        # 2. Backup and recreate cash_sessions
        cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'cash_sessions'")
        old_schema = cursor.fetchone()
        
        if old_schema:
            print("Migrating cash_sessions table...")
            
            # Create backup
            cursor.execute("ALTER TABLE cash_sessions RENAME TO cash_sessions_backup")
            
            # Create new table
            cursor.execute("""
                CREATE TABLE cash_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    poste_id INTEGER NOT NULL DEFAULT 1,
                    opened_by INTEGER,
                    closed_by INTEGER,
                    
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    
                    start_amount REAL NOT NULL DEFAULT 0.0,
                    opening_source TEXT DEFAULT 'manual' CHECK(opening_source IN ('manual', 'safe')),
                    
                    cash_sales_total REAL DEFAULT 0.0,
                    theoretical_balance REAL DEFAULT 0.0,
                    counted_balance REAL DEFAULT 0.0,
                    difference REAL DEFAULT 0.0,
                    closing_method TEXT CHECK(closing_method IN ('counting', 'direct', NULL)),
                    
                    counting_details TEXT,
                    
                    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'closed')),
                    notes TEXT,
                    
                    FOREIGN KEY (poste_id) REFERENCES postes(id),
                    FOREIGN KEY (opened_by) REFERENCES users(id),
                    FOREIGN KEY (closed_by) REFERENCES users(id)
                )
            """)
            
            # Migrate data
            cursor.execute("""
                INSERT INTO cash_sessions 
                (id, poste_id, opened_by, start_time, end_time, start_amount, 
                 cash_sales_total, theoretical_balance, counted_balance, difference, status, notes)
                SELECT 
                    id, 1, user_id, start_time, end_time, start_amount,
                    cash_sales_total, theoretical_balance, 
                    COALESCE(real_balance, 0), difference, status, notes
                FROM cash_sessions_backup
            """)
            
            # Drop backup (optional - keep for safety)
            # cursor.execute("DROP TABLE cash_sessions_backup")
            print(f"Migrated {cursor.rowcount} sessions")
        else:
            # Create fresh table
            cursor.execute("""
                CREATE TABLE cash_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    poste_id INTEGER NOT NULL DEFAULT 1,
                    opened_by INTEGER,
                    closed_by INTEGER,
                    
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    
                    start_amount REAL NOT NULL DEFAULT 0.0,
                    opening_source TEXT DEFAULT 'manual' CHECK(opening_source IN ('manual', 'safe')),
                    
                    cash_sales_total REAL DEFAULT 0.0,
                    theoretical_balance REAL DEFAULT 0.0,
                    counted_balance REAL DEFAULT 0.0,
                    difference REAL DEFAULT 0.0,
                    closing_method TEXT CHECK(closing_method IN ('counting', 'direct', NULL)),
                    
                    counting_details TEXT,
                    
                    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'closed')),
                    notes TEXT,
                    
                    FOREIGN KEY (poste_id) REFERENCES postes(id),
                    FOREIGN KEY (opened_by) REFERENCES users(id),
                    FOREIGN KEY (closed_by) REFERENCES users(id)
                )
            """)
        
        # 3. Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_postes_active ON postes(is_active)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cash_sessions_status ON cash_sessions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cash_sessions_poste ON cash_sessions(poste_id)")
        
        # 4. Create cash_movements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cash_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id INTEGER NOT NULL,
                
                movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                movement_type TEXT NOT NULL CHECK(movement_type IN (
                    'sale', 'advance', 'correction_in',
                    'expense', 'refund', 'correction_out',
                    'transfer_out', 'transfer_in'
                )),
                
                amount REAL NOT NULL,
                description TEXT,
                
                requires_safe INTEGER DEFAULT 0,
                safe_approved INTEGER DEFAULT 0,
                
                sale_id INTEGER,
                created_by INTEGER,
                
                FOREIGN KEY (session_id) REFERENCES cash_sessions(id),
                FOREIGN KEY (sale_id) REFERENCES sales(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cash_movements_session ON cash_movements(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cash_movements_type ON cash_movements(movement_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cash_movements_date ON cash_movements(movement_date)")
        
        # 5. Update safe_transactions if needed
        cursor.execute("SELECT sql FROM sqlite_master WHERE name = 'safe_transactions'")
        safe_result = cursor.fetchone()
        
        if safe_result and 'movement_id' not in safe_result[0]:
            print("Adding movement_id column to safe_transactions...")
            try:
                cursor.execute("ALTER TABLE safe_transactions ADD COLUMN movement_id INTEGER REFERENCES cash_movements(id)")
            except:
                pass  # Column may already exist
        
        # 6. Add settings for thresholds
        cursor.execute("""
            INSERT OR IGNORE INTO settings (setting_key, setting_value, setting_type, description) VALUES
            ('expense_threshold', '10000', 'float', 'Seuil pour dépenses obligatoires via coffre (DA)'),
            ('safe_password', '', 'string', 'Mot de passe pour accès au coffre')
        """)
        
        conn.commit()
        print("Migration completed successfully!")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
