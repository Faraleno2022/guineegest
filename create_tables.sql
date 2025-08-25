-- Script SQL pour créer les tables KPI manquantes

-- Table DistanceParcourue
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

-- Table ConsommationCarburant
CREATE TABLE IF NOT EXISTS "fleet_app_consommationcarburant" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date_plein1" date NOT NULL,
    "kilometrage_plein1" integer NOT NULL,
    "date_plein2" date NOT NULL,
    "kilometrage_plein2" integer NOT NULL,
    "litres_consommes" real NOT NULL,
    "distance_parcourue" integer NOT NULL,
    "consommation_calculee" real NOT NULL,
    "consommation_constructeur" real NULL,
    "ecart_constructeur" real NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);

-- Table DisponibiliteVehicule
CREATE TABLE IF NOT EXISTS "fleet_app_disponibilitevehicule" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date_debut" date NOT NULL,
    "date_fin" date NOT NULL,
    "disponibilite_pourcentage" real NOT NULL,
    "raison_indisponibilite" text NOT NULL,
    "heures_disponibles" integer NOT NULL,
    "heures_totales" integer NOT NULL,
    "jours_total_periode" integer NOT NULL,
    "jours_hors_service" integer NOT NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);

-- Table UtilisationActif
CREATE TABLE IF NOT EXISTS "fleet_app_utilisationactif" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date_debut" date NULL,
    "date_fin" date NULL,
    "conducteur" varchar(100) NULL,
    "departement" varchar(100) NULL,
    "motif_utilisation" text NULL,
    "periode" varchar(100) NULL,
    "jours_utilises" integer NULL,
    "jours_disponibles" integer NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);

-- Table CoutFonctionnement
CREATE TABLE IF NOT EXISTS "fleet_app_coutfonctionnement" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date" date NOT NULL,
    "type_cout" varchar(50) NOT NULL,
    "montant" decimal(10, 2) NOT NULL,
    "kilometrage" integer NOT NULL,
    "cout_par_km" decimal(10, 4) NOT NULL,
    "description" text NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);

-- Table CoutFinancier
CREATE TABLE IF NOT EXISTS "fleet_app_coutfinancier" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date" date NOT NULL,
    "type_cout" varchar(50) NOT NULL,
    "montant" decimal(10, 2) NOT NULL,
    "kilometrage" integer NOT NULL,
    "cout_par_km" decimal(10, 4) NOT NULL,
    "periode_amortissement" integer NULL,
    "description" text NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);

-- Table IncidentSecurite
CREATE TABLE IF NOT EXISTS "fleet_app_incidentsecurite" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "date_incident" date NOT NULL,
    "conducteur" varchar(100) NOT NULL,
    "type_incident" varchar(50) NOT NULL,
    "gravite" varchar(50) NOT NULL,
    "lieu" varchar(200) NOT NULL,
    "description" text NOT NULL,
    "mesures_prises" text NULL,
    "commentaires" text NULL,
    "vehicule_id" varchar(20) NOT NULL REFERENCES "fleet_app_vehicule" ("id_vehicule")
);
