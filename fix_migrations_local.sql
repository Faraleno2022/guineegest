-- Fix migrations localement
-- À exécuter dans SQLite

-- Supprimer les migrations 0019 et 0020 de l'historique
DELETE FROM django_migrations WHERE app = 'fleet_app' AND name = '0019_add_frais_km_to_paie';
DELETE FROM django_migrations WHERE app = 'fleet_app' AND name = '0020_add_frais_kilometrique';

-- Ajouter 0018 comme fake
INSERT INTO django_migrations (app, name, applied) VALUES ('fleet_app', '0018_placeholder', datetime('now'));
