import sqlite3

conn = sqlite3.connect(r"C:\Users\akulkarni\Glass Rejection Dashboard\glass-repo\glass_defects.db")
cursor = conn.cursor()

cursor.execute("SELECT rowid, * FROM defects LIMIT 17")
rows = cursor.fetchall()
for row in rows:
    print(row)

tags = cursor.fetchall()

print("All Tag# values in DB:")
for t in tags:
    print(f"'{t[0]}'")  # Shows exact content with quotes

conn.close()
