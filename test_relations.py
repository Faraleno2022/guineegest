import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Vehicule, Alerte, UtilisationActif
from django.db import connection

def print_separator():
    print('-' * 80)

def test_vehicule_alerte_relation():
    print("Test de la relation Vehicule -> Alerte")
    print_separator()
    
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.all()
    print(f"Nombre de véhicules: {vehicules.count()}")
    
    if vehicules.exists():
        # Prendre le premier véhicule
        vehicule = vehicules.first()
        print(f"Véhicule sélectionné: {vehicule}")
        
        # Récupérer les alertes liées à ce véhicule
        alertes = vehicule.alertes.all()
        print(f"Nombre d'alertes pour ce véhicule: {alertes.count()}")
        
        # Afficher les alertes
        for alerte in alertes:
            print(f"  - {alerte.type_alerte}: {alerte.description} ({alerte.niveau_urgence})")
    else:
        print("Aucun véhicule trouvé.")
    
    print_separator()

def test_alerte_vehicule_relation():
    print("Test de la relation Alerte -> Vehicule")
    print_separator()
    
    # Récupérer toutes les alertes
    alertes = Alerte.objects.all()
    print(f"Nombre d'alertes: {alertes.count()}")
    
    if alertes.exists():
        # Prendre la première alerte
        alerte = alertes.first()
        print(f"Alerte sélectionnée: {alerte.type_alerte} - {alerte.description}")
        
        # Récupérer le véhicule lié à cette alerte
        vehicule = alerte.vehicule
        if vehicule:
            print(f"Véhicule lié: {vehicule}")
        else:
            print("Aucun véhicule lié à cette alerte.")
    else:
        print("Aucune alerte trouvée.")
    
    print_separator()

def test_vehicule_utilisation_relation():
    print("Test de la relation Vehicule -> UtilisationActif")
    print_separator()
    
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.all()
    
    if vehicules.exists():
        # Prendre le premier véhicule
        vehicule = vehicules.first()
        print(f"Véhicule sélectionné: {vehicule}")
        
        # Récupérer les utilisations liées à ce véhicule
        utilisations = vehicule.utilisations.all()
        print(f"Nombre d'utilisations pour ce véhicule: {utilisations.count()}")
        
        # Afficher les utilisations
        for utilisation in utilisations:
            print(f"  - Période: {utilisation.periode} - Jours utilisés: {utilisation.jours_utilises}")
    else:
        print("Aucun véhicule trouvé.")
    
    print_separator()

def test_utilisation_vehicule_relation():
    print("Test de la relation UtilisationActif -> Vehicule")
    print_separator()
    
    # Récupérer toutes les utilisations
    utilisations = UtilisationActif.objects.all()
    print(f"Nombre d'utilisations: {utilisations.count()}")
    
    if utilisations.exists():
        # Prendre la première utilisation
        utilisation = utilisations.first()
        print(f"Utilisation sélectionnée: {utilisation.periode}")
        
        # Récupérer le véhicule lié à cette utilisation
        vehicule = utilisation.vehicule
        if vehicule:
            print(f"Véhicule lié: {vehicule}")
        else:
            print("Aucun véhicule lié à cette utilisation.")
    else:
        print("Aucune utilisation trouvée.")
    
    print_separator()

def test_raw_sql_queries():
    print("Test des requêtes SQL directes")
    print_separator()
    
    with connection.cursor() as cursor:
        # Vérifier la structure de la table fleet_app_alerte
        cursor.execute("PRAGMA table_info(fleet_app_alerte)")
        columns = cursor.fetchall()
        print("Structure de la table fleet_app_alerte:")
        for column in columns:
            print(f"  - {column}")
        
        print_separator()
        
        # Vérifier la structure de la table UtilisationActifs
        cursor.execute("PRAGMA table_info(UtilisationActifs)")
        columns = cursor.fetchall()
        print("Structure de la table UtilisationActifs:")
        for column in columns:
            print(f"  - {column}")
        
        print_separator()
        
        # Vérifier les contraintes de clé étrangère
        cursor.execute("PRAGMA foreign_key_list(fleet_app_alerte)")
        foreign_keys = cursor.fetchall()
        print("Clés étrangères de la table fleet_app_alerte:")
        for fk in foreign_keys:
            print(f"  - {fk}")
        
        print_separator()
        
        # Vérifier les contraintes de clé étrangère
        cursor.execute("PRAGMA foreign_key_list(UtilisationActifs)")
        foreign_keys = cursor.fetchall()
        print("Clés étrangères de la table UtilisationActifs:")
        for fk in foreign_keys:
            print(f"  - {fk}")

if __name__ == "__main__":
    print("=== TEST DES RELATIONS ENTRE LES MODÈLES ===")
    print_separator()
    
    test_vehicule_alerte_relation()
    test_alerte_vehicule_relation()
    test_vehicule_utilisation_relation()
    test_utilisation_vehicule_relation()
    test_raw_sql_queries()
    
    print("=== FIN DES TESTS ===")
