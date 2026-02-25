
import sqlite3

def list_categories():
    try:
        conn = sqlite3.connect('data/minimarket.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, name_ar FROM categories")
        rows = cursor.fetchall()
        print("Categories found:")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Name AR: {row[2]}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_categories()
