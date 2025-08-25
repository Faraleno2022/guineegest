import os
import django
import sys

print("Script d'association des employés démarré")
print(f"Version Python: {sys.version}")
print(f"Chemin courant: {os.getcwd()}")

try:
    # Configurer l'environnement Django
    print("Configuration de l'environnement Django...")
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
    print("Module de configuration défini: 'fleet_management.settings'")
    
    print("Initialisation de Django...")
    django.setup()
    print("Django initialisé avec succès")
    
    # Importer les modèles nécessaires
    print("Importation des modèles...")
    from fleet_app.models_entreprise import Employe
    from django.contrib.auth.models import User
    print("Modèles importés avec succès")
    
    def associate_employees_to_user():
        """
        Associe tous les employés sans utilisateur à l'utilisateur avec ID=1 (LENO)
        """
        try:
            # Récupérer l'utilisateur LENO (ID=1)
            print("Recherche de l'utilisateur avec ID=1...")
            user = User.objects.get(id=1)
            print(f"Utilisateur trouvé: {user.username} (ID: {user.id})")
            
            # Récupérer tous les employés sans utilisateur
            print("Recherche des employés sans utilisateur...")
            employes_sans_user = Employe.objects.filter(user__isnull=True)
            print(f"Nombre d'employés sans utilisateur: {employes_sans_user.count()}")
            
            # Associer chaque employé à l'utilisateur
            count = 0
            for employe in employes_sans_user:
                employe.user = user
                employe.save()
                count += 1
                print(f"Employé {employe.matricule} - {employe.prenom} {employe.nom} associé à l'utilisateur {user.username}")
            
            # Vérifier le résultat
            print(f"\nVérification après mise à jour:")
            print(f"Employés avec utilisateur: {Employe.objects.filter(user__isnull=False).count()}")
            print(f"Employés sans utilisateur: {Employe.objects.filter(user__isnull=True).count()}")
            print(f"Total d'employés mis à jour: {count}")
            
            return True
        except Exception as e:
            print(f"Erreur lors de l'association des employés: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    if __name__ == "__main__":
        print("Début de l'association des employés à l'utilisateur...")
        success = associate_employees_to_user()
        print("Terminé." if success else "Échec de l'opération.")

except Exception as e:
    print(f"Erreur lors de l'initialisation: {str(e)}")
    import traceback
    traceback.print_exc()
