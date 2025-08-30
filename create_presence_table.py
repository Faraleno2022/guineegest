#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

import sqlite3
from django.conf import settings

def create_presence_table():
    """Create the PresenceJournaliere table directly in SQLite"""
    db_path = settings.DATABASES['default']['NAME']
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create PresenceJournaliere table
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS PresenceJournaliere (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        employe_id INTEGER NOT NULL,
        date DATE NOT NULL,
        present BOOLEAN DEFAULT 1,
        statut VARCHAR(50),
        user_id INTEGER,
        FOREIGN KEY (employe_id) REFERENCES Employes (id),
        FOREIGN KEY (user_id) REFERENCES auth_user (id),
        UNIQUE (employe_id, date)
    );
    """
    
    try:
        cursor.execute(create_table_sql)
        conn.commit()
        print("✅ Table PresenceJournaliere created successfully!")
        
        # Verify table exists
        cursor.execute("PRAGMA table_info(PresenceJournaliere)")
        columns = cursor.fetchall()
        print(f"📋 Table has {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"❌ Error creating table: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_presence_table()
