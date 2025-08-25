import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Vehicule, CoutFinancier
from django.utils import timezone

def create_couts_financiers_data():
    """Crée des données de coûts financiers pour les véhicules existants"""
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.all()
    
    if not vehicules.exists():
        print("Aucun véhicule trouvé. Veuillez d'abord créer des véhicules.")
        return
    
    # Types de coûts financiers possibles
    types_couts = [
        "Achat",
        "Leasing",
        "Amortissement",
        "Financement",
        "Assurance annuelle",
        "Taxe annuelle",
        "Dépréciation"
    ]
    
    # Périodes pour les données (derniers mois)
    current_date = timezone.now().date()
    
    # Générer plusieurs entrées de coûts pour chaque véhicule
    total_created = 0
    
    for vehicule in vehicules:
        print(f"Création de données de coûts financiers pour {vehicule}")
        
        # Kilométrage de base pour ce véhicule
        base_kilometrage = random.randint(15000, 60000)
        
        # Créer plusieurs entrées de coûts pour différentes dates
        for i in range(5):  # 5 entrées par véhicule
            # Date aléatoire dans les 12 derniers mois
            days_ago = random.randint(0, 365)
            entry_date = current_date - datetime.timedelta(days=days_ago)
            
            # Type de coût aléatoire
            type_cout = random.choice(types_couts)
            
            # Montant en fonction du type de coût
            if type_cout == "Achat":
                montant = random.uniform(15000, 35000)
                periode_amortissement = 60  # 5 ans
            elif type_cout == "Leasing":
                montant = random.uniform(300, 600) * 12  # montant annuel
                periode_amortissement = 36  # 3 ans
            elif type_cout == "Amortissement":
                montant = random.uniform(2000, 5000)
                periode_amortissement = 60  # 5 ans
            elif type_cout == "Financement":
                montant = random.uniform(500, 1500)
                periode_amortissement = 48  # 4 ans
            elif type_cout == "Assurance annuelle":
                montant = random.uniform(800, 1500)
                periode_amortissement = 12  # 1 an
            elif type_cout == "Taxe annuelle":
                montant = random.uniform(200, 600)
                periode_amortissement = 12  # 1 an
            else:  # Dépréciation
                montant = random.uniform(1000, 3000)
                periode_amortissement = 12  # 1 an
                
            # Kilométrage progressif
            kilometrage = base_kilometrage + (i * random.randint(5000, 10000))
            
            # Coût par km
            cout_par_km = montant / (kilometrage if kilometrage > 0 else 10000)
            
            # Description
            descriptions = {
                "Achat": ["Achat véhicule neuf", "Achat véhicule d'occasion", "Achat avec reprise"],
                "Leasing": ["Contrat leasing 36 mois", "Leasing avec option d'achat", "Leasing tout inclus"],
                "Amortissement": ["Amortissement linéaire", "Amortissement dégressif", "Amortissement fiscal"],
                "Financement": ["Prêt bancaire", "Crédit automobile", "Financement interne"],
                "Assurance annuelle": ["Assurance tous risques", "Assurance au tiers", "Assurance flotte"],
                "Taxe annuelle": ["Taxe sur les véhicules de société", "Taxe écologique", "Taxe régionale"],
                "Dépréciation": ["Dépréciation annuelle", "Perte de valeur", "Dépréciation accélérée"]
            }
            description = random.choice(descriptions.get(type_cout, ["Divers"]))
            
            # Créer l'entrée de coût
            cout_obj, created = CoutFinancier.objects.get_or_create(
                vehicule=vehicule,
                date=entry_date,
                type_cout=type_cout,
                defaults={
                    'montant': round(montant, 2),
                    'kilometrage': kilometrage,
                    'cout_par_km': round(cout_par_km, 4),
                    'periode_amortissement': periode_amortissement,
                    'description': description
                }
            )
            
            if created:
                print(f"  - {entry_date}: {type_cout} - {round(montant, 2)}€ (amortissement: {periode_amortissement} mois)")
                total_created += 1
    
    print(f"\nTotal de {total_created} entrées de coûts financiers créées.")

if __name__ == "__main__":
    print("Création des données de coûts financiers...")
    print("=" * 50)
    create_couts_financiers_data()
    print("=" * 50)
    print("Terminé!")
