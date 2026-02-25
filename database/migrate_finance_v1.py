import sqlite3
import os
import sys

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
sys.path.insert(0, project_root)

# from config import DB_NAME
DB_NAME = "minimarket.db"

def migrate_finance_tables():
    db_path = os.path.join(project_root, 'data', DB_NAME)
    print(f"Migrating finance tables in: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 1. Create cash_sessions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cash_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            
            start_amount REAL NOT NULL DEFAULT 0.0,  -- Fond de caisse initial
            cash_sales_total REAL DEFAULT 0.0,       -- Ventes espèces pendant la session
            theoretical_balance REAL DEFAULT 0.0,    -- start + sales
            real_balance REAL DEFAULT 0.0,           -- Montant constaté
            difference REAL DEFAULT 0.0,             -- real - theoretical
            
            status TEXT DEFAULT 'open' CHECK(status IN ('open', 'closed')),
            notes TEXT,
            
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """)
        print("- Created table: cash_sessions")
        
        # 2. Create safe_transactions table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS safe_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            amount REAL NOT NULL,                    -- Positif = Entrée, Négatif = Sortie
            transaction_type TEXT NOT NULL,          -- 'deposit', 'withdrawal', 'transfer_from_caisse', 'supplier_payment'
            
            description TEXT,
            session_id INTEGER,                      -- Lien si transfert caisse
            supplier_id INTEGER,                     -- Lien si paiement fournisseur
            
            created_by INTEGER,
            
            FOREIGN KEY (session_id) REFERENCES cash_sessions(id),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(id),
            FOREIGN KEY (created_by) REFERENCES users(id)
        )
        """)
        print("- Created table: safe_transactions")
        
        # 3. Create index for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_cash_sessions_status ON cash_sessions(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_safe_trans_date ON safe_transactions(transaction_date)")
        
        conn.commit()
        print("Migration Finance completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_finance_tables()
