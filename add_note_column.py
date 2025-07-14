import sqlite3

conn = sqlite3.connect("glass_defects.db")
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE defects ADD COLUMN Note TEXT;")
    conn.commit()
    print("✅ 'Note' column added.")
except sqlite3.OperationalError as e:
    print("⚠️ Already exists or failed:", e)

conn.close()