import sqlite3

conn = sqlite3.connect(r"C:\Users\akulkarni\Glass Rejection Dashboard\glass-repo\glass_defects.db")
cursor = conn.cursor()

# Start a transaction
cursor.execute("BEGIN TRANSACTION;")

# 1. Create a new table with the same schema (adjust schema if needed)
cursor.execute("""
CREATE TABLE defects_new AS
SELECT * FROM defects
ORDER BY rowid;
""")

# 2. Drop the old table
cursor.execute("DROP TABLE defects;")

# 3. Rename new table to old name
cursor.execute("ALTER TABLE defects_new RENAME TO defects;")

conn.commit()
conn.close()

print("✅ Rowids reset successfully.")
