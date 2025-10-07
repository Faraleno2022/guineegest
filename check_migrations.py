#!/usr/bin/env python
"""
Script pour vérifier les migrations appliquées sur PythonAnywhere
À exécuter sur le serveur PythonAnywhere
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db.migrations.recorder import MigrationRecorder

print("=== Migrations appliquées pour fleet_app ===\n")

migrations = MigrationRecorder.Migration.objects.filter(app='fleet_app').order_by('id')

for migration in migrations:
    print(f"✓ {migration.name}")

if migrations.exists():
    last_migration = migrations.last()
    print(f"\n=== Dernière migration appliquée ===")
    print(f"Nom: {last_migration.name}")
    print(f"Date: {last_migration.applied}")
else:
    print("\nAucune migration appliquée pour fleet_app")
