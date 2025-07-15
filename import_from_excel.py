import pandas as pd, sqlite3

# 1. Load Excel backup
df = pd.read_excel("glass_defects_backup_2025-07-14.xlsx")

# 2. Keep only valid DB columns
valid_cols = ['PO', 'Tag', 'Quantity', 'Scratch_Location', 'Scratch_Type',
              'Glass_Type', 'Rack_Type', 'Date', 'Size', 'Vendor', 'Note']
df = df[valid_cols]

# 3. Open DB connection
conn = sqlite3.connect("glass_defects.db")
cursor = conn.cursor()

# 4. OPTIONAL: Clear existing data
cursor.execute("DELETE FROM defects")
conn.commit()

# 5. Import to DB
df.to_sql("defects", conn, if_exists="append", index=False)
conn.commit()
conn.close()

print(f"✅ Restored {len(df)} records into glass_defects.db")
