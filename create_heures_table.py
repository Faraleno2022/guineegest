import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS HeuresSupplementaires (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    employe_id bigint NOT NULL,
    date date NOT NULL,
    heure_debut time NOT NULL,
    heure_fin time NOT NULL,
    autorise_par varchar(100),
    duree decimal NOT NULL DEFAULT 0,
    taux_horaire decimal,
    total_a_payer decimal NOT NULL DEFAULT 0,
    type_jour varchar(20) NOT NULL DEFAULT 'ouvrable',
    user_id integer,
    created_at datetime NOT NULL,
    updated_at datetime NOT NULL
)
''')

cursor.execute('''
CREATE UNIQUE INDEX IF NOT EXISTS HeuresSupplementaires_employe_date_heure_debut_uniq 
ON HeuresSupplementaires (employe_id, date, heure_debut)
''')

cursor.execute('''
CREATE INDEX IF NOT EXISTS HeuresSupplementaires_employe_id_idx 
ON HeuresSupplementaires (employe_id)
''')

cursor.execute('''
CREATE INDEX IF NOT EXISTS HeuresSupplementaires_user_id_idx 
ON HeuresSupplementaires (user_id)
''')

cursor.execute('''
CREATE INDEX IF NOT EXISTS HeuresSupplementaires_date_idx 
ON HeuresSupplementaires (date)
''')

print("Table HeuresSupplementaires créée avec succès!")
