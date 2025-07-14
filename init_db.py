import sqlite3

conn = sqlite3.connect("glass_defects.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS defects (
    PO TEXT,
    Tag TEXT,
    Size TEXT,
    Quantity INTEGER,
    Scratch_Location TEXT,
    Scratch_Type TEXT,
    Glass_Type TEXT,
    Rack_Type TEXT,
    Vendor TEXT,
    Date TEXT,
    Note TEXT
)
""")

conn.commit()
conn.close()
