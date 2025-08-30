import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS ConfigurationSalaire (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    statut_presence varchar(50) NOT NULL DEFAULT 'P(Am_&_Pm)',
    montant_journalier decimal NOT NULL DEFAULT 0,
    actif bool NOT NULL DEFAULT 1,
    employe_id bigint NOT NULL,
    user_id integer
)
''')
cursor.execute('''
CREATE UNIQUE INDEX IF NOT EXISTS ConfigurationSalaire_employe_statut_uniq 
ON ConfigurationSalaire (employe_id, statut_presence)
''')
print("Table ConfigurationSalaire créée avec succès!")
