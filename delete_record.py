import sqlite3
import os

conn = sqlite3.connect(r"C:\Users\akulkarni\Glass Rejection Dashboard\glass-repo\glass_defects.db")
cursor = conn.cursor()

print("Using DB file at:", os.path.abspath(conn.execute("PRAGMA database_list").fetchone()[2]))

while True:
    mode = input("\nDelete by (1) Tag or (2) rowid? Enter 1 or 2 (or 'q' to quit): ").strip().lower()
    if mode == 'q':
        print("Exiting.")
        break

    if mode == "1":
        tag_input = input("Enter Tag to delete (or 'q' to quit): ").strip()
        if tag_input.lower() == 'q':
            print("Exiting.")
            break
        cursor.execute('SELECT rowid, * FROM defects WHERE LOWER(TRIM("Tag")) = LOWER(TRIM(?))', (tag_input,))
    elif mode == "2":
        rowid_input = input("Enter rowid to delete (or 'q' to quit): ").strip()
        if rowid_input.lower() == 'q':
            print("Exiting.")
            break
        cursor.execute("SELECT rowid, * FROM defects WHERE rowid = ?", (rowid_input,))
    else:
        print("❌ Invalid choice. Please enter 1, 2 or q.")
        continue

    rows = cursor.fetchall()

    if not rows:
        print("⚠️ No matching records found.")
        continue

    print("\n🔎 Matching records:")
    for row in rows:
        print(row)

    confirm = input("\n🗑 Are you sure you want to delete these rows? (y/n): ").strip().lower()
    if confirm == "y":
        if mode == "1":
            cursor.execute('DELETE FROM defects WHERE LOWER(TRIM("Tag")) = LOWER(TRIM(?))', (tag_input,))
        else:
            cursor.execute("DELETE FROM defects WHERE rowid = ?", (rowid_input,))
        conn.commit()
        print("✅ Deleted successfully.")
    else:
        print("❌ Cancelled.")

conn.close()
