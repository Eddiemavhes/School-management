import sqlite3
import os

os.chdir('c:/Users/Admin/Desktop/School management')

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Get table schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='core_student'")
schema = cursor.fetchone()
print("=== STUDENT TABLE SCHEMA ===")
print(schema[0] if schema else "Table not found")
print()

# Get all student data
cursor.execute("SELECT * FROM core_student LIMIT 5")
columns = [desc[0] for desc in cursor.description]
print("=== COLUMNS ===")
print(columns)
print()

print("=== STUDENT DATA ===")
cursor.execute("SELECT * FROM core_student")
rows = cursor.fetchall()
for row in rows:
    print(dict(zip(columns, row)))

conn.close()
