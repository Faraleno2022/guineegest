from django.core.management.base import BaseCommand
from fleet_app.models import DistanceParcourue, Vehicule
from datetime import date
import random

class Command(BaseCommand):
    help = 'Ajoute de nouvelles données de distances parcourues'

    def handle(self, *args, **options):
        # Supprimer toutes les distances existantes
        DistanceParcourue.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Toutes les distances parcourues existantes ont été supprimées.'))

        # Récupérer tous les véhicules
        vehicules = list(Vehicule.objects.all())
        self.stdout.write(f'Nombre de véhicules disponibles: {len(vehicules)}')

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
                
                self.stdout.write(f'Ajouté distance pour {v}: {distance} km entre {date_debut} et {date_fin}')

        self.stdout.write(self.style.SUCCESS('Toutes les nouvelles distances parcourues ont été ajoutées avec succès.'))
