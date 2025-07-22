import sqlite3

# Change this to your backup file path
backup_db_path = r"C:\Users\akulkarni\Glass Rejection Dashboard\glass-repo\glass_defects.db"

conn = sqlite3.connect(backup_db_path)
cursor = conn.cursor()

# List all tables in the DB
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables in DB:", cursor.fetchall())

# Show schema of defects table (columns info)
cursor.execute("PRAGMA table_info(defects);")
schema = cursor.fetchall()
print("\nSchema of defects table:")
for col in schema:
    print(col)

# Count rows in defects table
cursor.execute("SELECT COUNT(*) FROM defects;")
count = cursor.fetchone()[0]
print(f"\nNumber of records in defects: {count}")

conn.close()
