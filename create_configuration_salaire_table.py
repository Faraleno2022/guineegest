import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / 'django_fleet.db'

SCHEMA_SQL = '''
CREATE TABLE IF NOT EXISTS ConfigurationSalaire (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employe_id INTEGER NOT NULL,
    statut_presence VARCHAR(50) NOT NULL,
    montant_journalier NUMERIC(10,2) DEFAULT 0,
    actif BOOLEAN DEFAULT 1,
    user_id INTEGER,
    UNIQUE (employe_id, statut_presence),
    FOREIGN KEY(employe_id) REFERENCES Employes(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES auth_user(id) ON DELETE CASCADE
);
'''

def main():
    if not DB_PATH.exists():
        # try parent (project root)
        alt = Path(__file__).resolve().parent.parent / 'django_fleet.db'
        if alt.exists():
            global DB_PATH
            DB_PATH = alt
    print(f"Using database: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    try:
        cur = conn.cursor()
        cur.execute('PRAGMA foreign_keys = ON;')
        cur.executescript(SCHEMA_SQL)
        conn.commit()
        # Sanity check
        cur.execute("PRAGMA table_info('ConfigurationSalaire');")
        cols = cur.fetchall()
        print('ConfigurationSalaire columns:')
        for c in cols:
            print(' -', c)
        print('Done.')
    finally:
        conn.close()

if __name__ == '__main__':
    main()
