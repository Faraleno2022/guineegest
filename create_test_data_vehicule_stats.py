#!/usr/bin/env python
"""
Script pour créer des données de test pour le module Statistiques Véhicules
Génère des données réalistes pour démontrer toutes les fonctionnalités
"""

import os
import sys
import django
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.contrib.auth.models import User
from fleet_app.models import Vehicule, FeuilleDeRoute, CoutFonctionnement, ConsommationCarburant, Chauffeur, DisponibiliteVehicule
from fleet_app.models_location import LocationVehicule, FeuillePontageLocation, FactureLocation, FournisseurVehicule
from fleet_app.models_inventaire import Produit, EntreeStock, SortieStock


def create_test_user():
    """Créer un utilisateur de test"""
    user, created = User.objects.get_or_create(
        username='demo_stats',
        defaults={
            'email': 'demo@guineegest.com',
            'first_name': 'Demo',
            'last_name': 'Statistics',
            'is_active': True
        }
    )
    if created:
        user.set_password('demo123')
        user.save()
        print("✅ Utilisateur de test créé : demo_stats / demo123")
    else:
        print("✅ Utilisateur de test existant : demo_stats")
    
    return user


def create_test_vehicules(user):
    """Créer des véhicules de test variés"""
    vehicules_data = [
        {
            'id_vehicule': 'TOY-001',
            'immatriculation': 'GN-1234-AB',
            'marque': 'Toyota',
            'modele': 'Hilux',
            'type_moteur': 'Diesel',
            'categorie': '4x4',
            'statut_actuel': 'Actif',
            'date_mise_service': datetime.now().date() - timedelta(days=365*2),
            'kilometrage_initial': 15000
        },
        {
            'id_vehicule': 'NIS-002',
            'immatriculation': 'GN-5678-CD',
            'marque': 'Nissan',
            'modele': 'Navara',
            'type_moteur': 'Diesel',
            'categorie': '4x4',
            'statut_actuel': 'Actif',
            'date_mise_service': datetime.now().date() - timedelta(days=365*3),
            'kilometrage_initial': 25000
        },
        {
            'id_vehicule': 'FOR-003',
            'immatriculation': 'GN-9012-EF',
            'marque': 'Ford',
            'modele': 'Transit',
            'type_moteur': 'Diesel',
            'categorie': 'Camion',
            'statut_actuel': 'En entretien',
            'date_mise_service': datetime.now().date() - timedelta(days=365*1),
            'kilometrage_initial': 8000
        },
        {
            'id_vehicule': 'PEU-004',
            'immatriculation': 'GN-3456-GH',
            'marque': 'Peugeot',
            'modele': '208',
            'type_moteur': 'Essence',
            'categorie': 'Voiture',
            'statut_actuel': 'Actif',
            'date_mise_service': datetime.now().date() - timedelta(days=365*4),
            'kilometrage_initial': 45000
        },
        {
            'id_vehicule': 'MER-005',
            'immatriculation': 'GN-7890-IJ',
            'marque': 'Mercedes',
            'modele': 'Sprinter',
            'type_moteur': 'Diesel',
            'categorie': 'Bus',
            'statut_actuel': 'Hors Service',
            'date_mise_service': datetime.now().date() - timedelta(days=365*5),
            'kilometrage_initial': 120000
        },
        {
            'id_vehicule': 'HON-006',
            'immatriculation': 'GN-2468-KL',
            'marque': 'Honda',
            'modele': 'CRV',
            'type_moteur': 'Essence',
            'categorie': '4x4',
            'statut_actuel': 'Actif',
            'date_mise_service': datetime.now().date() - timedelta(days=365*1),
            'kilometrage_initial': 12000
        },
        {
            'id_vehicule': 'YAM-007',
            'immatriculation': 'GN-1357-MN',
            'marque': 'Yamaha',
            'modele': 'MT-07',
            'type_moteur': 'Essence',
            'categorie': 'Moto',
            'statut_actuel': 'Actif',
            'date_mise_service': datetime.now().date() - timedelta(days=365*2),
            'kilometrage_initial': 8500
        },
        {
            'id_vehicule': 'HYU-008',
            'immatriculation': 'GN-9753-OP',
            'marque': 'Hyundai',
            'modele': 'Tucson',
            'type_moteur': 'Essence',
            'categorie': '4x4',
            'statut_actuel': 'Inactif',
            'date_mise_service': datetime.now().date() - timedelta(days=365*3),
            'kilometrage_initial': 35000
        }
    ]
    
    vehicules = []
    for data in vehicules_data:
        vehicule, created = Vehicule.objects.get_or_create(
            id_vehicule=data['id_vehicule'],
            defaults={**data, 'user': user}
        )
        if created:
            print(f"✅ Véhicule créé : {vehicule.immatriculation} - {vehicule.marque} {vehicule.modele}")
        vehicules.append(vehicule)
    
    return vehicules


