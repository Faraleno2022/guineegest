"""
Script pour nettoyer les migrations Django liées au modèle Alerte.
Ce script va:
1. Supprimer les fichiers de migration qui font référence au modèle Alerte
2. Supprimer les entrées correspondantes dans la table django_migrations
3. Préparer le système pour une nouvelle migration propre
"""

import os
import re
import sqlite3
from pathlib import Path
import shutil

# Chemin vers le projet Django
BASE_DIR = Path(__file__).resolve().parent
MIGRATIONS_DIR = BASE_DIR / "fleet_app" / "migrations"
DB_PATH = BASE_DIR / "db.sqlite3"

def backup_database():
    """Crée une sauvegarde de la base de données."""
    backup_path = str(DB_PATH) + ".backup"
    try:
        shutil.copy2(DB_PATH, backup_path)
        print(f"Base de données sauvegardée dans {backup_path}")
        return True
    except Exception as e:
        print(f"Erreur lors de la sauvegarde de la base de données: {e}")
        return False

def find_alerte_migrations():
    """Trouve tous les fichiers de migration qui font référence au modèle Alerte."""
    alerte_migrations = []
    
    for file_path in MIGRATIONS_DIR.glob("*.py"):
        if file_path.name.startswith("__"):
            continue
            
        content = file_path.read_text(encoding="utf-8")
        if "alerte" in content.lower() or "Alerte" in content:
            alerte_migrations.append(file_path)
    
    return alerte_migrations

def remove_migration_files(migration_files):
    """Supprime les fichiers de migration spécifiés."""
    for file_path in migration_files:
        try:
            os.remove(file_path)
            print(f"Supprimé: {file_path.name}")
        except Exception as e:
            print(f"Erreur lors de la suppression de {file_path.name}: {e}")

def clean_migrations_table():
    """Supprime les entrées de migration liées au modèle Alerte de la table django_migrations."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Vérifier si la table django_migrations existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='django_migrations'")
        if not cursor.fetchone():
            print("La table django_migrations n'existe pas.")
            return False
        
        # Trouver et supprimer les migrations liées à Alerte
        cursor.execute("SELECT id, app, name FROM django_migrations WHERE app='fleet_app' AND name LIKE '%alerte%'")
        migrations = cursor.fetchall()
        
        if not migrations:
            print("Aucune migration liée à Alerte trouvée dans la table django_migrations.")
            return True
        
        for migration_id, app, name in migrations:
            cursor.execute("DELETE FROM django_migrations WHERE id=?", (migration_id,))
            print(f"Supprimé de django_migrations: {app}.{name}")
        
        conn.commit()
        print(f"{len(migrations)} entrées supprimées de la table django_migrations.")
        return True
    except Exception as e:
        print(f"Erreur lors de la manipulation de la base de données: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def main():
    print("Nettoyage des migrations liées au modèle Alerte...")
    
    # Sauvegarde de la base de données
    backup_database()
    
    # Trouver les fichiers de migration liés à Alerte
    alerte_migrations = find_alerte_migrations()
    print(f"\nFichiers de migration liés à Alerte trouvés: {len(alerte_migrations)}")
    for file_path in alerte_migrations:
        print(f"- {file_path.name}")
    
    # Supprimer les fichiers de migration
    if alerte_migrations:
        remove_migration_files(alerte_migrations)
    
    # Nettoyer la table django_migrations
    clean_migrations_table()
    
    print("\nNettoyage terminé. Veuillez maintenant:")
    print("1. Redémarrer votre serveur Django")
    print("2. Créer une nouvelle migration avec 'python manage.py makemigrations'")
    print("3. Appliquer la migration avec 'python manage.py migrate'")

if __name__ == "__main__":
    main()
