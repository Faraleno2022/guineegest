import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

# Imports nécessaires
from django.contrib.auth.models import User
from django.db import connection

def verifier_heures_supplementaires():
    try:
        # Récupérer l'utilisateur LENO
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username FROM auth_user WHERE username = 'LENO'")
            user_info = cursor.fetchone()
            
            if not user_info:
                print("Utilisateur LENO non trouvé!")
                return
                
            user_id = user_info[0]
            username = user_info[1]
            print(f"Utilisateur trouvé: {username} (ID: {user_id})")
            
            # Lister toutes les tables pour trouver le bon nom
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [table[0] for table in cursor.fetchall()]
            print("\nTables disponibles dans la base de données:")
            for table in tables:
                print(f"- {table}")
            
            # Chercher automatiquement la table des heures supplémentaires
            possible_tables = [t for t in tables if 'heure' in t.lower() or 'supplement' in t.lower()]
            
            if not possible_tables:
                print("\nAucune table d'heures supplémentaires trouvée automatiquement.")
                print("Vérifiez les noms de tables ci-dessus et relancez le script en modifiant le code.")
                return
            
            table_name = possible_tables[0]
            print(f"\nTable d'heures supplémentaires trouvée: {table_name}")
            
            # Vérifier la structure de la table
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print("\nStructure de la table:")
            for col in columns:
                print(f"- {col[1]} ({col[2]})")
            
            # Vérifier toutes les heures supplémentaires
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_count = cursor.fetchone()[0]
            print(f"\nNombre total d'heures supplémentaires dans la base: {total_count}")
            
            if total_count == 0:
                print("Aucune heure supplémentaire trouvée dans la base de données.")
                return
            
            # Vérifier les heures supplémentaires liées à des employés de l'utilisateur
            try:
                cursor.execute(f"""
                    SELECT COUNT(*) 
                    FROM {table_name} hs
                    JOIN Employes e ON hs.employe_id = e.id
                    WHERE e.user_id = {user_id}
                """)
                user_count = cursor.fetchone()[0]
                print(f"Nombre d'heures supplémentaires liées à vos employés: {user_count}")
                
                # Afficher les détails des heures supplémentaires
                cursor.execute(f"""
                    SELECT hs.id, e.prenom, e.nom, e.matricule, hs.date, hs.duree, hs.total_a_payer
                    FROM {table_name} hs
                    JOIN Employes e ON hs.employe_id = e.id
                    ORDER BY hs.date DESC
                    LIMIT 10
                """)
                
                rows = cursor.fetchall()
                if rows:
                    print("\nDétails des 10 dernières heures supplémentaires:")
                    print("ID | Employé | Matricule | Date | Durée | Montant")
                    print("-" * 70)
                    
                    for row in rows:
                        hs_id, prenom, nom, matricule, date, duree, total = row
                        print(f"{hs_id} | {prenom} {nom} | {matricule} | {date} | {duree}h | {total} GNF")
                else:
                    print("Aucune heure supplémentaire trouvée pour vos employés.")
            except Exception as e:
                print(f"Erreur lors de la requête sur les heures supplémentaires: {str(e)}")
                print("Vérifiez que la table a les bonnes colonnes (employe_id, date, duree, total_a_payer).")
            
    except Exception as e:
        print(f"Erreur: {str(e)}")

if __name__ == "__main__":
    verifier_heures_supplementaires()
