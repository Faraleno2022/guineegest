import os
import django

# Configuration de l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

# Imports nécessaires - Importation directe avec SQL pour éviter les problèmes de résolution de modèle
from django.contrib.auth.models import User
from django.db import connection

def associer_employes_utilisateur():
    # Récupérer l'utilisateur (probablement LENO avec ID=1)
    try:
        user = User.objects.get(username="LENO")  # Ajustez le nom d'utilisateur si nécessaire
        print(f"Utilisateur trouvé: {user.username} (ID: {user.id})")
        
        # Utiliser SQL brut pour éviter les problèmes de résolution de modèle
        with connection.cursor() as cursor:
            # Compter les employés sans utilisateur
            cursor.execute("SELECT COUNT(*) FROM Employes WHERE user_id IS NULL")
            count = cursor.fetchone()[0]
            print(f"Nombre d'employés sans utilisateur: {count}")
            
            # Mettre à jour les employés sans utilisateur
            cursor.execute(f"UPDATE Employes SET user_id = {user.id} WHERE user_id IS NULL")
            print(f"Terminé! {count} employés ont été associés à l'utilisateur {user.username}.")
        
    except User.DoesNotExist:
        print("Erreur: Utilisateur non trouvé. Veuillez vérifier le nom d'utilisateur.")
    except Exception as e:
        print(f"Erreur: {str(e)}")

if __name__ == "__main__":
    associer_employes_utilisateur()
