import sqlite3
import pandas as pd
import os

DB_PATH = "glass_defects.db"
CSV_PATH = "defects_data.csv"

conn = sqlite3.connect(DB_PATH)
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
    Date TEXT
)
""")

df = pd.read_sql_query("SELECT * FROM defects", conn)
if df.empty and os.path.exists(CSV_PATH):
    csv_df = pd.read_csv(CSV_PATH)
    csv_df.to_sql("defects", conn, if_exists="append", index=False)
    print("✅ Clean CSV data loaded.")
else:
    print("✅ Database already populated.")

conn.commit()
conn.close()