def create_test_fournisseurs(user):
    """Créer des fournisseurs de véhicules de test"""
    fournisseurs_data = [
        {
            'nom': 'AutoRent Guinée',
            'contact': 'Mamadou Diallo',
            'telephone': '+224 622 123 456',
            'email': 'contact@autorent-gn.com',
            'adresse': 'Quartier Almamya, Conakry'
        },
        {
            'nom': 'Location Express',
            'contact': 'Fatoumata Camara',
            'telephone': '+224 664 789 012',
            'email': 'info@locationexpress.gn',
            'adresse': 'Matoto, Conakry'
        },
        {
            'nom': 'Fleet Solutions',
            'contact': 'Alpha Bah',
            'telephone': '+224 655 345 678',
            'email': 'alpha@fleetsolutions.gn',
            'adresse': 'Ratoma, Conakry'
        }
    ]
    
    fournisseurs = []
    for data in fournisseurs_data:
        fournisseur, created = FournisseurVehicule.objects.get_or_create(
            nom=data['nom'],
            user=user,
            defaults=data
        )
        if created:
            print(f"✅ Fournisseur créé : {fournisseur.nom}")
        fournisseurs.append(fournisseur)
    
    return fournisseurs


def create_test_chauffeurs(user):
    """Créer des chauffeurs de test"""
    chauffeurs_data = [
        {
            'nom': 'Diallo',
            'prenom': 'Mamadou',
            'telephone': '+224 622 111 222',
            'numero_permis': 'GN123456789',
            'date_embauche': datetime.now().date() - timedelta(days=365*2)
        },
        {
            'nom': 'Camara',
            'prenom': 'Fatoumata',
            'telephone': '+224 664 333 444',
            'numero_permis': 'GN987654321',
            'date_embauche': datetime.now().date() - timedelta(days=365*3)
        },
        {
            'nom': 'Bah',
            'prenom': 'Alpha',
            'telephone': '+224 655 555 666',
            'numero_permis': 'GN456789123',
            'date_embauche': datetime.now().date() - timedelta(days=365*1)
        },
        {
            'nom': 'Touré',
            'prenom': 'Aminata',
            'telephone': '+224 628 777 888',
            'numero_permis': 'GN789123456',
            'date_embauche': datetime.now().date() - timedelta(days=365*4)
        }
    ]
    
    chauffeurs = []
    for data in chauffeurs_data:
        chauffeur, created = Chauffeur.objects.get_or_create(
            numero_permis=data['numero_permis'],
            defaults=data
        )
        if created:
            print(f"✅ Chauffeur créé : {chauffeur.prenom} {chauffeur.nom}")
        chauffeurs.append(chauffeur)
    
    return chauffeurs


