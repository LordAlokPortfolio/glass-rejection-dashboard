import sqlite3

conn = sqlite3.connect("glass_defects.db")
cursor = conn.cursor()

# 🔹 Ask user what they want to delete
mode = input("Delete by (1) Tag# or (2) rowid? Enter 1 or 2: ").strip()

if mode == "1":
    tag_input = input("Enter Tag# to delete: ").strip()
    cursor.execute("SELECT rowid, * FROM defects WHERE Tag = ?", (tag_input,))
elif mode == "2":
    rowid_input = input("Enter rowid to delete: ").strip()
    cursor.execute("SELECT rowid, * FROM defects WHERE rowid = ?", (rowid_input,))
else:
    print("❌ Invalid choice. Exiting.")
    conn.close()
    exit()

rows = cursor.fetchall()

if not rows:
    print("⚠️ No matching records found.")
    conn.close()
    exit()

# 🔍 Show matches
print("\n🔎 Matching records:")
for row in rows:
    print(row)

confirm = input("\n🗑 Are you sure you want to delete these rows? (y/n): ").strip().lower()
if confirm == "y":
    if mode == "1":
        cursor.execute("DELETE FROM defects WHERE Tag = ?", (tag_input,))
    else:
        cursor.execute("DELETE FROM defects WHERE rowid = ?", (rowid_input,))
    conn.commit()
    print("✅ Deleted successfully.")
else:
    print("❌ Cancelled.")

conn.close()
