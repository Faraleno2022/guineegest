import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Vehicule, DistanceParcourue
from django.utils import timezone

def create_distance_data():
    """Crée des données de distance parcourue pour les véhicules existants"""
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.all()
    
    if not vehicules.exists():
        print("Aucun véhicule trouvé. Veuillez d'abord créer des véhicules.")
        return
    
    # Périodes pour les données
    current_date = timezone.now().date()
    periods = [
        # Dernier mois
        {
            'start': current_date - datetime.timedelta(days=30),
            'end': current_date
        },
        # Mois précédent
        {
            'start': current_date - datetime.timedelta(days=60),
            'end': current_date - datetime.timedelta(days=31)
        },
        # Il y a deux mois
        {
            'start': current_date - datetime.timedelta(days=90),
            'end': current_date - datetime.timedelta(days=61)
        }
    ]
    
    total_created = 0
    
    # Pour chaque véhicule, créer des données pour chaque période
    for vehicule in vehicules:
        print(f"Création de données de distance pour {vehicule}")
        
        # Kilométrage initial du véhicule
        km_actuel = vehicule.kilometrage_initial
        
        for period in periods:
            # Générer une distance aléatoire entre 500 et 3000 km
            distance = random.randint(500, 3000)
            km_fin = km_actuel + distance
            
            # Créer l'entrée de distance parcourue
            distance_obj, created = DistanceParcourue.objects.get_or_create(
                vehicule=vehicule,
                date_debut=period['start'],
                date_fin=period['end'],
                defaults={
                    'km_debut': km_actuel,
                    'km_fin': km_fin,
                    'distance_parcourue': distance
                }
            )
            
            if created:
                print(f"  - Période {period['start']} à {period['end']}: {distance} km")
                total_created += 1
            else:
                print(f"  - Données déjà existantes pour la période {period['start']} à {period['end']}")
            
            # Mettre à jour le kilométrage actuel pour la prochaine période
            km_actuel = km_fin
    
    print(f"\nTotal de {total_created} entrées de distance parcourue créées.")

if __name__ == "__main__":
    print("Création des données de distance parcourue...")
    print("=" * 50)
    create_distance_data()
    print("=" * 50)
    print("Terminé!")
