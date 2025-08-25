import os
import sys
import django

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.apps import apps
from django.db import connection

# Vérifier si le modèle Alerte existe dans le registre d'applications
print("Vérification des modèles Alerte dans le registre d'applications...")
app_config = apps.get_app_config('fleet_app')
model_names = [model.__name__ for model in app_config.get_models()]
print(f"Modèles dans l'application fleet_app: {model_names}")

# Vérifier si la table existe dans la base de données
print("\nVérification des tables dans la base de données...")
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables dans la base de données: {[table[0] for table in tables]}")

print("\nVérification spécifique pour la table Alerte...")
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%alerte%';")
    alerte_tables = cursor.fetchall()
    print(f"Tables liées à Alerte: {[table[0] for table in alerte_tables]}")

# Si la table existe, afficher sa structure
if alerte_tables:
    print("\nStructure de la table Alerte:")
    with connection.cursor() as cursor:
        for table in alerte_tables:
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print(f"Colonnes de {table[0]}: {columns}")

print("\nFin de la vérification.")
