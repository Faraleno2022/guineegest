#!/usr/bin/env python
"""
Complete fix for fleet_app_alerte table issues.
Drops and recreates the table with exact Django ORM schema.
"""
import sqlite3
import os

def fix_alerte_table():
    """Drop and recreate fleet_app_alerte table with correct schema"""
    
    db_path = 'db.sqlite3'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Drop existing table if it exists
        cursor.execute("DROP TABLE IF EXISTS fleet_app_alerte")
        print("✓ Dropped existing fleet_app_alerte table")
        
        # Create table with exact Django schema
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
        
        cursor.execute(create_table_sql)
        print("✓ Created fleet_app_alerte table with correct schema")
        
        # Create index for foreign key
        cursor.execute('CREATE INDEX "fleet_app_alerte_vehicule_id_idx" ON "fleet_app_alerte" ("vehicule_id")')
        print("✓ Created vehicule_id index")
        
        conn.commit()
        
        # Verify table structure
        cursor.execute("PRAGMA table_info(fleet_app_alerte)")
        columns = cursor.fetchall()
        print(f"✓ Table verified with {len(columns)} columns:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
        # Test insert to verify schema works
        test_sql = """
        INSERT INTO fleet_app_alerte 
        (titre, description, niveau, date_creation, statut) 
        VALUES (?, ?, ?, datetime('now'), ?)
        """
        cursor.execute(test_sql, ('Test Alert', 'Test description', 'Moyen', 'Active'))
        print("✓ Test insert successful")
        
        # Remove test record
        cursor.execute("DELETE FROM fleet_app_alerte WHERE titre = 'Test Alert'")
        print("✓ Test record cleaned up")
        
        conn.commit()
        
    except Exception as e:
        print(f"✗ Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    fix_alerte_table()
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # Créer la table ConfigurationSalaire
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "ConfigurationSalaire" (
            "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
            "statut_presence" varchar(50) NOT NULL DEFAULT 'P(Am_&_Pm)',
            "montant_journalier" decimal NOT NULL DEFAULT 0,
            "actif" bool NOT NULL DEFAULT 1,
            "employe_id" bigint NOT NULL,
            "user_id" integer
        );
    ''')
    
    # Créer l'index unique
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS "ConfigurationSalaire_employe_statut_uniq" 
        ON "ConfigurationSalaire" ("employe_id", "statut_presence");
    ''')
    
    print("Table ConfigurationSalaire créée avec succès!")
