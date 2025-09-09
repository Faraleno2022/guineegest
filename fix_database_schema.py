#!/usr/bin/env python
"""
Script pour corriger le schéma de base de données en ajoutant les colonnes user_id manquantes
"""
import os
import sys
import django
import sqlite3

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.conf import settings
from django.contrib.auth.models import User

def get_db_path():
    """Obtenir le chemin de la base de données SQLite"""
    db_config = settings.DATABASES['default']
    if db_config['ENGINE'] == 'django.db.backends.sqlite3':
        return db_config['NAME']
    else:
        raise Exception("Ce script ne fonctionne qu'avec SQLite")

def add_user_columns():
    """Ajouter les colonnes user_id aux tables qui n'en ont pas"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Liste des tables et colonnes à ajouter
    tables_to_update = [
        'fleet_app_vehicule',
        'fleet_app_chauffeur', 
        'fleet_app_feuillederroute',
        'fleet_app_alerte',
        'fleet_app_coutfonctionnement',
        'fleet_app_coutfinancier',
        'fleet_app_utilisationvehicule'
    ]
    
    for table in tables_to_update:
        try:
            # Vérifier si la colonne existe déjà
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'user_id' not in columns:
                print(f"Ajout de la colonne user_id à {table}...")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN user_id INTEGER REFERENCES auth_user(id)")
                print(f"✓ Colonne user_id ajoutée à {table}")
            else:
                print(f"✓ Colonne user_id existe déjà dans {table}")
                
        except sqlite3.Error as e:
            print(f"✗ Erreur avec la table {table}: {e}")
            continue
    
    conn.commit()
    conn.close()
    print("✓ Toutes les colonnes user_id ont été ajoutées")

def create_test_user():
    """Créer un utilisateur de test"""
    try:
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@guineegest.com',
                'first_name': 'Admin',
                'last_name': 'GuinéeGest',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            print("✓ Utilisateur admin créé")
        else:
            print("✓ Utilisateur admin existe déjà")
        return user
    except Exception as e:
        print(f"✗ Erreur lors de la création de l'utilisateur: {e}")
        return None

def associate_data_to_user():
    """Associer les données existantes à l'utilisateur admin"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Obtenir l'ID de l'utilisateur admin
    try:
        user = User.objects.get(username='admin')
        user_id = user.id
    except User.DoesNotExist:
        print("✗ Utilisateur admin non trouvé")
        return False
    
    # Mettre à jour les tables avec l'ID utilisateur
    tables_to_update = [
        'fleet_app_vehicule',
        'fleet_app_chauffeur', 
        'fleet_app_feuillederroute',
        'fleet_app_alerte',
        'fleet_app_coutfonctionnement',
        'fleet_app_coutfinancier',
        'fleet_app_utilisationvehicule'
    ]
    
    for table in tables_to_update:
        try:
            cursor.execute(f"UPDATE {table} SET user_id = ? WHERE user_id IS NULL", (user_id,))
            updated_rows = cursor.rowcount
            print(f"✓ {updated_rows} enregistrements mis à jour dans {table}")
        except sqlite3.Error as e:
            print(f"✗ Erreur avec la table {table}: {e}")
            continue
    
    conn.commit()
    conn.close()
    print("✓ Toutes les données ont été associées à l'utilisateur admin")
    return True

if __name__ == '__main__':
    print("=== Correction du schéma de base de données ===")
    
    try:
        # Étape 1: Ajouter les colonnes user_id
        add_user_columns()
        
        # Étape 2: Créer un utilisateur de test
        user = create_test_user()
        if not user:
            sys.exit(1)
        
        # Étape 3: Associer les données existantes
        if not associate_data_to_user():
            sys.exit(1)
        
        print("\n✓ Correction terminée avec succès!")
        print("Vous pouvez maintenant démarrer le serveur avec: python manage.py runserver")
        
    except Exception as e:
        print(f"✗ Erreur critique: {e}")
        sys.exit(1)