def create_test_feuilles_route(vehicules, chauffeurs, user):
    """Créer des feuilles de route pour les 6 derniers mois"""
    print("📋 Création des feuilles de route...")
    
    objets = ['Mission', 'Livraison', 'Personnel']
    destinations = ['Conakry', 'Kindia', 'Mamou', 'Labé', 'Kankan', 'N\'Zérékoré', 'Boké', 'Faranah']
    
    start_date = datetime.now().date() - timedelta(days=180)  # 6 mois
    end_date = datetime.now().date()
    
    created_count = 0
    for vehicule in vehicules:
        current_date = start_date
        while current_date <= end_date:
            # Créer une feuille tous les 3-5 jours en moyenne
            if random.random() < 0.25:  # 25% de chance par jour
                chauffeur = random.choice(chauffeurs)
                
                # Données de base
                km_depart = vehicule.kilometrage_initial + random.randint(0, 50000)
                distance = random.randint(50, 500)
                km_retour = km_depart + distance
                
                carburant_depart = random.uniform(20, 80)
                consommation_100km = random.uniform(6, 15)
                carburant_utilise = (distance * consommation_100km) / 100
                carburant_retour = max(0, carburant_depart - carburant_utilise)
                
                heure_depart = datetime.now().time().replace(
                    hour=random.randint(6, 10),
                    minute=random.randint(0, 59)
                )
                
                duree_mission = random.randint(2, 10)  # heures
                heure_retour = (datetime.combine(current_date, heure_depart) + 
                               timedelta(hours=duree_mission)).time()
                
                feuille, created = FeuilleDeRoute.objects.get_or_create(
                    vehicule=vehicule,
                    chauffeur=chauffeur,
                    date_depart=current_date,
                    defaults={
                        'heure_depart': heure_depart,
                        'destination': random.choice(destinations),
                        'objet_deplacement': random.choice(objets),
                        'signature_gestionnaire': True,
                        'km_depart': km_depart,
                        'carburant_depart': round(carburant_depart, 2),
                        'km_retour': km_retour,
                        'carburant_retour': round(carburant_retour, 2),
                        'date_retour': current_date,
                        'heure_retour': heure_retour,
                        'signature_chauffeur': True,
                        'distance_parcourue': distance,
                        'carburant_utilise': round(carburant_utilise, 2),
                        'consommation': round(consommation_100km, 2),
                        'alerte_surconsommation': consommation_100km > 12
                    }
                )
                if created:
                    created_count += 1
            
            current_date += timedelta(days=1)
    
    print(f"✅ {created_count} feuilles de route créées")


def create_test_disponibilites(vehicules, user):
    """Créer des données de disponibilité des véhicules"""
    print("📊 Création des disponibilités...")
    
    created_count = 0
    start_date = datetime.now().date() - timedelta(days=180)
    
    for vehicule in vehicules:
        # Créer des périodes de disponibilité mensuelles
        current_date = start_date
        while current_date <= datetime.now().date():
            # Période d'un mois
            if current_date.day == 1:  # Premier jour du mois
                fin_mois = (current_date.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)
                
                # Calculer la disponibilité selon le statut du véhicule
                if vehicule.statut_actuel == 'Actif':
                    heures_disponibles = random.randint(600, 720)  # 20-24h par jour
                elif vehicule.statut_actuel == 'En entretien':
                    heures_disponibles = random.randint(300, 500)  # 10-16h par jour
                elif vehicule.statut_actuel == 'Hors Service':
                    heures_disponibles = random.randint(0, 200)   # 0-6h par jour
                else:  # Inactif
                    heures_disponibles = random.randint(100, 400)  # 3-13h par jour
                
                jours_mois = (fin_mois - current_date).days + 1
                heures_totales = jours_mois * 24
                pourcentage = (heures_disponibles / heures_totales) * 100
                
                jours_hs = random.randint(0, max(1, int(jours_mois * 0.1)))  # Max 10% du mois
                
                disponibilite, created = DisponibiliteVehicule.objects.get_or_create(
                    vehicule=vehicule,
                    date_debut=current_date,
                    date_fin=fin_mois,
                    user=user,
                    defaults={
                        'heures_disponibles': heures_disponibles,
                        'heures_totales': heures_totales,
                        'disponibilite_pourcentage': round(pourcentage, 2),
                        'raison_indisponibilite': random.choice([
                            'Entretien préventif',
                            'Réparation',
                            'Panne',
                            'Maintenance',
                            ''
                        ]) if pourcentage < 80 else '',
                        'periode': f"{current_date.strftime('%B %Y')}",
                        'jours_total_periode': jours_mois,
                        'jours_hors_service': jours_hs
                    }
                )
                if created:
                    created_count += 1
            
            current_date += timedelta(days=1)
    
    print(f"✅ {created_count} disponibilités créées")


