import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Vehicule, CoutFonctionnement
from django.utils import timezone

def create_couts_data():
    """Crée des données de coûts de fonctionnement pour les véhicules existants"""
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.all()
    
    if not vehicules.exists():
        print("Aucun véhicule trouvé. Veuillez d'abord créer des véhicules.")
        return
    
    # Types de coûts possibles
    types_couts = [
        "Carburant",
        "Entretien",
        "Réparation",
        "Assurance",
        "Taxe",
        "Péage",
        "Parking",
        "Lavage"
    ]
    
    # Périodes pour les données (derniers mois)
    current_date = timezone.now().date()
    
    # Générer plusieurs entrées de coûts pour chaque véhicule
    total_created = 0
    
    for vehicule in vehicules:
        print(f"Création de données de coûts pour {vehicule}")
        
        # Kilométrage de base pour ce véhicule
        base_kilometrage = random.randint(15000, 60000)
        
        # Créer plusieurs entrées de coûts pour différentes dates
        for i in range(15):  # 15 entrées par véhicule
            # Date aléatoire dans les 3 derniers mois
            days_ago = random.randint(0, 90)
            entry_date = current_date - datetime.timedelta(days=days_ago)
            
            # Type de coût aléatoire
            type_cout = random.choice(types_couts)
            
            # Montant en fonction du type de coût
            if type_cout == "Carburant":
                montant = random.uniform(50, 120)
            elif type_cout == "Entretien":
                montant = random.uniform(100, 500)
            elif type_cout == "Réparation":
                montant = random.uniform(200, 1500)
            elif type_cout == "Assurance":
                montant = random.uniform(300, 800)
            elif type_cout == "Taxe":
                montant = random.uniform(100, 400)
            else:
                montant = random.uniform(10, 50)
                
            # Kilométrage progressif
            kilometrage = base_kilometrage + (i * random.randint(500, 1500))
            
            # Coût par km
            cout_par_km = montant / (500 if type_cout == "Carburant" else 1000)
            
            # Description
            descriptions = {
                "Carburant": ["Plein station Total", "Plein station Esso", "Plein station BP"],
                "Entretien": ["Vidange et filtres", "Révision annuelle", "Changement pneus"],
                "Réparation": ["Remplacement freins", "Réparation embrayage", "Remplacement batterie"],
                "Assurance": ["Prime annuelle", "Ajustement assurance", "Complément assurance"],
                "Taxe": ["Taxe annuelle", "Vignette écologique", "Taxe régionale"],
                "Péage": ["Autoroute A1", "Péage urbain", "Tunnel"],
                "Parking": ["Parking centre-ville", "Parking aéroport", "Stationnement longue durée"],
                "Lavage": ["Lavage extérieur", "Nettoyage complet", "Nettoyage intérieur"]
            }
            description = random.choice(descriptions.get(type_cout, ["Divers"]))
            
            # Créer l'entrée de coût
            cout_obj, created = CoutFonctionnement.objects.get_or_create(
                vehicule=vehicule,
                date=entry_date,
                type_cout=type_cout,
                defaults={
                    'montant': round(montant, 2),
                    'kilometrage': kilometrage,
                    'cout_par_km': round(cout_par_km, 3),
                    'description': description
                }
            )
            
            if created:
                print(f"  - {entry_date}: {type_cout} - {round(montant, 2)}€ ({kilometrage} km)")
                total_created += 1
    
    print(f"\nTotal de {total_created} entrées de coûts créées.")

if __name__ == "__main__":
    print("Création des données de coûts de fonctionnement...")
    print("=" * 50)
    create_couts_data()
    print("=" * 50)
    print("Terminé!")
