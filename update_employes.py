import os
import sys
import django
from datetime import date

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

# Import des modèles après la configuration Django
from fleet_app.models_entreprise import Employe

def update_employes():
    """
    Met à jour les employés existants pour ajouter une date d'embauche par défaut
    et s'assurer que le statut est défini
    """
    # Récupérer tous les employés sans date d'embauche
    employes_sans_date = Employe.objects.filter(date_embauche=None)
    count = employes_sans_date.count()
    
    print(f"Nombre d'employés sans date d'embauche: {count}")
    
    # Mettre à jour les employés avec une date d'embauche par défaut (aujourd'hui)
    for employe in employes_sans_date:
        employe.date_embauche = date.today()
        employe.statut = 'Actif'  # S'assurer que le statut est défini
        employe.save()
        print(f"Employé mis à jour: {employe.prenom} {employe.nom} - Date d'embauche: {employe.date_embauche}")
    
    print(f"\nMise à jour terminée. {count} employés ont été mis à jour.")

if __name__ == "__main__":
    update_employes()
