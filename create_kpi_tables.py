import sqlite3
import os
import sys

# Forcer l'affichage immédiat
sys.stdout.reconfigure(line_buffering=True)

print("=== SCRIPT DE CRÉATION DIRECTE DES TABLES KPI ===\n")

# Chemin vers la base de données SQLite
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')
print(f"Chemin de la base de données: {db_path}")

# Se connecter à la base de données
print("\nConnexion à la base de données SQLite...")
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("Connexion établie avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de se connecter à la base de données: {e}")
    exit(1)

# Créer la table fleet_app_distanceparcourue
print("\nCréation de la table fleet_app_distanceparcourue...")
try:
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
    print("Table fleet_app_distanceparcourue créée avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de créer la table fleet_app_distanceparcourue: {e}")

# Créer la table fleet_app_consommationcarburant
print("\nCréation de la table fleet_app_consommationcarburant...")
try:
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
    print("Table fleet_app_consommationcarburant créée avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de créer la table fleet_app_consommationcarburant: {e}")

# Créer la table fleet_app_disponibilitevehicule
print("\nCréation de la table fleet_app_disponibilitevehicule...")
try:
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
    print("Table fleet_app_disponibilitevehicule créée avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de créer la table fleet_app_disponibilitevehicule: {e}")

# Créer la table fleet_app_utilisationactif
print("\nCréation de la table fleet_app_utilisationactif...")
try:
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
    print("Table fleet_app_utilisationactif créée avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de créer la table fleet_app_utilisationactif: {e}")

# Créer la table fleet_app_coutfonctionnement si elle n'existe pas
print("\nCréation de la table fleet_app_coutfonctionnement...")
try:
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
    print("Table fleet_app_coutfonctionnement créée avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de créer la table fleet_app_coutfonctionnement: {e}")

# Créer la table fleet_app_coutfinancier si elle n'existe pas
print("\nCréation de la table fleet_app_coutfinancier...")
try:
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
    print("Table fleet_app_coutfinancier créée avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de créer la table fleet_app_coutfinancier: {e}")

# Créer la table fleet_app_incidentsecurite si elle n'existe pas
print("\nCréation de la table fleet_app_incidentsecurite...")
try:
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
    print("Table fleet_app_incidentsecurite créée avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de créer la table fleet_app_incidentsecurite: {e}")

# Valider les modifications
print("\nValidation des modifications...")
conn.commit()
print("Modifications validées avec succès.")

# Vérifier si les tables ont été créées
print("\nVérification des tables créées:")
cursor.execute("""
SELECT name FROM sqlite_master 
WHERE type='table' AND name IN (
    'fleet_app_distanceparcourue',
    'fleet_app_consommationcarburant',
    'fleet_app_disponibilitevehicule',
    'fleet_app_utilisationactif',
    'fleet_app_coutfonctionnement',
    'fleet_app_coutfinancier',
    'fleet_app_incidentsecurite'
);
""")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# Fermer la connexion
conn.close()
print("Connexion à la base de données fermée.")

print("\n=== SCRIPT TERMINÉ ===")
