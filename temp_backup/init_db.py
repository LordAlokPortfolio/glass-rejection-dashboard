import sqlite3

# Set your target path
conn = sqlite3.connect(r"C:\Users\akulkarni\Glass Rejection Dashboard\glass_defects.db")
cursor = conn.cursor()

# Create table with correct structure (includes Size column)
cursor.execute("""
CREATE TABLE IF NOT EXISTS defects (
    PO TEXT,
    Tag TEXT,
    Size TEXT,
    Quantity INTEGER,
    Scratch_Location TEXT,
    Scratch_Type TEXT,
    Glass_Type TEXT,
    Vendor TEXT,
    Rack_Type TEXT,
    Date TEXT
)
""")

conn.commit()
conn.close()

print("✅ glass_defects.db created with correct table structure.")