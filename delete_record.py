import sqlite3

# Connect to DB
conn = sqlite3.connect("glass_defects.db")
cursor = conn.cursor()

# Find duplicate Tag#s (keep the one with MIN(rowid))
cursor.execute("""
    DELETE FROM defects
    WHERE rowid NOT IN (
        SELECT MIN(rowid)
        FROM defects
        GROUP BY Tag
    )
""")

conn.commit()
print("✅ Duplicate rows deleted based on Tag# (keeping first entry only).")
conn.close()
