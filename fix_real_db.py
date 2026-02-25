import sqlite3
import os

db_path = 'data/minimarket.db'
if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    # try looking in local dir just in case
    if os.path.exists('minimarket.db'):
        db_path = 'minimarket.db'

try:
    print(f"Connecting to {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='products'")
    if not cursor.fetchone():
        print("Error: Table 'products' not found!")
    else:
        # 1. Check if ID 0 exists
        cursor.execute("SELECT id FROM products WHERE id = 0")
        if cursor.fetchone():
            print("Product ID 0 already exists.")
        else:
            print("Creating Product ID 0 for Custom Items...")
            # Insert placeholder product
            cursor.execute("""
                INSERT INTO products (id, name, barcode, selling_price, stock_quantity, is_active)
                VALUES (0, 'Produit Personnalisé', 'CUSTOM', 0, 0, 1)
            """)
            conn.commit()
            print("Product ID 0 created successfully.")

    conn.close()
    
except Exception as e:
    print(f"Error fixing database: {e}")
