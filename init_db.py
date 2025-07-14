import sqlite3
import os

# Set DB path
DB_PATH = r"C:\Users\akulkarni\Glass Rejection Dashboard\glass_defects.db"

# Optional: ensure images folder exists
IMG_DIR = r"C:\Users\akulkarni\Glass Rejection Dashboard\images"
os.makedirs(IMG_DIR, exist_ok=True)

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Create table with all updated fields including Vendor
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
    Date TEXT
)
""")

conn.commit()
conn.close()

print("✅ glass_defects.db created with all required columns including Vendor.")
