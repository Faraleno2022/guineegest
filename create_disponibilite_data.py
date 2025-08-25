import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Vehicule, DisponibiliteVehicule
from django.utils import timezone

def create_disponibilite_data():
    """Crée des données de disponibilité pour les véhicules existants"""
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.all()
    
    if not vehicules.exists():
        print("Aucun véhicule trouvé. Veuillez d'abord créer des véhicules.")
        return
    
    # Périodes pour les données (derniers mois)
    current_date = timezone.now().date()
    periods = [
        {
            'nom': 'Juillet 2025',
            'start': current_date.replace(day=1),
            'end': current_date,
            'jours': current_date.day
        },
        {
            'nom': 'Juin 2025',
            'start': (current_date.replace(day=1) - datetime.timedelta(days=1)).replace(day=1),
            'end': current_date.replace(day=1) - datetime.timedelta(days=1),
            'jours': 30
        },
        {
            'nom': 'Mai 2025',
            'start': ((current_date.replace(day=1) - datetime.timedelta(days=1)).replace(day=1) - datetime.timedelta(days=1)).replace(day=1),
            'end': (current_date.replace(day=1) - datetime.timedelta(days=1)).replace(day=1) - datetime.timedelta(days=1),
            'jours': 31
        }
    ]
    
    total_created = 0
    
    # Pour chaque véhicule, créer des données pour chaque période
    for vehicule in vehicules:
        print(f"Création de données de disponibilité pour {vehicule}")
        
        for period in periods:
            # Jours totaux dans la période
            jours_total = period['jours']
            
            # Jours hors service (aléatoire entre 0 et 5 jours)
            jours_hors_service = random.randint(0, 5)
            
            # Heures disponibles et totales
            heures_totales = jours_total * 24
            heures_disponibles = (jours_total - jours_hors_service) * 24
            
            # Pourcentage de disponibilité
            disponibilite_pourcentage = round((heures_disponibles / heures_totales) * 100, 2)
            
            # Raison d'indisponibilité
            raisons = [
                "Maintenance préventive",
                "Réparation moteur",
                "Remplacement pièces",
                "Inspection technique",
                "Accident mineur",
                "Problème électrique",
                "Entretien programmé"
            ]
            raison = random.choice(raisons) if jours_hors_service > 0 else ""
            
            # Créer l'entrée de disponibilité
            disponibilite_obj, created = DisponibiliteVehicule.objects.get_or_create(
                vehicule=vehicule,
                date_debut=period['start'],
                date_fin=period['end'],
                defaults={
                    'heures_disponibles': heures_disponibles,
                    'heures_totales': heures_totales,
                    'disponibilite_pourcentage': disponibilite_pourcentage,
                    'raison_indisponibilite': raison,
                    'periode': period['nom'],
                    'jours_total_periode': jours_total,
                    'jours_hors_service': jours_hors_service
                }
            )
            
            if created:
                print(f"  - Période {period['nom']}: {disponibilite_pourcentage}% disponible ({jours_hors_service} jours hors service)")
                total_created += 1
            else:
                print(f"  - Données déjà existantes pour la période {period['nom']}")
    
    print(f"\nTotal de {total_created} entrées de disponibilité créées.")

if __name__ == "__main__":
    print("Création des données de disponibilité des véhicules...")
    print("=" * 50)
    create_disponibilite_data()
    print("=" * 50)
    print("Terminé!")
