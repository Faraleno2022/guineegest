import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# Vérifier si la table existe déjà
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='HeuresSupplementaires'")
table_exists = cursor.fetchone()

if not table_exists:
    # Créer la table complète
    cursor.execute('''
    CREATE TABLE HeuresSupplementaires (
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
        created_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    print("Table HeuresSupplementaires créée")
else:
    # Vérifier si la colonne user_id existe
    cursor.execute("PRAGMA table_info(HeuresSupplementaires)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'user_id' not in columns:
        cursor.execute('ALTER TABLE HeuresSupplementaires ADD COLUMN user_id integer')
        print("Colonne user_id ajoutée à HeuresSupplementaires")
    
    if 'created_at' not in columns:
        cursor.execute('ALTER TABLE HeuresSupplementaires ADD COLUMN created_at datetime')
        cursor.execute('UPDATE HeuresSupplementaires SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL')
        print("Colonne created_at ajoutée")
    
    if 'updated_at' not in columns:
        cursor.execute('ALTER TABLE HeuresSupplementaires ADD COLUMN updated_at datetime')
        cursor.execute('UPDATE HeuresSupplementaires SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL')
        print("Colonne updated_at ajoutée")

# Créer les index
try:
    cursor.execute('''
    CREATE UNIQUE INDEX IF NOT EXISTS HeuresSupplementaires_employe_date_heure_debut_uniq 
    ON HeuresSupplementaires (employe_id, date, heure_debut)
    ''')
    
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS HeuresSupplementaires_employe_id_idx 
    ON HeuresSupplementaires (employe_id)
    ''')
    
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS HeuresSupplementaires_date_idx 
    ON HeuresSupplementaires (date)
    ''')
    
    if 'user_id' in [row[1] for row in cursor.execute("PRAGMA table_info(HeuresSupplementaires)")]:
        cursor.execute('''
        CREATE INDEX IF NOT EXISTS HeuresSupplementaires_user_id_idx 
        ON HeuresSupplementaires (user_id)
        ''')
    
    print("Index créés avec succès")
except Exception as e:
    print(f"Erreur lors de la création des index: {e}")

print("Table HeuresSupplementaires configurée avec succès!")
