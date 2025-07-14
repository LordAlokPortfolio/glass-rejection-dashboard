import sqlite3

# Connect to the database
conn = sqlite3.connect("glass_defects.db")
cursor = conn.cursor()

# 🟡 Set your target Tag# here
tag_to_delete = "160744"  # Replace with the Tag# you want to delete
rowid_to_delete = None    # Optional: set to a specific rowid if you only want to delete one row

# 🔎 Show matches
if rowid_to_delete:
    cursor.execute("SELECT rowid, * FROM defects WHERE Tag = ? AND rowid = ?", (tag_to_delete, rowid_to_delete))
else:
    cursor.execute("SELECT rowid, * FROM defects WHERE Tag = ?", (tag_to_delete,))
rows = cursor.fetchall()

if not rows:
    print("⚠️ No matching rows found.")
else:
    print("🔎 Matching rows:")
    for r in rows:
        print(r)

    confirm = input(f"\n🗑 Delete {'rowid '+str(rowid_to_delete) if rowid_to_delete else 'ALL'} with Tag# {tag_to_delete}? (y/n): ").strip().lower()
    if confirm == "y":
        if rowid_to_delete:
            cursor.execute("DELETE FROM defects WHERE Tag = ? AND rowid = ?", (tag_to_delete, rowid_to_delete))
        else:
            cursor.execute("DELETE FROM defects WHERE Tag = ?", (tag_to_delete,))
        conn.commit()
        print("✅ Deleted successfully.")
    else:
        print("❌ Cancelled.")

conn.close()