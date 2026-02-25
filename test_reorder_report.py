from modules.reports.reorder_report import generate_reorder_report
import sys
import os

# Mock DB connection if needed or just rely on existing DB
# Assuming main.py initializes DB, we might need to do same here
from database.db_manager import db
# db is already initialized in db_manager.py

success, message = generate_reorder_report()
print(f"Success: {success}")
print(f"Message: {message}")
if success:
    # Check if file exists
    # Extract filename from message "Rapport généré: ..."
    filename = message.replace("Rapport généré: ", "")
    if os.path.exists(filename):
        print("File verified exists.")
    else:
        print("File not found.")