def create_test_couts_fonctionnement(vehicules, user):
    """Créer des coûts de fonctionnement (entretien)"""
    print("💰 Création des coûts d'entretien...")
    
    types_entretien = [
        ('Vidange moteur', 75000, 150000),
        ('Changement filtres', 25000, 50000),
        ('Réparation freins', 100000, 300000),
        ('Changement pneus', 200000, 800000),
        ('Réparation transmission', 300000, 1000000),
        ('Entretien climatisation', 50000, 200000),
        ('Réparation électrique', 75000, 400000),
        ('Carrosserie', 100000, 500000)
    ]
    
    created_count = 0
    start_date = datetime.now().date() - timedelta(days=180)
    
    for vehicule in vehicules:
        # Nombre d'interventions selon l'âge et le type de véhicule
        nb_interventions = random.randint(3, 12)
        
        for _ in range(nb_interventions):
            date_intervention = start_date + timedelta(days=random.randint(0, 180))
            type_entretien, cout_min, cout_max = random.choice(types_entretien)
            montant = random.randint(cout_min, cout_max)
            
            cout, created = CoutFonctionnement.objects.get_or_create(
                vehicule=vehicule,
                date=date_intervention,
                type_cout='Entretien',
                montant=montant,
                user=user,
                defaults={
                    'description': type_entretien,
                    'fournisseur': random.choice(['Garage Central', 'Auto Service', 'Mécanique Express', 'Atelier Pro'])
                }
            )
            if created:
                created_count += 1
    
    print(f"✅ {created_count} coûts d'entretien créés")


def create_test_consommation_carburant(vehicules, user):
    """Créer des données de consommation carburant"""
    print("⛽ Création des consommations carburant...")
    
    created_count = 0
    start_date = datetime.now().date() - timedelta(days=180)
    
    for vehicule in vehicules:
        # Consommation selon le type de véhicule
        if vehicule.categorie == 'Moto':
            conso_constructeur = random.uniform(3, 5)  # L/100km
        elif vehicule.categorie == 'Voiture':
            conso_constructeur = random.uniform(7, 12)
        elif vehicule.categorie == '4x4':
            conso_constructeur = random.uniform(10, 15)
        elif vehicule.categorie == 'Camion':
            conso_constructeur = random.uniform(15, 25)
        else:  # Bus
            conso_constructeur = random.uniform(20, 35)
        
        # Créer des mesures de consommation tous les 15-30 jours
        current_date = start_date
        while current_date <= datetime.now().date():
            if random.random() < 0.05:  # 5% de chance par jour (environ tous les 20 jours)
                # Première mesure
                date_plein1 = current_date
                km_plein1 = vehicule.kilometrage_initial + random.randint(0, 50000)
                
                # Deuxième mesure (7-15 jours plus tard)
                jours_entre_pleins = random.randint(7, 15)
                date_plein2 = date_plein1 + timedelta(days=jours_entre_pleins)
                
                # Distance parcourue
                distance = random.randint(200, 1500)
                km_plein2 = km_plein1 + distance
                
                # Litres ajoutés (avec variation réaliste)
                conso_reelle = conso_constructeur * random.uniform(0.8, 1.3)  # ±30% variation
                litres_ajoutes = (distance * conso_reelle) / 100
                
                # Calcul de la consommation aux 100km
                consommation_100km = (litres_ajoutes * 100) / distance
                
                # Écart avec le constructeur
                ecart = consommation_100km - conso_constructeur
                
                consommation, created = ConsommationCarburant.objects.get_or_create(
                    vehicule=vehicule,
                    date_plein1=date_plein1,
                    date_plein2=date_plein2,
                    user=user,
                    defaults={
                        'km_plein1': km_plein1,
                        'km_plein2': km_plein2,
                        'litres_ajoutes': round(litres_ajoutes, 2),
                        'distance_parcourue': distance,
                        'consommation_100km': round(consommation_100km, 2),
                        'consommation_constructeur': round(conso_constructeur, 2),
                        'ecart_constructeur': round(ecart, 2)
                    }
                )
                if created:
                    created_count += 1
                    current_date = date_plein2  # Avancer à la date du 2ème plein
            
            current_date += timedelta(days=1)
    
    print(f"✅ {created_count} consommations carburant créées")


