import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='GlassDB@alok2613',  # <-- change to your real MySQL password
    database='glass_db'
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM defects LIMIT 15;")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()
