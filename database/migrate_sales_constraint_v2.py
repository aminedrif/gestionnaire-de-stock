import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), 'data', 'minimarket.db')

def migrate_sales_constraint_v2():
    print(f"Migrating database (v2) at: {DB_PATH}")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("BEGIN TRANSACTION")
        
        # 1. Drop dependent views first
        print("Dropping dependent views...")
        cursor.execute("DROP VIEW IF EXISTS today_sales")
        cursor.execute("DROP VIEW IF EXISTS top_selling_products")
        
        # 2. Check and clean up existing tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        
        if 'sales_old' in tables:
             print("Found sales_old, assuming leftover. Drop checking...")
             cursor.execute("DROP TABLE IF EXISTS sales_old")
            
        # 3. Rename existing table
        print("Renaming existing table sales -> sales_old...")
        cursor.execute("ALTER TABLE sales RENAME TO sales_old")
        
        # 4. Create new table with updated constraint
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
        
        # 5. Copy data
        print("Copying data...")
        # Get column names to ensure mapping is correct
        cursor.execute("PRAGMA table_info(sales_old)")
        columns = [row[1] for row in cursor.fetchall()]
        col_str = ", ".join(columns)
        
        cursor.execute(f"INSERT INTO sales ({col_str}) SELECT {col_str} FROM sales_old")
        
        # 6. Verify count
        cursor.execute("SELECT COUNT(*) FROM sales_old")
        old_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sales")
        new_count = cursor.fetchone()[0]
        
        if old_count == new_count:
            print(f"Success! {new_count} records migrated.")
            # 7. Drop old table
            print("Dropping old table sales_old...")
            cursor.execute("DROP TABLE sales_old")
            
            # 8. Recreate indices
            print("Recreating indices...")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_number ON sales(sale_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_cashier ON sales(cashier_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_status ON sales(status)")
            
            # 9. Recreate Views
            print("Recreating views...")
            cursor.execute("""
            CREATE VIEW IF NOT EXISTS today_sales AS
            SELECT 
                s.id,
                s.sale_number,
                s.total_amount,
                s.payment_method,
                s.sale_date,
                u.full_name as cashier_name,
                c.full_name as customer_name
            FROM sales s
            LEFT JOIN users u ON s.cashier_id = u.id
            LEFT JOIN customers c ON s.customer_id = c.id
            WHERE date(s.sale_date) = date('now')
              AND s.status = 'completed';
            """)
            
            cursor.execute("""
            CREATE VIEW IF NOT EXISTS top_selling_products AS
            SELECT 
                p.id,
                p.name,
                p.name_ar,
                SUM(si.quantity) as total_quantity_sold,
                SUM(si.subtotal) as total_revenue,
                COUNT(DISTINCT si.sale_id) as number_of_sales
            FROM sale_items si
            JOIN products p ON si.product_id = p.id
            JOIN sales s ON si.sale_id = s.id
            WHERE s.status = 'completed'
            GROUP BY p.id, p.name, p.name_ar
            ORDER BY total_quantity_sold DESC;
            """)
            
            conn.commit()
            print("Migration v2 completed successfully.")
        else:
            print(f"Error: Count mismatch ({old_count} vs {new_count}). Rolling back.")
            conn.rollback()
            
    except Exception as e:
        print(f"Migration failed details: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_sales_constraint_v2()