def create_test_locations(vehicules, fournisseurs, user):
    """Créer des locations de véhicules"""
    print("🚗 Création des locations...")
    
    created_count = 0
    start_date = datetime.now().date() - timedelta(days=120)  # 4 mois
    
    # Sélectionner quelques véhicules pour les locations externes
    vehicules_location = random.sample(vehicules, min(4, len(vehicules)))
    
    for vehicule in vehicules_location:
        # Créer 1-3 locations par véhicule
        nb_locations = random.randint(1, 3)
        
        for i in range(nb_locations):
            date_debut = start_date + timedelta(days=random.randint(0, 90))
            duree = random.randint(15, 60)  # 15 à 60 jours
            date_fin = date_debut + timedelta(days=duree)
            
            type_location = random.choice(['Interne', 'Externe'])
            fournisseur = random.choice(fournisseurs) if type_location == 'Externe' else None
            
            # Tarif selon le type de véhicule
            if vehicule.categorie == 'Moto':
                tarif_base = random.randint(15000, 25000)
            elif vehicule.categorie == 'Voiture':
                tarif_base = random.randint(30000, 50000)
            elif vehicule.categorie == '4x4':
                tarif_base = random.randint(50000, 80000)
            elif vehicule.categorie == 'Camion':
                tarif_base = random.randint(70000, 120000)
            else:  # Bus
                tarif_base = random.randint(80000, 150000)
            
            location, created = LocationVehicule.objects.get_or_create(
                vehicule=vehicule,
                date_debut=date_debut,
                user=user,
                defaults={
                    'type_location': type_location,
                    'fournisseur': fournisseur,
                    'date_fin': date_fin,
                    'tarif_journalier': tarif_base,
                    'statut': random.choice(['Active', 'Inactive', 'Clôturée']),
                    'motif': random.choice(['Mission terrain', 'Transport personnel', 'Livraison', 'Déplacement officiel'])
                }
            )
            if created:
                created_count += 1
                
                # Créer des feuilles de pontage pour cette location
                create_test_pontages(location, user)
    
    print(f"✅ {created_count} locations créées")


def create_test_pontages(location, user):
    """Créer des feuilles de pontage pour une location"""
    current_date = location.date_debut
    end_date = min(location.date_fin or datetime.now().date(), datetime.now().date())
    
    while current_date <= end_date:
        # 80% de chance d'avoir une feuille de pontage par jour
        if random.random() < 0.8:
            statut = random.choices(
                ['Travail', 'Entretien', 'Hors service'],
                weights=[85, 10, 5]
            )[0]
            
            FeuillePontageLocation.objects.get_or_create(
                location=location,
                date=current_date,
                user=user,
                defaults={
                    'statut': statut,
                    'commentaire': random.choice([
                        'Mission accomplie',
                        'Transport effectué',
                        'Maintenance préventive',
                        'Réparation mineure',
                        'RAS',
                        ''
                    ])
                }
            )
        
        current_date += timedelta(days=1)


def create_test_factures(user):
    """Créer des factures de location"""
    print("🧾 Création des factures...")
    
    locations = LocationVehicule.objects.filter(user=user)
    created_count = 0
    
    for location in locations:
        # 70% de chance d'avoir une facture
        if random.random() < 0.7:
            # Calculer le montant basé sur les jours de travail
            jours_travail = location.feuilles.filter(statut='Travail').count()
            
            if jours_travail > 0:
                montant_ht = jours_travail * location.tarif_journalier
                tva = montant_ht * 0.18  # TVA 18%
                montant_ttc = montant_ht + tva
                
                numero = f"FACT-{location.pk}-{random.randint(1000, 9999)}"
                
                facture, created = FactureLocation.objects.get_or_create(
                    location=location,
                    user=user,
                    defaults={
                        'numero': numero,
                        'date_facture': location.date_debut + timedelta(days=random.randint(5, 30)),
                        'montant_ht': montant_ht,
                        'tva': tva,
                        'montant_ttc': montant_ttc,
                        'statut': random.choice(['Brouillon', 'Envoyée', 'Payée']),
                        'date_echeance': location.date_debut + timedelta(days=random.randint(30, 60))
                    }
                )
                if created:
                    created_count += 1
    
    print(f"✅ {created_count} factures créées")


