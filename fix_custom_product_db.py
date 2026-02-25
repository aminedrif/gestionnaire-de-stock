import sqlite3
import os

db_path = 'database/store.db'
if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Check if ID 0 exists
    cursor.execute("SELECT id FROM products WHERE id = 0")
    if cursor.fetchone():
        print("Product ID 0 already exists.")
    else:
        print("Creating Product ID 0 for Custom Items...")
        # Insert placeholder product
        # Ensure we satisfy NOT NULL constraints of products table
        # products(id, name, barcode, selling_price, stock_quantity, category_id, is_active)
        # We need to know the schema of products too, but usually name and price are required.
        cursor.execute("""
            INSERT INTO products (id, name, barcode, selling_price, stock_quantity, is_active)
            VALUES (0, 'Produit Personnalisé', 'CUSTOM', 0, 0, 1)
        """)
        conn.commit()
        print("Product ID 0 created successfully.")

    conn.close()
    
except Exception as e:
    print(f"Error fixing database: {e}")
