-- Script SQL pour créer la table DocumentAdministratif manquante

-- Table DocumentAdministratif
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

-- Vérification de la création de la table
SELECT name FROM sqlite_master WHERE type='table' AND name='fleet_app_documentadministratif';
