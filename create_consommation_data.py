import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Vehicule, ConsommationCarburant
from django.utils import timezone

def create_consommation_data():
    """Crée des données de consommation de carburant pour les véhicules existants"""
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
    
    # Consommation moyenne par type de moteur (L/100km)
    consommation_moyenne = {
        'Essence': 7.5,
        'Diesel': 6.0,
        'Hybride': 4.5,
        'Électrique': 0.0,  # Pas de consommation de carburant
    }
    
    total_created = 0
    
    # Pour chaque véhicule, créer des données pour chaque période
    for vehicule in vehicules:
        print(f"Création de données de consommation pour {vehicule}")
        
        # Sauter les véhicules électriques
        if vehicule.type_moteur == 'Électrique':
            print(f"  - Véhicule électrique, pas de consommation de carburant")
            continue
        
        # Kilométrage initial du véhicule
        km_actuel = vehicule.kilometrage_initial
        
        for i, period in enumerate(periods):
            # Générer une distance aléatoire entre 500 et 3000 km
            distance = random.randint(500, 3000)
            km_plein1 = km_actuel
            km_plein2 = km_plein1 + distance
            
            # Consommation moyenne avec variation aléatoire
            base_consommation = consommation_moyenne[vehicule.type_moteur]
            variation = random.uniform(-0.8, 1.2)  # Variation de -0.8 à +1.2 L/100km
            consommation_100km = round(base_consommation + variation, 2)
            
            # Calculer les litres ajoutés
            litres_ajoutes = round((consommation_100km * distance) / 100, 2)
            
            # Consommation constructeur (fixe par type de moteur)
            consommation_constructeur = consommation_moyenne[vehicule.type_moteur]
            
            # Écart avec constructeur
            ecart_constructeur = round(((consommation_100km - consommation_constructeur) / consommation_constructeur) * 100, 2)
            
            # Créer l'entrée de consommation
            consommation_obj, created = ConsommationCarburant.objects.get_or_create(
                vehicule=vehicule,
                date_plein1=period['start'],
                date_plein2=period['end'],
                defaults={
                    'km_plein1': km_plein1,
                    'km_plein2': km_plein2,
                    'litres_ajoutes': litres_ajoutes,
                    'distance_parcourue': distance,
                    'consommation_100km': consommation_100km,
                    'consommation_constructeur': consommation_constructeur,
                    'ecart_constructeur': ecart_constructeur
                }
            )
            
            if created:
                print(f"  - Période {period['start']} à {period['end']}: {consommation_100km} L/100km")
                total_created += 1
            else:
                print(f"  - Données déjà existantes pour la période {period['start']} à {period['end']}")
            
            # Mettre à jour le kilométrage actuel pour la prochaine période
            km_actuel = km_plein2
    
    print(f"\nTotal de {total_created} entrées de consommation de carburant créées.")

if __name__ == "__main__":
    print("Création des données de consommation de carburant...")
    print("=" * 50)
    create_consommation_data()
    print("=" * 50)
    print("Terminé!")
