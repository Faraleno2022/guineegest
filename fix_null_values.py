import sqlite3

def fix_null_values():
    con = sqlite3.connect(r'C:\Users\faral\Desktop\Gestion_parck\django_fleet.db')
    c = con.cursor()
    
    # Update all NULL values for numeric fields
    numeric_updates = [
        'UPDATE Employes SET taux_cnss_salarie_custom = 0 WHERE taux_cnss_salarie_custom IS NULL',
        'UPDATE Employes SET taux_cnss_employeur_custom = 0 WHERE taux_cnss_employeur_custom IS NULL', 
        'UPDATE Employes SET taux_vf_custom = 0 WHERE taux_vf_custom IS NULL',
        'UPDATE Employes SET taux_horaire_specifique = 0 WHERE taux_horaire_specifique IS NULL'
    ]
    
    # Update text fields
    text_updates = [
        'UPDATE Employes SET mode_calcul_heures_supp = "standard" WHERE mode_calcul_heures_supp IS NULL OR mode_calcul_heures_supp = ""'
    ]
    
    for query in numeric_updates + text_updates:
        try:
            c.execute(query)
            print(f'Executed: {query[:50]}...')
        except Exception as e:
            print(f'Error: {e}')
    
    con.commit()
    con.close()
    print('All NULL values updated')

if __name__ == '__main__':
    fix_null_values()
