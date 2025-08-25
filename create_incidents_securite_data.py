import os
import django
import datetime
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Vehicule, IncidentSecurite
from django.utils import timezone

def create_incidents_securite_data():
    """Crée des données d'incidents de sécurité pour les véhicules existants"""
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.all()
    
    if not vehicules.exists():
        print("Aucun véhicule trouvé. Veuillez d'abord créer des véhicules.")
        return
    
    # Types d'incidents possibles (définis dans le modèle)
    types_incidents = ['Accident', 'Incident', 'Défaut critique']
    
    # Niveaux de gravité possibles
    niveaux_gravite = ['Faible', 'Modéré', 'Élevé', 'Critique']
    
    # Commentaires possibles par type d'incident
    commentaires = {
        'Accident': [
            "Collision par l'arrière sur autoroute",
            "Accrochage sur parking",
            "Collision frontale à faible vitesse",
            "Sortie de route par temps de pluie",
            "Collision latérale à une intersection",
            "Accident en marche arrière",
            "Collision avec un obstacle fixe",
            "Accident dû à un non-respect de priorité"
        ],
        'Incident': [
            "Freinage d'urgence suite à un obstacle",
            "Dérapage sur chaussée glissante",
            "Perte de contrôle momentanée",
            "Éclatement d'un pneu",
            "Dysfonctionnement des feux de signalisation",
            "Défaillance temporaire des freins",
            "Problème de direction assistée",
            "Incident lié à la climatisation"
        ],
        'Défaut critique': [
            "Défaillance du système de freinage",
            "Problème de direction",
            "Défaut airbag",
            "Défaillance du système électrique",
            "Surchauffe moteur critique",
            "Défaut de transmission",
            "Problème de suspension dangereux",
            "Défaillance des ceintures de sécurité"
        ]
    }
    
    # Date actuelle
    current_date = timezone.now().date()
    
    # Générer plusieurs incidents pour chaque véhicule
    total_created = 0
    
    for vehicule in vehicules:
        print(f"Création de données d'incidents de sécurité pour {vehicule}")
        
        # Nombre d'incidents à créer pour ce véhicule (entre 1 et 4)
        nb_incidents = random.randint(1, 4)
        
        for i in range(nb_incidents):
            # Date aléatoire dans les 12 derniers mois
            days_ago = random.randint(0, 365)
            incident_date = current_date - datetime.timedelta(days=days_ago)
            
            # Type d'incident aléatoire
            type_incident = random.choice(types_incidents)
            
            # Gravité en fonction du type d'incident
            if type_incident == 'Accident':
                gravite = random.choice(niveaux_gravite)
            elif type_incident == 'Incident':
                gravite = random.choice(['Faible', 'Modéré'])
            else:  # Défaut critique
                gravite = random.choice(['Élevé', 'Critique'])
            
            # Commentaire aléatoire en fonction du type d'incident
            commentaire = random.choice(commentaires[type_incident])
            
            # Créer l'incident
            incident, created = IncidentSecurite.objects.get_or_create(
                vehicule=vehicule,
                date_incident=incident_date,
                type_incident=type_incident,
                defaults={
                    'gravite': gravite,
                    'commentaires': commentaire
                }
            )
            
            if created:
                print(f"  - {incident_date}: {type_incident} - Gravité: {gravite}")
                total_created += 1
    
    print(f"\nTotal de {total_created} incidents de sécurité créés.")

if __name__ == "__main__":
    print("Création des données d'incidents de sécurité...")
    print("=" * 50)
    create_incidents_securite_data()
    print("=" * 50)
    print("Terminé!")
