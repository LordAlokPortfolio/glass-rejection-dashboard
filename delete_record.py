import sqlite3

# ✅ Correct DB path on C drive
DB_PATH = r"C:\Users\akulkarni\Glass Rejection Dashboard\glass_defects.db"
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

tag_to_delete = input("Enter the Tag# of the record you want to delete: ").strip()

cursor.execute("SELECT * FROM defects WHERE Tag = ?", (tag_to_delete,))
rows = cursor.fetchall()

if not rows:
    print(f"No record found with Tag#: {tag_to_delete}")
else:
    confirm = input(f"Found {len(rows)} records. Confirm delete? (y/n): ").lower()
    if confirm == "y":
        cursor.execute("DELETE FROM defects WHERE Tag = ?", (tag_to_delete,))
        conn.commit()
        print(f"✅ Deleted {len(rows)} record(s) with Tag#: {tag_to_delete}")
    else:
        print("❌ Deletion cancelled.")

conn.close()
