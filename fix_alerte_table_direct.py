#!/usr/bin/env python
"""
Direct fix for missing fleet_app_alerte table.
Creates the table manually with correct schema.
"""
import sqlite3
import os

def create_alerte_table():
    """Create fleet_app_alerte table directly"""
    
    db_path = 'db.sqlite3'
    
    # Create database if it doesn't exist
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if table already exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fleet_app_alerte'")
    if cursor.fetchone():
        print("fleet_app_alerte table already exists")
        conn.close()
        return
    
    # Create the table with correct schema matching the Alerte model
    create_table_sql = """
    CREATE TABLE "fleet_app_alerte" (
        "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
        "titre" varchar(200) NOT NULL,
        "description" text NOT NULL,
        "niveau" varchar(20) NOT NULL,
        "vehicule_id" bigint NULL,
        "date_creation" datetime NOT NULL,
        "statut" varchar(20) NOT NULL,
        "resolution" text NULL,
        "date_resolution" datetime NULL,
        FOREIGN KEY ("vehicule_id") REFERENCES "fleet_app_vehicule" ("id_vehicule") DEFERRABLE INITIALLY DEFERRED
    )
    """
    
    try:
        cursor.execute(create_table_sql)
        print("✓ Created fleet_app_alerte table")
        
        # Create index for foreign key
        cursor.execute('CREATE INDEX "fleet_app_alerte_vehicule_id_idx" ON "fleet_app_alerte" ("vehicule_id")')
        print("✓ Created index for vehicule_id")
        
        conn.commit()
        
        # Verify table structure
        cursor.execute("PRAGMA table_info(fleet_app_alerte)")
        columns = cursor.fetchall()
        print(f"✓ Table created with {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
    except Exception as e:
        print(f"✗ Error creating table: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    create_alerte_table()
