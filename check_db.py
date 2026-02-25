import sqlite3

conn = sqlite3.connect('database/superette.db')
cursor = conn.execute("SELECT sql FROM sqlite_master WHERE name = 'cash_sessions'")
result = cursor.fetchone()
print("Current cash_sessions schema:")
print(result[0] if result else "Table does not exist")

# Check for postes
cursor = conn.execute("SELECT sql FROM sqlite_master WHERE name = 'postes'")
result = cursor.fetchone()
print("\nPostes table schema:")
print(result[0] if result else "Table does not exist")

# Check for cash_movements
cursor = conn.execute("SELECT sql FROM sqlite_master WHERE name = 'cash_movements'")
result = cursor.fetchone()
print("\nCash_movements table schema:")
print(result[0] if result else "Table does not exist")

conn.close()
