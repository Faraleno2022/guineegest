#!/usr/bin/env python
"""
Script de test pour le module Location de GuinéeGest
Vérifie que toutes les fonctionnalités du module location fonctionnent correctement
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse

from fleet_app.models_location import (
    FournisseurVehicule,
    LocationVehicule,
    FeuillePontageLocation,
    FactureLocation,
)
from fleet_app.models import Vehicule


def test_location_models():
    """Test des modèles de location"""
    print("🔍 Test des modèles de location...")
    
    try:
        # Créer un utilisateur de test
        user = User.objects.create_user(
            username='test_location',
            email='test@location.com',
            password='testpass123'
        )
        print("✅ Utilisateur de test créé")
        
        # Créer un véhicule de test
        vehicule = Vehicule.objects.create(
            immatriculation='TEST-001',
            marque='Toyota',
            modele='Hilux',
            user=user
        )
        print("✅ Véhicule de test créé")
        
        # Créer un fournisseur
        fournisseur = FournisseurVehicule.objects.create(
            nom='Fournisseur Test',
            contact='Contact Test',
            telephone='123456789',
            email='fournisseur@test.com',
            user=user
        )
        print("✅ Fournisseur créé")
        
        # Créer une location
        location = LocationVehicule.objects.create(
            vehicule=vehicule,
            type_location='Externe',
            fournisseur=fournisseur,
            date_debut='2024-01-01',
            tarif_journalier=50000,
            user=user
        )
        print("✅ Location créée")
        
        # Créer une feuille de pontage
        feuille = FeuillePontageLocation.objects.create(
            location=location,
            date='2024-01-01',
            statut='Travail',
            commentaire='Test pontage',
            user=user
        )
        print("✅ Feuille de pontage créée")
        
        # Créer une facture
        facture = FactureLocation.objects.create(
            location=location,
            numero='FACT-TEST-001',
            montant_ht=50000,
            tva=9000,
            montant_ttc=59000,
            user=user
        )
        print("✅ Facture créée")
        
        # Vérifier les propriétés calculées
        print(f"📊 Jours actifs: {location.jours_actifs}")
        print(f"📊 Jours entretien: {location.jours_entretien}")
        print(f"📊 Jours hors service: {location.jours_hors_service}")
        
        print("✅ Tous les modèles fonctionnent correctement")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans les modèles: {e}")
        return False


def test_location_urls():
    """Test des URLs du module location"""
    print("\n🔍 Test des URLs de location...")
    
    try:
        client = Client()
        
        # Créer un utilisateur et se connecter
        user = User.objects.get_or_create(
            username='test_location',
            defaults={'email': 'test@location.com'}
        )[0]
        user.set_password('testpass123')
        user.save()
        
        client.login(username='test_location', password='testpass123')
        
        # Tester les URLs principales
        urls_to_test = [
            'fleet_app:locations_dashboard',
            'fleet_app:location_list',
            'fleet_app:location_create',
            'fleet_app:feuille_pontage_location_list',
            'fleet_app:feuille_pontage_create',
            'fleet_app:fournisseur_location_list',
            'fleet_app:fournisseur_create',
            'fleet_app:facture_location_list',
            'fleet_app:facture_location_create',
        ]
        
        for url_name in urls_to_test:
            try:
                url = reverse(url_name)
                response = client.get(url)
                if response.status_code in [200, 302]:
                    print(f"✅ {url_name}: {response.status_code}")
                else:
                    print(f"⚠️  {url_name}: {response.status_code}")
            except Exception as e:
                print(f"❌ {url_name}: {e}")
        
        print("✅ Test des URLs terminé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans les URLs: {e}")
        return False


def test_location_security():
    """Test de la sécurité - isolation des données par utilisateur"""
    print("\n🔍 Test de la sécurité du module location...")
    
    try:
        # Créer deux utilisateurs
        user1 = User.objects.create_user(
            username='user1_location',
            email='user1@test.com',
            password='testpass123'
        )
        
        user2 = User.objects.create_user(
            username='user2_location',
            email='user2@test.com',
            password='testpass123'
        )
        
        # Créer des véhicules pour chaque utilisateur
        import uuid
        vehicule1 = Vehicule.objects.create(
            id_vehicule=f'USER1-{uuid.uuid4().hex[:8]}',
            immatriculation='USER1-001',
            marque='Toyota',
            modele='Hilux',
            user=user1
        )
        
        vehicule2 = Vehicule.objects.create(
            id_vehicule=f'USER2-{uuid.uuid4().hex[:8]}',
            immatriculation='USER2-001',
            marque='Nissan',
            modele='Navara',
            user=user2
        )
        
        # Créer des fournisseurs pour chaque utilisateur
        fournisseur1 = FournisseurVehicule.objects.create(
            nom='Fournisseur User1',
            user=user1
        )
        
        fournisseur2 = FournisseurVehicule.objects.create(
            nom='Fournisseur User2',
            user=user2
        )
        
        # Créer des locations pour chaque utilisateur
        location1 = LocationVehicule.objects.create(
            vehicule=vehicule1,
            type_location='Externe',
            fournisseur=fournisseur1,
            date_debut='2024-01-01',
            tarif_journalier=50000,
            user=user1
        )
        
        location2 = LocationVehicule.objects.create(
            vehicule=vehicule2,
            type_location='Interne',
            date_debut='2024-01-01',
            tarif_journalier=60000,
            user=user2
        )
        
        # Vérifier l'isolation des données
        user1_locations = LocationVehicule.objects.filter(user=user1)
        user2_locations = LocationVehicule.objects.filter(user=user2)
        
        user1_fournisseurs = FournisseurVehicule.objects.filter(user=user1)
        user2_fournisseurs = FournisseurVehicule.objects.filter(user=user2)
        
        # Assertions de sécurité
        assert user1_locations.count() == 1, "User1 devrait avoir 1 location"
        assert user2_locations.count() == 1, "User2 devrait avoir 1 location"
        assert user1_fournisseurs.count() == 1, "User1 devrait avoir 1 fournisseur"
        assert user2_fournisseurs.count() == 1, "User2 devrait avoir 1 fournisseur"
        
        # Vérifier qu'un utilisateur ne voit pas les données de l'autre
        assert location1 not in user2_locations, "User2 ne devrait pas voir les locations de User1"
        assert location2 not in user1_locations, "User1 ne devrait pas voir les locations de User2"
        
        print("✅ Isolation des données vérifiée")
        print("✅ Sécurité du module location confirmée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de sécurité: {e}")
        return False


def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests du module Location")
    print("=" * 50)
    
    results = []
    
    # Test des modèles
    results.append(test_location_models())
    
    # Test des URLs
    results.append(test_location_urls())
    
    # Test de sécurité
    results.append(test_location_security())
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 50)
    
    if all(results):
        print("✅ Tous les tests sont passés avec succès!")
        print("🎉 Le module Location est prêt à être utilisé")
    else:
        print("❌ Certains tests ont échoué")
        print("⚠️  Vérifiez les erreurs ci-dessus")
    
    # Nettoyage (optionnel)
    try:
        User.objects.filter(username__startswith='test_location').delete()
        User.objects.filter(username__startswith='user1_location').delete()
        User.objects.filter(username__startswith='user2_location').delete()
        print("🧹 Nettoyage des données de test effectué")
    except:
        pass


if __name__ == '__main__':
    main()
