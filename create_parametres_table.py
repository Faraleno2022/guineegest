import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS ParametresPaie (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    nom varchar(100) NOT NULL,
    valeur varchar(255) NOT NULL,
    cle varchar(100),
    description text,
    user_id integer
)
''')

cursor.execute('''
CREATE INDEX IF NOT EXISTS ParametresPaie_user_id_idx 
ON ParametresPaie (user_id)
''')

cursor.execute('''
CREATE INDEX IF NOT EXISTS ParametresPaie_cle_idx 
ON ParametresPaie (cle)
''')

print("Table ParametresPaie créée avec succès!")
