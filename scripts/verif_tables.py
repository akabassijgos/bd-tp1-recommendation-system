import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(users)")
print("TABLE : users")
print(cursor.fetchall())
print()

cursor.execute("PRAGMA table_info(movies)")
print("TABLE : movies")
print(cursor.fetchall())
print()

cursor.execute("PRAGMA table_info(ratings)")
print("TABLE : ratings")
print(cursor.fetchall())
print()

conn.close()
