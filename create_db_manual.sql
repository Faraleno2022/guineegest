-- Script SQL pour créer la base de données GuinéeGest
-- Exécutez ce script avec psql en tant que superutilisateur postgres

-- Créer la base de données
CREATE DATABASE guineegest_db;

-- Créer l'utilisateur
CREATE USER guineegest_user WITH PASSWORD 'guineegest2024';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE guineegest_db TO guineegest_user;

-- Se connecter à la nouvelle base de données
\c guineegest_db

-- Accorder les privilèges sur le schéma public
GRANT ALL ON SCHEMA public TO guineegest_user;
GRANT CREATE ON SCHEMA public TO guineegest_user;

-- Afficher confirmation
SELECT 'Base de donnees GuineeGest creee avec succes' AS message;
