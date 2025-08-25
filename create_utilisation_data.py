import os
import django
import datetime
import random
import names

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Vehicule, UtilisationVehicule
from django.utils import timezone

def create_utilisation_data():
    """Crée des données d'utilisation pour les véhicules existants"""
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.all()
    
    if not vehicules.exists():
        print("Aucun véhicule trouvé. Veuillez d'abord créer des véhicules.")
        return
    
    # Départements possibles (définis dans le modèle)
    departements = ['Commercial', 'Technique', 'Administratif', 'Direction', 'Logistique', 'Maintenance', 'Autre']
    
    # Motifs d'utilisation possibles
    motifs = [
        "Visite client",
        "Livraison",
        "Déplacement professionnel",
        "Intervention technique",
        "Transport de matériel",
        "Réunion externe",
        "Formation",
        "Salon professionnel",
        "Maintenance préventive",
        "Dépannage urgence"
    ]
    
    # Observations possibles
    observations = [
        "RAS",
        "Véhicule rendu propre",
        "Légère rayure sur l'aile avant droite",
        "Niveau d'huile bas",
        "Pression des pneus vérifiée",
        "Voyant moteur allumé",
        "Climatisation défectueuse",
        "Bruit suspect au niveau de la suspension",
        "Consommation excessive",
        ""
    ]
    
    # Date actuelle
    current_date = timezone.now().date()
    
    # Générer plusieurs utilisations pour chaque véhicule
    total_created = 0
    
    for vehicule in vehicules:
        print(f"Création de données d'utilisation pour {vehicule}")
        
        # Kilométrage de base pour ce véhicule (basé sur le kilométrage initial)
        base_kilometrage = vehicule.kilometrage_initial or random.randint(10000, 50000)
        current_km = base_kilometrage
        
        # Nombre d'utilisations à créer pour ce véhicule (entre 5 et 10)
        nb_utilisations = random.randint(5, 10)
        
        for i in range(nb_utilisations):
            # Date de début aléatoire dans les 6 derniers mois
            days_ago_start = random.randint(0, 180)
            date_debut = current_date - datetime.timedelta(days=days_ago_start)
            
            # Durée de l'utilisation (entre 1 et 5 jours)
            duree = random.randint(1, 5)
            date_fin = date_debut + datetime.timedelta(days=duree)
            
            # Kilométrage au départ (basé sur le kilométrage actuel)
            km_depart = current_km
            
            # Distance parcourue pendant l'utilisation (entre 50 et 500 km)
            distance = random.randint(50, 500)
            km_retour = km_depart + distance
            
            # Mise à jour du kilométrage actuel
            current_km = km_retour
            
            # Conducteur aléatoire (nom et prénom générés)
            conducteur = f"{names.get_first_name()} {names.get_last_name()}"
            
            # Département aléatoire
            departement = random.choice(departements)
            
            # Motif d'utilisation aléatoire
            motif = random.choice(motifs)
            
            # Observation aléatoire
            observation = random.choice(observations)
            
            # Créer l'utilisation
            utilisation, created = UtilisationVehicule.objects.get_or_create(
                vehicule=vehicule,
                date_debut=date_debut,
                date_fin=date_fin,
                defaults={
                    'conducteur': conducteur,
                    'departement': departement,
                    'motif': motif,
                    'km_depart': km_depart,
                    'km_retour': km_retour,
                    'observations': observation
                }
            )
            
            if created:
                print(f"  - {date_debut} à {date_fin}: {conducteur} ({departement}) - {km_retour - km_depart} km")
                total_created += 1
    
    print(f"\nTotal de {total_created} utilisations créées.")

if __name__ == "__main__":
    print("Création des données d'utilisation des véhicules...")
    print("=" * 50)
    create_utilisation_data()
    print("=" * 50)
    print("Terminé!")
