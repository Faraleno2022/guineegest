#!/usr/bin/env python
"""
Script pour corriger l'historique des migrations dans la base de données locale
"""

import sqlite3
from datetime import datetime

# Connexion à la base de données
conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

print("=== Correction de l'historique des migrations ===\n")

# Supprimer les migrations 0019 et 0020
print("1. Suppression des migrations 0019 et 0020...")
cursor.execute("DELETE FROM django_migrations WHERE app = 'fleet_app' AND name IN ('0019_add_frais_km_to_paie', '0020_add_frais_kilometrique')")
print(f"   {cursor.rowcount} migrations supprimées")

# Ajouter 0018 comme fake
print("\n2. Ajout de la migration 0018_placeholder...")
try:
    cursor.execute("INSERT INTO django_migrations (app, name, applied) VALUES ('fleet_app', '0018_placeholder', ?)", (datetime.now(),))
    print("   Migration 0018 ajoutée")
except sqlite3.IntegrityError:
    print("   Migration 0018 existe déjà")

# Commit
conn.commit()

# Vérifier
print("\n3. Vérification des migrations fleet_app...")
cursor.execute("SELECT name FROM django_migrations WHERE app = 'fleet_app' ORDER BY id")
migrations = cursor.fetchall()

for migration in migrations:
    print(f"   ✓ {migration[0]}")

conn.close()

print("\n✅ Correction terminée!")
print("\nVous pouvez maintenant exécuter:")
print("  python manage.py migrate fleet_app")
