-- Script pour recréer la base de données avec encodage correct
DROP DATABASE IF EXISTS guineegest_db;
DROP USER IF EXISTS guineegest_user;

-- Créer l'utilisateur
CREATE USER guineegest_user WITH PASSWORD 'guineegest2024';

-- Créer la base de données avec encodage UTF8 explicite
CREATE DATABASE guineegest_db 
    WITH OWNER guineegest_user
    ENCODING 'UTF8'
    LC_COLLATE = 'C'
    LC_CTYPE = 'C'
    TEMPLATE template0;

-- Accorder tous les privilèges
GRANT ALL PRIVILEGES ON DATABASE guineegest_db TO guineegest_user;

-- Se connecter à la base et accorder les privilèges sur le schéma
\c guineegest_db
GRANT ALL ON SCHEMA public TO guineegest_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO guineegest_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO guineegest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO guineegest_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO guineegest_user;
