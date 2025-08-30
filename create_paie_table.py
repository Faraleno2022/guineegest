import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS PaieEmployes (
    id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
    employe_id bigint NOT NULL,
    mois integer NOT NULL,
    annee integer NOT NULL,
    salaire_base decimal NOT NULL DEFAULT 0,
    salaire_brut decimal NOT NULL DEFAULT 0,
    salaire_net decimal NOT NULL DEFAULT 0,
    salaire_net_a_payer decimal NOT NULL DEFAULT 0,
    jours_mois integer NOT NULL DEFAULT 0,
    jours_presence integer NOT NULL DEFAULT 0,
    jours_repos integer NOT NULL DEFAULT 0,
    absences integer NOT NULL DEFAULT 0,
    dimanches integer NOT NULL DEFAULT 0,
    conge integer NOT NULL DEFAULT 0,
    montant_jours_travailles decimal NOT NULL DEFAULT 0,
    heures_supplementaires decimal NOT NULL DEFAULT 0,
    montant_heures_supplementaires decimal NOT NULL DEFAULT 0,
    montant_heures_supplement_dimanches decimal NOT NULL DEFAULT 0,
    indemnite_transport decimal NOT NULL DEFAULT 0,
    indemnite_logement decimal NOT NULL DEFAULT 0,
    cherete_vie decimal NOT NULL DEFAULT 0,
    prime_discipline decimal NOT NULL DEFAULT 0,
    prime_ferie decimal NOT NULL DEFAULT 0,
    cnss decimal NOT NULL DEFAULT 0,
    rts decimal NOT NULL DEFAULT 0,
    vf decimal NOT NULL DEFAULT 0,
    avance_sur_salaire decimal NOT NULL DEFAULT 0,
    sanction_vol_carburant decimal NOT NULL DEFAULT 0,
    user_id integer
)
''')

cursor.execute('''
CREATE UNIQUE INDEX IF NOT EXISTS PaieEmployes_employe_mois_annee_uniq 
ON PaieEmployes (employe_id, mois, annee)
''')

cursor.execute('''
CREATE INDEX IF NOT EXISTS PaieEmployes_employe_id_idx 
ON PaieEmployes (employe_id)
''')

cursor.execute('''
CREATE INDEX IF NOT EXISTS PaieEmployes_user_id_idx 
ON PaieEmployes (user_id)
''')

print("Table PaieEmployes créée avec succès!")
