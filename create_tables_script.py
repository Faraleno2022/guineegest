import sqlite3
import os

# Chemin vers la base de données
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')

# Connexion à la base de données
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Afficher les tables existantes
print("Tables existantes avant création :")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# Créer la table DocumentAdministratif
print("\nCréation de la table DocumentAdministratif...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS "fleet_app_documentadministratif" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "type_document" varchar(50) NOT NULL,
    "numero" varchar(50) NOT NULL,
    "date_emission" date NOT NULL,
    "date_expiration" date NOT NULL,
    "fichier" varchar(100) NULL,
    "commentaires" text NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);
''')

# Créer la table DistanceParcourue
print("Création de la table DistanceParcourue...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS "fleet_app_distanceparcourue" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date_debut" date NOT NULL,
    "km_debut" integer NOT NULL,
    "date_fin" date NOT NULL,
    "km_fin" integer NOT NULL,
    "distance_parcourue" integer NOT NULL,
    "type_moteur" varchar(20) NOT NULL,
    "limite_annuelle" integer NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);
''')

# Créer la table ConsommationCarburant
print("Création de la table ConsommationCarburant...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS "fleet_app_consommationcarburant" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date_plein1" date NOT NULL,
    "km_plein1" integer NOT NULL,
    "date_plein2" date NOT NULL,
    "km_plein2" integer NOT NULL,
    "litres" real NOT NULL,
    "prix_litre" real NOT NULL,
    "montant_total" real NOT NULL,
    "distance_parcourue" integer NOT NULL,
    "consommation" real NOT NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);
''')

# Créer la table DisponibiliteVehicule
print("Création de la table DisponibiliteVehicule...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS "fleet_app_disponibilitevehicule" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "mois" date NOT NULL,
    "jours_total_mois" integer NOT NULL,
    "jours_panne_garage" integer NOT NULL,
    "jours_disponibles" integer NOT NULL,
    "taux_disponibilite" real NOT NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);
''')

# Créer la table UtilisationVehicule
print("Création de la table UtilisationVehicule...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS "fleet_app_utilisationvehicule" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "mois" date NOT NULL,
    "jours_disponibles" integer NOT NULL,
    "jours_effectivement_utilises" integer NOT NULL,
    "taux_utilisation" real NOT NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);
''')

# Créer la table CoutFonctionnement
print("Création de la table CoutFonctionnement...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS "fleet_app_coutfonctionnement" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "mois" date NOT NULL,
    "cout_carburant" real NOT NULL,
    "cout_pneus" real NOT NULL,
    "cout_entretien" real NOT NULL,
    "cout_reparations" real NOT NULL,
    "km_parcourus" integer NOT NULL,
    "cout_total" real NOT NULL,
    "cout_par_km" real NOT NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);
''')

# Créer la table CoutFinancier
print("Création de la table CoutFinancier...")
cursor.execute('''
CREATE TABLE IF NOT EXISTS "fleet_app_coutfinancier" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "mois" date NOT NULL,
    "cout_amortissement" real NOT NULL,
    "cout_assurance" real NOT NULL,
    "cout_taxes" real NOT NULL,
    "cout_location" real NOT NULL,
    "km_parcourus" integer NOT NULL,
    "cout_total" real NOT NULL,
    "cout_par_km" real NOT NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);
''')

# Valider les changements
conn.commit()

# Vérifier les tables après création
print("\nTables existantes après création :")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

# Vérifier spécifiquement les tables que nous venons de créer
tables_to_check = [
    "fleet_app_documentadministratif",
    "fleet_app_distanceparcourue",
    "fleet_app_consommationcarburant",
    "fleet_app_disponibilitevehicule",
    "fleet_app_utilisationvehicule",
    "fleet_app_coutfonctionnement",
    "fleet_app_coutfinancier"
]

print("\nVérification des tables créées :")
for table in tables_to_check:
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
    result = cursor.fetchone()
    if result:
        print(f"- {table}: CRÉÉE AVEC SUCCÈS")
    else:
        print(f"- {table}: NON CRÉÉE")

# Fermer la connexion
conn.close()

print("\nScript terminé.")
