#!/usr/bin/env python
"""
Script pour créer manuellement la table ConfigurationSalaire
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db import connection

def create_configurationsalaire_table():
    """Créer la table ConfigurationSalaire manuellement"""
    with connection.cursor() as cursor:
        # Créer la table ConfigurationSalaire
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS "ConfigurationSalaire" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "statut_presence" varchar(50) NOT NULL DEFAULT 'P(Am_&_Pm)',
                "montant_journalier" decimal NOT NULL DEFAULT 0,
                "actif" bool NOT NULL DEFAULT 1,
                "employe_id" bigint NOT NULL REFERENCES "Employes" ("id") DEFERRABLE INITIALLY DEFERRED,
                "user_id" integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
            );
        """)
        
        # Créer l'index unique
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS "ConfigurationSalaire_employe_id_statut_presence_uniq" 
            ON "ConfigurationSalaire" ("employe_id", "statut_presence");
        """)
        
        # Créer les autres index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS "ConfigurationSalaire_employe_id_idx" 
            ON "ConfigurationSalaire" ("employe_id");
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS "ConfigurationSalaire_user_id_idx" 
            ON "ConfigurationSalaire" ("user_id");
        """)
        
        print("✅ Table ConfigurationSalaire créée avec succès!")

if __name__ == '__main__':
    create_configurationsalaire_table()
