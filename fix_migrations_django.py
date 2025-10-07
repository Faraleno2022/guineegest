#!/usr/bin/env python
"""
Script Django pour corriger l'historique des migrations
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db.migrations.recorder import MigrationRecorder
from datetime import datetime

print("=== Correction de l'historique des migrations ===\n")

# Supprimer les migrations 0019 et 0020
print("1. Suppression des migrations 0019 et 0020...")
deleted_count = MigrationRecorder.Migration.objects.filter(
    app='fleet_app',
    name__in=['0019_add_frais_km_to_paie', '0020_add_frais_kilometrique']
).delete()[0]
print(f"   {deleted_count} migrations supprimées")

# Ajouter 0018 comme fake
print("\n2. Ajout de la migration 0018_placeholder...")
migration, created = MigrationRecorder.Migration.objects.get_or_create(
    app='fleet_app',
    name='0018_placeholder',
    defaults={'applied': datetime.now()}
)
if created:
    print("   Migration 0018 ajoutée")
else:
    print("   Migration 0018 existe déjà")

# Vérifier
print("\n3. Vérification des migrations fleet_app...")
migrations = MigrationRecorder.Migration.objects.filter(app='fleet_app').order_by('id')

for migration in migrations:
    print(f"   ✓ {migration.name}")

print("\n✅ Correction terminée!")
print("\nVous pouvez maintenant exécuter:")
print("  python manage.py migrate fleet_app")
