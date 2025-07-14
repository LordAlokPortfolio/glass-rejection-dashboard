import sqlite3
import shutil
from datetime import datetime

DB_FILE = "glass_defects.db"

# 🔒 1. Automatic backup
backup_name = f"{DB_FILE.replace('.db','')}_backup_{datetime.now():%Y%m%d_%H%M%S}.db"
shutil.copyfile(DB_FILE, backup_name)
print(f"✅ Backup created → {backup_name}")

# 🔄 2. Connect and delete all rows
conn   = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("DELETE FROM defects;")
conn.commit()
conn.close()

print("🗑  All rows in 'defects' table deleted.")
