import sqlite3
import os

# Check if db.sqlite3 exists and list all tables
db_path = 'db.sqlite3'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("All tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # Check for alerte-related tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%alerte%'")
    alerte_tables = cursor.fetchall()
    print(f"\nAlerte-related tables: {alerte_tables}")
    
    # Check if fleet_app_alerte exists and show its schema
    try:
        cursor.execute("PRAGMA table_info(fleet_app_alerte)")
        columns = cursor.fetchall()
        if columns:
            print("\nfleet_app_alerte table schema:")
            for col in columns:
                print(f"  {col[1]} ({col[2]})")
        else:
            print("\nfleet_app_alerte table does not exist")
    except Exception as e:
        print(f"\nError checking fleet_app_alerte: {e}")
    
    conn.close()
else:
    print(f"Database file {db_path} not found")
