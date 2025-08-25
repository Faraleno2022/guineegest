# Script pour ajouter des données de distances parcourues
from fleet_app.models import DistanceParcourue, Vehicule
from datetime import date
import random

# Récupérer tous les véhicules
vehicules = list(Vehicule.objects.all())
print(f'Nombre de véhicules disponibles: {len(vehicules)}')

# Ajouter des données de distance pour les 5 premiers véhicules
for i, v in enumerate(vehicules[:5]):
    for j in range(3):
        # Créer des dates pour chaque période (tous les 2 mois en 2025)
        date_debut = date(2025, 1+j*2, 1)
        date_fin = date(2025, 2+j*2, 28)
        
        # Générer des kilométrages réalistes
        km_debut = random.randint(5000, 50000) + j*1000
        km_fin = km_debut + random.randint(1000, 5000)
        distance = km_fin - km_debut
        
        # Définir la limite annuelle selon le type de moteur
        if v.type_moteur == 'Diesel':
            limite = 30000  # 30 000 km/an pour diesel
        elif v.type_moteur == 'Essence':
            limite = 15000  # 15 000 km/an pour essence
        else:
            limite = 10000  # 10 000 km/an pour autres (électrique, hybride)
        
        # Créer l'entrée de distance parcourue
        DistanceParcourue.objects.create(
            vehicule=v,
            date_debut=date_debut,
            km_debut=km_debut,
            date_fin=date_fin,
            km_fin=km_fin,
            distance_parcourue=distance,
            type_moteur=v.type_moteur,
            limite_annuelle=limite
        )
        
        print(f'Ajouté distance pour {v}: {distance} km entre {date_debut} et {date_fin}')

print("Toutes les nouvelles distances parcourues ont été ajoutées avec succès.")
