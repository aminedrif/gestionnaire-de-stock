
import sys
import os
sys.path.append(os.getcwd())
from modules.products.product_manager import product_manager

print("Attributes of product_manager:")
print(dir(product_manager))

try:
    print("Testing get_product_by_name...")
    p = product_manager.get_product_by_name("Produit Divers")
    print(f"Result: {p}")
except Exception as e:
    print(f"Error: {e}")
