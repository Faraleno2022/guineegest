import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

# Importer les modèles après la configuration de Django
from django.db import connection

print("=== CRÉATION DES TABLES KPI MANQUANTES VIA DJANGO SHELL ===")

# Liste des tables à vérifier/créer
tables_to_check = [
    'fleet_app_distanceparcourue',
    'fleet_app_consommationcarburant',
    'fleet_app_disponibilitevehicule',
    'fleet_app_utilisationactif',
    'fleet_app_coutfonctionnement',
    'fleet_app_coutfinancier',
    'fleet_app_incidentsecurite'
]

# Vérifier les tables existantes
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    print("\nTables existantes dans la base de données:")
    for table in existing_tables:
        print(f"- {table}")
    
    print("\nVérification des tables KPI nécessaires:")
    for table in tables_to_check:
        if table in existing_tables:
            print(f"✓ {table} existe déjà")
        else:
            print(f"✗ {table} n'existe pas")

# Créer les tables manquantes en utilisant les modèles Django
print("\nCréation des tables manquantes via l'ORM Django...")

# Forcer la création des tables via l'ORM Django
from django.core.management import call_command

print("\nExécution de makemigrations...")
call_command('makemigrations', 'fleet_app', interactive=False)

print("\nExécution de migrate...")
call_command('migrate', 'fleet_app', interactive=False)

# Vérifier à nouveau après la migration
print("\nVérification des tables après migration:")
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [row[0] for row in cursor.fetchall()]
    
    for table in tables_to_check:
        if table in existing_tables:
            print(f"✓ {table} existe maintenant")
        else:
            print(f"✗ {table} n'existe toujours pas - création manuelle nécessaire")
            
            # Créer manuellement les tables manquantes
            if table == 'fleet_app_distanceparcourue':
                print(f"  Création manuelle de {table}...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS fleet_app_distanceparcourue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_debut DATE NOT NULL,
                    km_debut INTEGER NOT NULL,
                    date_fin DATE NOT NULL,
                    km_fin INTEGER NOT NULL,
                    distance_parcourue INTEGER NOT NULL,
                    type_moteur VARCHAR(20) NOT NULL,
                    limite_annuelle INTEGER NULL,
                    vehicule_id VARCHAR(20) NOT NULL REFERENCES fleet_app_vehicule (id_vehicule)
                );
                """)
                
            elif table == 'fleet_app_consommationcarburant':
                print(f"  Création manuelle de {table}...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS fleet_app_consommationcarburant (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_plein1 DATE NOT NULL,
                    kilometrage_plein1 INTEGER NOT NULL,
                    date_plein2 DATE NOT NULL,
                    kilometrage_plein2 INTEGER NOT NULL,
                    litres_consommes REAL NOT NULL,
                    distance_parcourue INTEGER NOT NULL,
                    consommation_calculee REAL NOT NULL,
                    consommation_constructeur REAL NULL,
                    ecart_constructeur REAL NULL,
                    vehicule_id VARCHAR(20) NOT NULL REFERENCES fleet_app_vehicule (id_vehicule)
                );
                """)
                
            elif table == 'fleet_app_disponibilitevehicule':
                print(f"  Création manuelle de {table}...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS fleet_app_disponibilitevehicule (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_debut DATE NOT NULL,
                    date_fin DATE NOT NULL,
                    disponibilite_pourcentage REAL NOT NULL,
                    raison_indisponibilite TEXT NOT NULL,
                    heures_disponibles INTEGER NOT NULL,
                    heures_totales INTEGER NOT NULL,
                    jours_total_periode INTEGER NOT NULL,
                    jours_hors_service INTEGER NOT NULL,
                    vehicule_id VARCHAR(20) NOT NULL REFERENCES fleet_app_vehicule (id_vehicule)
                );
                """)
                
            elif table == 'fleet_app_utilisationactif':
                print(f"  Création manuelle de {table}...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS fleet_app_utilisationactif (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_debut DATE NULL,
                    date_fin DATE NULL,
                    conducteur VARCHAR(100) NULL,
                    departement VARCHAR(100) NULL,
                    motif_utilisation TEXT NULL,
                    periode VARCHAR(100) NULL,
                    jours_utilises INTEGER NULL,
                    jours_disponibles INTEGER NULL,
                    vehicule_id VARCHAR(20) NOT NULL REFERENCES fleet_app_vehicule (id_vehicule)
                );
                """)
                
            elif table == 'fleet_app_coutfonctionnement':
                print(f"  Création manuelle de {table}...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS fleet_app_coutfonctionnement (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    type_cout VARCHAR(50) NOT NULL,
                    montant DECIMAL(10, 2) NOT NULL,
                    kilometrage INTEGER NOT NULL,
                    cout_par_km DECIMAL(10, 4) NOT NULL,
                    description TEXT NULL,
                    vehicule_id VARCHAR(20) NOT NULL REFERENCES fleet_app_vehicule (id_vehicule)
                );
                """)
                
            elif table == 'fleet_app_coutfinancier':
                print(f"  Création manuelle de {table}...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS fleet_app_coutfinancier (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    type_cout VARCHAR(50) NOT NULL,
                    montant DECIMAL(10, 2) NOT NULL,
                    kilometrage INTEGER NOT NULL,
                    cout_par_km DECIMAL(10, 4) NOT NULL,
                    periode_amortissement INTEGER NULL,
                    description TEXT NULL,
                    vehicule_id VARCHAR(20) NOT NULL REFERENCES fleet_app_vehicule (id_vehicule)
                );
                """)
                
            elif table == 'fleet_app_incidentsecurite':
                print(f"  Création manuelle de {table}...")
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS fleet_app_incidentsecurite (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date_incident DATE NOT NULL,
                    conducteur VARCHAR(100) NOT NULL,
                    type_incident VARCHAR(50) NOT NULL,
                    gravite VARCHAR(50) NOT NULL,
                    lieu VARCHAR(200) NOT NULL,
                    description TEXT NOT NULL,
                    mesures_prises TEXT NULL,
                    commentaires TEXT NULL,
                    vehicule_id VARCHAR(20) NOT NULL REFERENCES fleet_app_vehicule (id_vehicule)
                );
                """)

# Valider les modifications
connection.commit()

print("\n=== SCRIPT TERMINÉ ===")
