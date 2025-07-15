import pandas as pd, sqlite3

# 1. Load Excel backup
df = pd.read_excel("glass_defects_backup_2025-07-14.xlsx")

# 2. Open connection to DB
conn = sqlite3.connect("glass_defects.db")
cursor = conn.cursor()

# 3. OPTIONAL: Clear current table
cursor.execute("DELETE FROM defects")
conn.commit()

# 4. Insert all rows into 'defects' table
df.to_sql("defects", conn, if_exists="append", index=False)
conn.commit()
conn.close()

print(f"✅ Restored {len(df)} records into glass_defects.db")