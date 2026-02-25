
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from modules.sales.pos import pos_manager
from modules.products.product_manager import product_manager
from database.db_manager import db

def test_fix():
    print("Testing add_to_cart with product_id=0...")
    
    # 1. Ensure "Produit Divers" doesn't exist or is clean (optional, but let's just see if it creates/finds it)
    # We won't delete it to avoid messing up live data too much, just checking if it WORKS.
    
    # 2. Add custom item
    success, msg = pos_manager.add_to_cart(0, 1, 150.0, "Test Divers Item")
    
    if not success:
        print(f"FAILED to add to cart: {msg}")
        return
        
    print(f"Successfully added to cart: {msg}")
    
    # 3. Verify item in cart has valid ID
    cart_items = pos_manager.get_cart().items
    if not cart_items:
        print("FAILED: Cart is empty!")
        return
        
    item = cart_items[-1]
    print(f"Cart Item: ID={item.product_id}, Name={item.product_name}, Price={item.unit_price}")
    
    if item.product_id <= 0:
        print("FAILED: Product ID is still negative or zero!")
    else:
        print("SUCCESS: Product ID is positive (valid DB ID).")
        
        # Verify in DB
        prod = product_manager.get_product(item.product_id)
        if prod:
            print(f"Verified in DB: {prod['name']} (ID: {prod['id']})")
        else:
            print("FAILED: Product ID not found in DB!")

    # 4. Verify category "Divers"
    cat = db.fetch_one("SELECT * FROM categories WHERE name='Divers'")
    if cat:
        print(f"Verified Category 'Divers': ID={cat['id']}")
    else:
        print("FAILED: Category 'Divers' missing!")

if __name__ == "__main__":
    try:
        test_fix()
    except Exception as e:
        print(f"CRASHED: {e}")
        import traceback
        traceback.print_exc()
