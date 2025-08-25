import os
import django
import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Vehicule, Alerte, UtilisationActif
from django.utils import timezone

def create_vehicles():
    """Crée des véhicules de test"""
    vehicles = [
        {
            'id_vehicule': 'VH001',
            'immatriculation': 'AA-123-BB',
            'marque': 'Renault',
            'modele': 'Clio',
            'type_moteur': 'Essence',
            'categorie': 'Voiture',
            'date_mise_service': timezone.now().date() - datetime.timedelta(days=365),
            'date_acquisition': timezone.now().date() - datetime.timedelta(days=400),
            'kilometrage_initial': 0,
            'affectation': 'Service Commercial',
            'statut_actuel': 'Actif',
            'numero_chassis': 'REN123456789',
            'numero_moteur': 'MOT123456',
            'observations': 'Véhicule en bon état'
        },
        {
            'id_vehicule': 'VH002',
            'immatriculation': 'CC-456-DD',
            'marque': 'Peugeot',
            'modele': '308',
            'type_moteur': 'Diesel',
            'categorie': 'Voiture',
            'date_mise_service': timezone.now().date() - datetime.timedelta(days=180),
            'date_acquisition': timezone.now().date() - datetime.timedelta(days=200),
            'kilometrage_initial': 1000,
            'affectation': 'Service Technique',
            'statut_actuel': 'Actif',
            'numero_chassis': 'PEU987654321',
            'numero_moteur': 'MOT654321',
            'observations': 'Véhicule neuf'
        },
        {
            'id_vehicule': 'VH003',
            'immatriculation': 'EE-789-FF',
            'marque': 'Citroën',
            'modele': 'Berlingo',
            'type_moteur': 'Diesel',
            'categorie': '4x4',
            'date_mise_service': timezone.now().date() - datetime.timedelta(days=730),
            'date_acquisition': timezone.now().date() - datetime.timedelta(days=750),
            'kilometrage_initial': 500,
            'affectation': 'Service Livraison',
            'statut_actuel': 'Maintenance',
            'numero_chassis': 'CIT123789456',
            'numero_moteur': 'MOT789456',
            'observations': 'Véhicule en maintenance pour problème de freins'
        }
    ]
    
    created_vehicles = []
    for vehicle_data in vehicles:
        vehicle, created = Vehicule.objects.get_or_create(
            id_vehicule=vehicle_data['id_vehicule'],
            defaults=vehicle_data
        )
        if created:
            print(f"Véhicule créé: {vehicle}")
        else:
            print(f"Véhicule existant: {vehicle}")
        created_vehicles.append(vehicle)
    
    return created_vehicles

def create_alerts(vehicles):
    """Crée des alertes liées aux véhicules"""
    alerts = [
        {
            'vehicule': vehicles[0],
            'type_alerte': 'Maintenance',
            'description': 'Vidange à prévoir',
            'date_creation': timezone.now().date() - datetime.timedelta(days=5),
            'niveau_urgence': 'Moyen',
            'statut': 'Active'
        },
        {
            'vehicule': vehicles[0],
            'type_alerte': 'Document',
            'description': 'Assurance à renouveler',
            'date_creation': timezone.now().date() - datetime.timedelta(days=10),
            'niveau_urgence': 'Élevé',
            'statut': 'Active'
        },
        {
            'vehicule': vehicles[1],
            'type_alerte': 'Panne',
            'description': 'Problème de batterie',
            'date_creation': timezone.now().date() - datetime.timedelta(days=2),
            'niveau_urgence': 'Critique',
            'statut': 'Active'
        },
        {
            'vehicule': vehicles[2],
            'type_alerte': 'Maintenance',
            'description': 'Remplacement des plaquettes de frein',
            'date_creation': timezone.now().date() - datetime.timedelta(days=15),
            'niveau_urgence': 'Élevé',
            'statut': 'Résolue'
        }
    ]
    
    created_alerts = []
    for alert_data in alerts:
        alert, created = Alerte.objects.get_or_create(
            vehicule=alert_data['vehicule'],
            type_alerte=alert_data['type_alerte'],
            description=alert_data['description'],
            defaults=alert_data
        )
        if created:
            print(f"Alerte créée: {alert}")
        else:
            print(f"Alerte existante: {alert}")
        created_alerts.append(alert)
    
    return created_alerts

def create_utilisations(vehicles):
    """Crée des utilisations liées aux véhicules"""
    utilisations = [
        {
            'vehicule': vehicles[0],
            'periode': 'Janvier 2025',
            'jours_disponibles': 31,
            'jours_utilises': 22,
            'date_debut': datetime.date(2025, 1, 1),
            'date_fin': datetime.date(2025, 1, 31),
            'conducteur': 'Jean Dupont',
            'departement': 'Commercial',
            'motif_utilisation': 'Visites clients'
        },
        {
            'vehicule': vehicles[0],
            'periode': 'Février 2025',
            'jours_disponibles': 28,
            'jours_utilises': 20,
            'date_debut': datetime.date(2025, 2, 1),
            'date_fin': datetime.date(2025, 2, 28),
            'conducteur': 'Jean Dupont',
            'departement': 'Commercial',
            'motif_utilisation': 'Visites clients'
        },
        {
            'vehicule': vehicles[1],
            'periode': 'Janvier 2025',
            'jours_disponibles': 31,
            'jours_utilises': 15,
            'date_debut': datetime.date(2025, 1, 1),
            'date_fin': datetime.date(2025, 1, 31),
            'conducteur': 'Marie Martin',
            'departement': 'Technique',
            'motif_utilisation': 'Interventions sur site'
        },
        {
            'vehicule': vehicles[2],
            'periode': 'Janvier 2025',
            'jours_disponibles': 31,
            'jours_utilises': 10,
            'date_debut': datetime.date(2025, 1, 1),
            'date_fin': datetime.date(2025, 1, 31),
            'conducteur': 'Pierre Durand',
            'departement': 'Logistique',
            'motif_utilisation': 'Livraisons'
        }
    ]
    
    created_utilisations = []
    for utilisation_data in utilisations:
        utilisation, created = UtilisationActif.objects.get_or_create(
            vehicule=utilisation_data['vehicule'],
            periode=utilisation_data['periode'],
            defaults=utilisation_data
        )
        if created:
            print(f"Utilisation créée: {utilisation}")
        else:
            print(f"Utilisation existante: {utilisation}")
        created_utilisations.append(utilisation)
    
    return created_utilisations

if __name__ == "__main__":
    print("Création des données de test...")
    print("=" * 50)
    
    # Création des véhicules
    print("\nCréation des véhicules:")
    print("-" * 50)
    vehicles = create_vehicles()
    
    # Création des alertes
    print("\nCréation des alertes:")
    print("-" * 50)
    alerts = create_alerts(vehicles)
    
    # Création des utilisations
    print("\nCréation des utilisations:")
    print("-" * 50)
    utilisations = create_utilisations(vehicles)
    
    print("\nDonnées de test créées avec succès!")
    print("=" * 50)
