#!/usr/bin/env python
import os
import django
import sqlite3

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.conf import settings

def add_montant_ferie_column():
    """Ajoute la colonne montant_ferie à la table ConfigurationsMontantsStatuts"""
    
    # Chemin vers la base de données SQLite
    db_path = settings.DATABASES['default']['NAME']
    
    try:
        # Connexion à la base de données
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Vérifier si la colonne existe déjà
        cursor.execute("PRAGMA table_info(ConfigurationsMontantsStatuts)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'montant_ferie' not in columns:
            print("Ajout de la colonne montant_ferie...")
            
            # Ajouter la colonne montant_ferie
            cursor.execute("""
                ALTER TABLE ConfigurationsMontantsStatuts 
                ADD COLUMN montant_ferie DECIMAL(15,2) DEFAULT 0
            """)
            
            conn.commit()
            print("✅ Colonne montant_ferie ajoutée avec succès!")
        else:
            print("✅ La colonne montant_ferie existe déjà.")
            
    except sqlite3.Error as e:
        print(f"❌ Erreur SQLite: {e}")
    except Exception as e:
        print(f"❌ Erreur: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_montant_ferie_column()