def create_test_pieces_detachees(vehicules, user):
    """Créer des données de pièces détachées utilisées"""
    print("🔧 Création des sorties de pièces détachées...")
    
    # Créer quelques produits (pièces détachées) si ils n'existent pas
    pieces_data = [
        ('Filtre à huile', 15000, 'Pièce'),
        ('Filtre à air', 12000, 'Pièce'),
        ('Plaquettes de frein', 45000, 'Pièce'),
        ('Disque de frein', 85000, 'Pièce'),
        ('Pneu', 180000, 'Pièce'),
        ('Batterie', 120000, 'Pièce'),
        ('Amortisseur', 95000, 'Pièce'),
        ('Courroie', 25000, 'Pièce'),
        ('Bougie', 8000, 'Pièce'),
        ('Huile moteur (5L)', 35000, 'Consommable')
    ]
    
    produits = []
    for nom, prix, type_produit in pieces_data:
        produit, created = Produit.objects.get_or_create(
            nom=nom,
            defaults={
                'prix_unitaire': prix,
                'type_produit': type_produit,
                'stock_minimum': 5,
                'stock_actuel': random.randint(10, 50),
                'unite': 'Unité'
            }
        )
        produits.append(produit)
    
    # Créer des sorties de stock pour les véhicules
    created_count = 0
    start_date = datetime.now().date() - timedelta(days=180)
    
    for vehicule in vehicules:
        # Nombre de sorties selon l'activité du véhicule
        nb_sorties = random.randint(5, 20)
        
        for _ in range(nb_sorties):
            date_sortie = start_date + timedelta(days=random.randint(0, 180))
            produit = random.choice(produits)
            quantite = random.randint(1, 4)
            
            # Note: Le modèle SortieStock pourrait ne pas avoir de champ user
            # On essaie de créer avec, sinon sans
            try:
                sortie, created = SortieStock.objects.get_or_create(
                    produit=produit,
                    date=date_sortie,
                    vehicule=vehicule,
                    quantite=quantite,
                    defaults={
                        'prix_unitaire': produit.prix_unitaire,
                        'motif': 'Entretien véhicule',
                        'destination': f'Véhicule {vehicule.immatriculation}',
                        'stock_avant': produit.stock_actuel + quantite,
                        'stock_apres': produit.stock_actuel
                    }
                )
                if created:
                    created_count += 1
            except Exception as e:
                # Si le modèle n'a pas de champ user, on continue
                print(f"⚠️  Impossible de créer sortie stock: {e}")
                continue
    
    print(f"✅ {created_count} sorties de pièces créées")


def main():
    """Fonction principale pour créer toutes les données de test"""
    print("🚀 Création des données de test pour le module Statistiques Véhicules")
    print("=" * 70)
    
    try:
        # 1. Créer l'utilisateur de test
        user = create_test_user()
        
        # 2. Créer les véhicules
        vehicules = create_test_vehicules(user)
        
        # 3. Créer les fournisseurs
        fournisseurs = create_test_fournisseurs(user)
        
        # 4. Créer les chauffeurs
        chauffeurs = create_test_chauffeurs(user)
        
        # 5. Créer les feuilles de route
        create_test_feuilles_route(vehicules, chauffeurs, user)
        
        # 6. Créer les disponibilités
        create_test_disponibilites(vehicules, user)
        
        # 7. Créer les coûts d'entretien
        create_test_couts_fonctionnement(vehicules, user)
        
        # 8. Créer les consommations carburant
        create_test_consommation_carburant(vehicules, user)
        
        # 9. Créer les locations
        create_test_locations(vehicules, fournisseurs, user)
        
        # 10. Créer les factures
        create_test_factures(user)
        
        # 11. Créer les sorties de pièces détachées
        create_test_pieces_detachees(vehicules, user)
        
        print("\n" + "=" * 70)
        print("🎉 DONNÉES DE TEST CRÉÉES AVEC SUCCÈS !")
        print("=" * 70)
        print("📊 Résumé des données créées :")
        print(f"   👤 Utilisateur : demo_stats (mot de passe: demo123)")
        print(f"   🚗 Véhicules : {len(vehicules)}")
        print(f"   🏢 Fournisseurs : {len(fournisseurs)}")
        print(f"   📋 Feuilles de route : {FeuilleDeRoute.objects.filter(user=user).count()}")
        print(f"   💰 Coûts d'entretien : {CoutFonctionnement.objects.filter(user=user).count()}")
        print(f"   ⛽ Consommations carburant : {ConsommationCarburant.objects.filter(user=user).count()}")
        print(f"   🚗 Locations : {LocationVehicule.objects.filter(user=user).count()}")
        print(f"   📋 Feuilles de pontage : {FeuillePontageLocation.objects.filter(user=user).count()}")
        print(f"   🧾 Factures : {FactureLocation.objects.filter(user=user).count()}")
        
        print("\n🌐 Pour tester le module :")
        print("   1. Connectez-vous avec : demo_stats / demo123")
        print("   2. Allez dans Menu KPIs → Statistiques Véhicules")
        print("   3. Testez les filtres dynamiques et les fonctionnalités")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création des données : {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
