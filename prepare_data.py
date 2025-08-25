"""
Script pour préparer les données avant d'appliquer les migrations qui convertissent
les champs conducteur de texte à ForeignKey.
"""
import os
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Chauffeur, UtilisationActif, UtilisationVehicule, IncidentSecurite

def get_or_create_chauffeur(nom_complet):
    """
    Crée ou récupère un chauffeur à partir d'un nom complet
    """
    if not nom_complet:
        return None
        
    # Essayer de séparer le nom et prénom
    parts = nom_complet.strip().split(' ', 1)
    if len(parts) == 2:
        nom, prenom = parts
    else:
        nom = parts[0]
        prenom = ''
        
    # Chercher un chauffeur existant avec ce nom et prénom
    chauffeurs = Chauffeur.objects.filter(nom__iexact=nom)
    if prenom:
        chauffeurs = chauffeurs.filter(prenom__iexact=prenom)
        
    if chauffeurs.exists():
        return chauffeurs.first()
    else:
        # Créer un nouveau chauffeur
        return Chauffeur.objects.create(
            nom=nom,
            prenom=prenom,
            numero_permis='À renseigner',
            statut='Actif'
        )

def main():
    print("Préparation des données pour la migration...")
    
    # Collecter tous les noms de conducteurs uniques
    conducteurs = set()
    
    # Récupérer les noms de conducteurs depuis UtilisationActif
    for utilisation in UtilisationActif.objects.all():
        if hasattr(utilisation, 'conducteur') and isinstance(utilisation.conducteur, str) and utilisation.conducteur:
            conducteurs.add(utilisation.conducteur)
    
    # Récupérer les noms de conducteurs depuis UtilisationVehicule
    for utilisation in UtilisationVehicule.objects.all():
        if hasattr(utilisation, 'conducteur') and isinstance(utilisation.conducteur, str) and utilisation.conducteur:
            conducteurs.add(utilisation.conducteur)
    
    # Récupérer les noms de conducteurs depuis IncidentSecurite
    for incident in IncidentSecurite.objects.all():
        if hasattr(incident, 'conducteur') and isinstance(incident.conducteur, str) and incident.conducteur:
            conducteurs.add(incident.conducteur)
    
    print(f"Noms de conducteurs trouvés: {conducteurs}")
    
    # Créer les chauffeurs
    chauffeurs_crees = {}
    for nom_conducteur in conducteurs:
        chauffeur = get_or_create_chauffeur(nom_conducteur)
        chauffeurs_crees[nom_conducteur] = chauffeur
        print(f"Chauffeur créé: {chauffeur.nom} {chauffeur.prenom}")
    
    print("Préparation des données terminée.")
    print("Vous pouvez maintenant appliquer la migration avec l'option --fake.")

if __name__ == "__main__":
    main()
