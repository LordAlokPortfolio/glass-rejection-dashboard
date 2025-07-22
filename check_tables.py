import sqlite3

conn = sqlite3.connect(r"C:\Users\akulkarni\Glass Rejection Dashboard\glass-repo\glass_defects.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in DB:", tables)

conn.close()
