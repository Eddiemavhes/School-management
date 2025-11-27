import sqlite3
import os

os.chdir('c:/Users/Admin/Desktop/School management')

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# Check all tables
print("=== ALL TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
for table in sorted(tables):
    print(f"  {table}")

print("\n=== PAYMENT-RELATED TABLES ===")
for table in tables:
    if 'payment' in table.lower() or 'balance' in table.lower() or 'fee' in table.lower():
        cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
        schema = cursor.fetchone()
        print(f"\n{table}:")
        print(schema[0])

print("\n=== PAYMENT DATA ===")
cursor.execute("SELECT * FROM core_payment LIMIT 10")
if cursor.description:
    columns = [desc[0] for desc in cursor.description]
    print("Columns:", columns)
    cursor.execute("SELECT * FROM core_payment")
    rows = cursor.fetchall()
    for row in rows:
        print(dict(zip(columns, row)))

conn.close()
