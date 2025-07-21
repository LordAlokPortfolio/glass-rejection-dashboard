import sqlite3

conn   = sqlite3.connect("glass_defects.db")
cursor = conn.cursor()

# 1) Create the table if it doesn't exist yet
cursor.execute("""
CREATE TABLE IF NOT EXISTS defects (
    PO             TEXT,
    Tag            TEXT,
    Size           TEXT,
    Quantity       INTEGER,
    Scratch_Location TEXT,
    Scratch_Type   TEXT,
    Glass_Type     TEXT,
    Rack_Type      TEXT,
    Vendor         TEXT,
    Date           TEXT,
    Note           TEXT
)
""")

# 2) Ensure the ImageData BLOB column is present
cursor.execute("PRAGMA table_info(defects)")
existing_cols = [row[1] for row in cursor.fetchall()]
if "ImageData" not in existing_cols:
    cursor.execute("ALTER TABLE defects ADD COLUMN ImageData BLOB")

conn.commit()
conn.close()

