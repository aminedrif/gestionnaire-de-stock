import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'minimarket.db')

def migrate_sales_constraint():
    print(f"Migrating database at: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Rename existing table
        print("Renaming existing table...")
        cursor.execute("ALTER TABLE sales RENAME TO sales_old")
        
        # 2. Create new table with updated constraint
        print("Creating new sales table...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_number TEXT UNIQUE NOT NULL,
                customer_id INTEGER,
                cashier_id INTEGER NOT NULL,
                subtotal REAL NOT NULL DEFAULT 0.0,
                discount_amount REAL DEFAULT 0.0,
                tax_amount REAL DEFAULT 0.0,
                total_amount REAL NOT NULL,
                payment_method TEXT DEFAULT 'cash' CHECK(payment_method IN ('cash', 'card', 'credit', 'mixed')),
                amount_paid REAL DEFAULT 0.0,
                change_amount REAL DEFAULT 0.0,
                register_number INTEGER DEFAULT 1,
                status TEXT DEFAULT 'completed' CHECK(status IN ('completed', 'returned', 'cancelled')),
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
                FOREIGN KEY (cashier_id) REFERENCES users(id)
            )
        """)
        
        # 3. Copy data
        print("Copying data...")
        # Get column names to ensure mapping is correct
        cursor.execute("PRAGMA table_info(sales_old)")
        columns = [row[1] for row in cursor.fetchall()]
        col_str = ", ".join(columns)
        
        cursor.execute(f"INSERT INTO sales ({col_str}) SELECT {col_str} FROM sales_old")
        
        # 4. Verify count
        cursor.execute("SELECT COUNT(*) FROM sales_old")
        old_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sales")
        new_count = cursor.fetchone()[0]
        
        if old_count == new_count:
            print(f"Success! {new_count} records migrated.")
            # 5. Drop old table
            print("Dropping old table...")
            cursor.execute("DROP TABLE sales_old")
            
            # Recreate indices
            print("Recreating indices...")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_number ON sales(sale_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_cashier ON sales(cashier_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_status ON sales(status)")
            
            conn.commit()
            print("Migration completed successfully.")
        else:
            print(f"Error: Count mismatch ({old_count} vs {new_count}). Rolling back.")
            conn.rollback()
            
    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_sales_constraint()
