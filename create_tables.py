import sqlite3
import os

print("=== SCRIPT DE CRÉATION DIRECTE DES TABLES ===\n")

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

# Créer la table fleet_app_vehicule si elle n'existe pas
print("\nCréation de la table fleet_app_vehicule...")
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fleet_app_vehicule (
        id_vehicule INTEGER PRIMARY KEY AUTOINCREMENT,
        immatriculation VARCHAR(20) NOT NULL,
        marque VARCHAR(50) NOT NULL,
        modele VARCHAR(50) NOT NULL,
        type_vehicule VARCHAR(50),
        moteur VARCHAR(20),
        statut VARCHAR(20),
        observations TEXT,
        date_acquisition DATE,
        prix_achat DECIMAL(10, 2),
        assurance_compagnie VARCHAR(100),
        assurance_numero VARCHAR(50),
        assurance_debut DATE,
        assurance_fin DATE,
        date_mise_service DATE
    );
    """)
    print("Table fleet_app_vehicule créée avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de créer la table fleet_app_vehicule: {e}")

# Créer la table fleet_app_documentadministratif si elle n'existe pas
print("\nCréation de la table fleet_app_documentadministratif...")
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fleet_app_documentadministratif (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_document VARCHAR(50) NOT NULL,
        numero VARCHAR(50) NOT NULL,
        date_emission DATE NOT NULL,
        date_expiration DATE,
        fichier VARCHAR(100),
        commentaires TEXT,
        vehicule_id INTEGER NOT NULL,
        FOREIGN KEY (vehicule_id) REFERENCES fleet_app_vehicule(id_vehicule)
    );
    """)
    print("Table fleet_app_documentadministratif créée avec succès.")
except Exception as e:
    print(f"ERREUR: Impossible de créer la table fleet_app_documentadministratif: {e}")

# Valider les modifications
print("\nValidation des modifications...")
conn.commit()
print("Modifications validées avec succès.")

# Vérifier si les tables ont été créées
print("\nVérification des tables créées:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name='fleet_app_vehicule' OR name='fleet_app_documentadministratif');")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# Fermer la connexion
conn.close()
print("Connexion à la base de données fermée.")

print("\n=== SCRIPT TERMINÉ ===")
