import sqlite3
import os

os.chdir('c:/Users/Admin/Desktop/School management')

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=== STUDENT BALANCE TABLE ===")
cursor.execute("SELECT * FROM core_studentbalance")
columns = [desc[0] for desc in cursor.description]
print("Columns:", columns)
rows = cursor.fetchall()
for row in rows:
    print(dict(zip(columns, row)))

print("\n=== CURRENT TERMS ===")
cursor.execute("SELECT id, name, year FROM core_academicterm ORDER BY id DESC LIMIT 5")
columns = [desc[0] for desc in cursor.description]
print("Columns:", columns)
for row in cursor.fetchall():
    print(dict(zip(columns, row)))

print("\n=== TERM FEES ===")
cursor.execute("SELECT t.id, t.name, tf.amount FROM core_academicterm t LEFT JOIN core_termfee tf ON t.id = tf.term_id ORDER BY t.id DESC")
columns = [desc[0] for desc in cursor.description]
for row in cursor.fetchall():
    print(dict(zip(columns, row)))

conn.close()
