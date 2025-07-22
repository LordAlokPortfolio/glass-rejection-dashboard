import sqlite3
import csv

db_path = r"C:\Users\akulkarni\Glass Rejection Dashboard\glass-repo\glass_defects.db"
csv_path = r"C:\Users\akulkarni\Glass Rejection Dashboard\glass-repo\defects_export.csv"

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT * FROM defects")
rows = cursor.fetchall()

# Get column names
columns = [description[0] for description in cursor.description]

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(columns)  # write header
    writer.writerows(rows)    # write data rows

print(f"Exported {len(rows)} rows to {csv_path}")

conn.close()
