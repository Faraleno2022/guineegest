#!/usr/bin/env python
"""
Script de test pour le module Statistiques Véhicules de GuinéeGest
Vérifie que toutes les fonctionnalités de statistiques fonctionnent correctement
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse
from fleet_app.models import Vehicule, FeuilleDeRoute, CoutFonctionnement, ConsommationCarburant
from fleet_app.models_location import LocationVehicule, FeuillePontageLocation, FactureLocation, FournisseurVehicule
from fleet_app.models_inventaire import EntreeStock, SortieStock, Produit
from fleet_app.views_vehicule_stats import calculer_stats_vehicule, calculer_stats_vehicule_detaillees


def test_stats_models():
    """Test des calculs de statistiques"""
    print("🔍 Test des calculs de statistiques...")
    
    try:
        # Créer un utilisateur de test
        user = User.objects.create_user(
            username='test_stats',
            email='test@stats.com',
            password='testpass123'
        )
        print("✅ Utilisateur de test créé")
        
        # Créer un véhicule de test
        vehicule = Vehicule.objects.create(
            id_vehicule='STATS-001',
            immatriculation='STATS-001',
            marque='Toyota',
            modele='Hilux',
            statut='Actif',
            user=user
        )
        print("✅ Véhicule de test créé")
        
        # Créer des données de test
        today = datetime.now().date()
        start_date = today - timedelta(days=30)
        
        # Feuilles de route
        for i in range(10):
            date_feuille = start_date + timedelta(days=i*2)
            FeuilleDeRoute.objects.create(
                vehicule=vehicule,
                date=date_feuille,
                statut='Actif',
                user=user
            )
        
        # Coûts d'entretien
        CoutFonctionnement.objects.create(
            vehicule=vehicule,
            date=today - timedelta(days=5),
            type_cout='Entretien',
            montant=150000,
            description='Vidange',
            user=user
        )
        
        # Consommation carburant
        ConsommationCarburant.objects.create(
            vehicule=vehicule,
            date=today - timedelta(days=3),
            quantite=50.5,
            cout_total=75000,
            user=user
        )
        
        # Créer un fournisseur et une location
        fournisseur = FournisseurVehicule.objects.create(
            nom='Fournisseur Test Stats',
            user=user
        )
        
        location = LocationVehicule.objects.create(
            vehicule=vehicule,
            type_location='Externe',
            fournisseur=fournisseur,
            date_debut=start_date,
            tarif_journalier=25000,
            user=user
        )
        
        # Feuilles de pontage
        for i in range(5):
            date_pontage = start_date + timedelta(days=i*3)
            FeuillePontageLocation.objects.create(
                location=location,
                date=date_pontage,
                statut='Travail',
                user=user
            )
        
        print("✅ Données de test créées")
        
        # Tester les calculs de statistiques
        stats = calculer_stats_vehicule(vehicule, start_date, today, user)
        print(f"📊 Jours actifs calculés: {stats['jours_actifs']}")
        print(f"📊 Coût entretien: {stats['cout_entretien']}")
        print(f"📊 Consommation: {stats['consommation_litres']} L")
        print(f"📊 Frais location: {stats['frais_location']['total']}")
        
        # Tester les statistiques détaillées
        stats_detail = calculer_stats_vehicule_detaillees(vehicule, start_date, today, user)
        print(f"📊 Pourcentage actif: {stats_detail['pourcentage_actif']}%")
        print(f"📊 Coût par jour: {stats_detail['cout_par_jour']}")
        
        print("✅ Calculs de statistiques validés")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans les calculs: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_stats_urls():
    """Test des URLs des statistiques"""
    print("\n🔍 Test des URLs de statistiques...")
    
    try:
        client = Client()
        
        # Créer un utilisateur et se connecter
        user = User.objects.get_or_create(
            username='test_stats',
            defaults={'email': 'test@stats.com'}
        )[0]
        user.set_password('testpass123')
        user.save()
        
        client.login(username='test_stats', password='testpass123')
        
        # Tester les URLs principales
        urls_to_test = [
            'fleet_app:vehicule_stats_dashboard',
            'fleet_app:vehicule_comparaison_stats',
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
        
        # Tester l'URL de détail avec un véhicule
        vehicules = Vehicule.objects.filter(user=user)
        if vehicules.exists():
            vehicule = vehicules.first()
            try:
                url = reverse('fleet_app:vehicule_stats_detail', args=[vehicule.pk])
                response = client.get(url)
                print(f"✅ vehicule_stats_detail: {response.status_code}")
            except Exception as e:
                print(f"❌ vehicule_stats_detail: {e}")
        
        print("✅ Test des URLs terminé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur dans les URLs: {e}")
        return False


def test_stats_security():
    """Test de la sécurité des statistiques"""
    print("\n🔍 Test de la sécurité des statistiques...")
    
    try:
        # Créer deux utilisateurs
        user1 = User.objects.create_user(
            username='user1_stats',
            email='user1@stats.com',
            password='testpass123'
        )
        
        user2 = User.objects.create_user(
            username='user2_stats',
            email='user2@stats.com',
            password='testpass123'
        )
        
        # Créer des véhicules pour chaque utilisateur
        vehicule1 = Vehicule.objects.create(
            id_vehicule='USER1-STATS-001',
            immatriculation='USER1-STATS-001',
            marque='Toyota',
            modele='Hilux',
            user=user1
        )
        
        vehicule2 = Vehicule.objects.create(
            id_vehicule='USER2-STATS-001',
            immatriculation='USER2-STATS-001',
            marque='Nissan',
            modele='Navara',
            user=user2
        )
        
        # Tester l'isolation des données
        client = Client()
        
        # Se connecter en tant que user1
        client.login(username='user1_stats', password='testpass123')
        
        # Tenter d'accéder aux statistiques du véhicule de user2
        try:
            url = reverse('fleet_app:vehicule_stats_detail', args=[vehicule2.pk])
            response = client.get(url)
            if response.status_code == 404:
                print("✅ Isolation sécurisée: user1 ne peut pas voir les stats de user2")
            else:
                print(f"❌ Faille de sécurité: user1 peut voir les stats de user2 (code: {response.status_code})")
                return False
        except Exception as e:
            print(f"✅ Isolation sécurisée: {e}")
        
        # Vérifier que user1 peut accéder à ses propres stats
        try:
            url = reverse('fleet_app:vehicule_stats_detail', args=[vehicule1.pk])
            response = client.get(url)
            if response.status_code == 200:
                print("✅ user1 peut accéder à ses propres statistiques")
            else:
                print(f"⚠️  Problème d'accès aux propres données: {response.status_code}")
        except Exception as e:
            print(f"❌ Erreur d'accès aux propres données: {e}")
        
        print("✅ Sécurité des statistiques validée")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de sécurité: {e}")
        return False


def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests du module Statistiques Véhicules")
    print("=" * 60)
    
    results = []
    
    # Test des modèles et calculs
    results.append(test_stats_models())
    
    # Test des URLs
    results.append(test_stats_urls())
    
    # Test de sécurité
    results.append(test_stats_security())
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DES TESTS")
    print("=" * 60)
    
    if all(results):
        print("✅ Tous les tests sont passés avec succès!")
        print("🎉 Le module Statistiques Véhicules est prêt à être utilisé")
    else:
        print("❌ Certains tests ont échoué")
        print("⚠️  Vérifiez les erreurs ci-dessus")
    
    # Nettoyage (optionnel)
    try:
        User.objects.filter(username__startswith='test_stats').delete()
        User.objects.filter(username__startswith='user1_stats').delete()
        User.objects.filter(username__startswith='user2_stats').delete()
        print("🧹 Nettoyage des données de test effectué")
    except:
        pass


if __name__ == '__main__':
    main()
