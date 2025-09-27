#!/usr/bin/env python
"""
Script pour corriger directement la base de données SQLite
"""
import sqlite3
import os

def fix_database():
    """Corriger la base de données directement"""
    db_path = "db.sqlite3"
    
    if not os.path.exists(db_path):
        print("✗ Base de données non trouvée")
        return False
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables à corriger
    tables = [
        'fleet_app_vehicule',
        'fleet_app_chauffeur',
        'fleet_app_feuillederroute',
        'fleet_app_alerte',
        'fleet_app_coutfonctionnement',
        'fleet_app_coutfinancier',
        'fleet_app_utilisationvehicule',
        'fleet_app_distanceparcourue',
        'fleet_app_consommationcarburant',
        'fleet_app_disponibilitevehicule',
        'fleet_app_utilisationactif',
        'fleet_app_incidentsecurite'
    ]
    
    for table in tables:
        try:
            # Vérifier si la table existe
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
            if not cursor.fetchone():
                print(f"⚠ Table {table} n'existe pas")
                continue
            
            # Vérifier si la colonne user_id existe
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'user_id' not in columns:
                print(f"Ajout de user_id à {table}...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER")
                print(f"✓ Colonne user_id ajoutée à {table}")
            else:
                print(f"✓ Colonne user_id existe déjà dans {table}")
                
        except sqlite3.Error as e:
            print(f"✗ Erreur avec {table}: {e}")
            continue
    
    # Créer un utilisateur admin si nécessaire
    try:
        cursor.execute("SELECT id FROM auth_user WHERE username = 'admin'")
        admin_user = cursor.fetchone()
        
        if not admin_user:
            print("Création de l'utilisateur admin...")
            cursor.execute("""
                INSERT INTO auth_user (username, first_name, last_name, email, is_staff, is_active, is_superuser, date_joined, password)
                VALUES ('admin', 'Admin', 'GuinéeGest', 'admin@guineegest.com', 1, 1, 1, datetime('now'), 'pbkdf2_sha256$600000$dummy$dummy')
            """)
            admin_id = cursor.lastrowid
            print(f"✓ Utilisateur admin créé avec ID {admin_id}")
        else:
            admin_id = admin_user[0]
            print(f"✓ Utilisateur admin existe avec ID {admin_id}")
        
        # Associer les données existantes à l'admin
        for table in tables:
            try:
                cursor.execute(f"UPDATE {table} SET user_id = ? WHERE user_id IS NULL", (admin_id,))
                updated = cursor.rowcount
                if updated > 0:
                    print(f"✓ {updated} enregistrements associés dans {table}")
            except sqlite3.Error as e:
                print(f"⚠ Erreur mise à jour {table}: {e}")
                continue
        
    except sqlite3.Error as e:
        print(f"✗ Erreur utilisateur admin: {e}")
    
    conn.commit()
    conn.close()
    print("\n✓ Base de données corrigée avec succès!")
    return True

if __name__ == '__main__':
    print("=== Correction directe de la base de données ===")
    fix_database()
