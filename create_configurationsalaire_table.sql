-- Créer la table ConfigurationSalaire manquante
CREATE TABLE IF NOT EXISTS "ConfigurationSalaire" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    "statut_presence" varchar(50) NOT NULL DEFAULT 'P(Am_&_Pm)',
    "montant_journalier" decimal NOT NULL DEFAULT 0,
    "actif" bool NOT NULL DEFAULT 1,
    "employe_id" bigint NOT NULL REFERENCES "Employes" ("id") DEFERRABLE INITIALLY DEFERRED,
    "user_id" integer REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED
);

-- Créer l'index unique sur employe et statut_presence
CREATE UNIQUE INDEX IF NOT EXISTS "ConfigurationSalaire_employe_id_statut_presence_uniq" 
ON "ConfigurationSalaire" ("employe_id", "statut_presence");

-- Créer les autres index
CREATE INDEX IF NOT EXISTS "ConfigurationSalaire_employe_id_idx" ON "ConfigurationSalaire" ("employe_id");
CREATE INDEX IF NOT EXISTS "ConfigurationSalaire_user_id_idx" ON "ConfigurationSalaire" ("user_id");
