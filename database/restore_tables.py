import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'minimarket.db')

def restore_tables():
    print(f"Restoring tables in: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # Recreate sale_items
        print("Recreating sale_items...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER,
                
                product_name TEXT NOT NULL,
                barcode TEXT,
                
                quantity REAL NOT NULL,
                unit_price REAL NOT NULL,
                discount_percentage REAL DEFAULT 0.0,
                subtotal REAL NOT NULL,
                
                purchase_price REAL,
                
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_product ON sale_items(product_id)")
        
        # Recreate returns
        print("Recreating returns...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_number TEXT UNIQUE NOT NULL,
                original_sale_id INTEGER NOT NULL,
                
                return_amount REAL NOT NULL,
                refund_method TEXT DEFAULT 'cash',
                
                processed_by INTEGER NOT NULL,
                return_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                reason TEXT,
                
                FOREIGN KEY (original_sale_id) REFERENCES sales(id) ON DELETE CASCADE,
                FOREIGN KEY (processed_by) REFERENCES users(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_returns_number ON returns(return_number)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_returns_sale ON returns(original_sale_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_returns_date ON returns(return_date)")
        
        # Recreate return_items
        print("Recreating return_items...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS return_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_id INTEGER NOT NULL,
                sale_item_id INTEGER,
                product_id INTEGER,
                
                quantity REAL NOT NULL,
                refund_amount REAL NOT NULL,
                condition TEXT DEFAULT 'good', -- good, damaged, expired
                
                FOREIGN KEY (return_id) REFERENCES returns(id) ON DELETE CASCADE,
                FOREIGN KEY (sale_item_id) REFERENCES sale_items(id) ON DELETE SET NULL,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_return_items_return ON return_items(return_id)")
        
        # Recreate customer_credit_transactions
        print("Recreating customer_credit_transactions...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customer_credit_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                transaction_type TEXT CHECK(transaction_type IN ('credit_sale', 'payment', 'adjustment')),
                
                amount REAL NOT NULL,
                sale_id INTEGER, -- Si lié à une vente
                
                processed_by INTEGER NOT NULL,
                transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
                FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE SET NULL,
                FOREIGN KEY (processed_by) REFERENCES users(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_credit_trans_customer ON customer_credit_transactions(customer_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_credit_trans_date ON customer_credit_transactions(transaction_date)")
        
        conn.commit()
        print("Tables restored successfully with correct Foreign Keys.")
            
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    restore_tables()
