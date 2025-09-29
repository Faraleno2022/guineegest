#!/usr/bin/env python3
"""
Script pour corriger les migrations en production PythonAnywhere
Exécute ce script dans la console Bash PythonAnywhere
"""

import os
import sys

# Ajouter le répertoire du projet au path
sys.path.append('/home/gestionnairedeparc/guineegest')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')

import django
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection

def fix_production_db():
    """Vérifie et corrige la base de données de production"""
    
    print("=== Vérification de la base de données ===")
    
    # Vérifier les tables existantes
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables existantes: {len(tables)}")
        
        # Vérifier la table Vehicule
        if 'fleet_app_vehicule' in tables:
            cursor.execute("PRAGMA table_info(fleet_app_vehicule);")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"Colonnes Vehicule: {columns}")
            
            if 'user_id' not in columns:
                print("❌ Colonne user_id manquante")
            else:
                print("✅ Colonne user_id présente")
                
            if 'entreprise_id' not in columns:
                print("❌ Colonne entreprise_id manquante")
            else:
                print("✅ Colonne entreprise_id présente")
        else:
            print("❌ Table fleet_app_vehicule manquante")
    
    print("\n=== Application des migrations ===")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations appliquées avec succès")
    except Exception as e:
        print(f"❌ Erreur migration: {e}")
        
        # Essayer fake-initial
        try:
            execute_from_command_line(['manage.py', 'migrate', '--fake-initial'])
            print("✅ Migrations fake-initial appliquées")
        except Exception as e2:
            print(f"❌ Erreur fake-initial: {e2}")

if __name__ == '__main__':
    fix_production_db()
