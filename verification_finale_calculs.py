#!/usr/bin/env python
"""
Vérification finale des calculs des heures supplémentaires
Test complet de tous les aspects du système
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models_entreprise import HeureSupplementaire, Employe, DataSynchronizer
from django.contrib.auth.models import User
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime, date, time

def creer_donnees_test():
    """Créer des données de test pour vérifier les calculs"""
    
    print("=" * 60)
    print("CRÉATION DES DONNÉES DE TEST")
    print("=" * 60)
    
    # Récupérer ou créer un utilisateur
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
    )
    
    if created:
        print(f"✓ Utilisateur créé: {user.username}")
    else:
        print(f"✓ Utilisateur existant: {user.username}")
    
    # Récupérer ou créer un employé
    employe, created = Employe.objects.get_or_create(
        matricule='TEST001',
        defaults={
            'prenom': 'Jean',
            'nom': 'Dupont',
            'fonction': 'Testeur',
            'salaire_journalier': Decimal('50000'),
            'user': user
        }
    )
    
    if created:
        print(f"✓ Employé créé: {employe.matricule} - {employe.prenom} {employe.nom}")
    else:
        print(f"✓ Employé existant: {employe.matricule} - {employe.prenom} {employe.nom}")
    
    # Supprimer les anciennes heures supplémentaires de test
    HeureSupplementaire.objects.filter(employe=employe).delete()
    
    # Créer des heures supplémentaires de test
    test_cases = [
        {
            'date': date(2025, 7, 24),
            'heure_debut': time(8, 0),
            'heure_fin': time(12, 2),  # 4h02min = 4.03h
            'montant_manuel': Decimal('80000'),  # 80,000 GNF par heure
            'description': 'Test calcul normal'
        },
        {
            'date': date(2025, 7, 25),
            'heure_debut': time(8, 0),
            'heure_fin': time(8, 0),  # Cas spécial = 24h
            'montant_manuel': Decimal('50000'),  # 50,000 GNF par heure
            'description': 'Test cas spécial (24h)'
        },
        {
            'date': date(2025, 7, 26),
            'heure_debut': time(22, 0),
            'heure_fin': time(6, 0),  # Sur 2 jours = 8h
            'montant_manuel': Decimal('100000'),  # 100,000 GNF par heure
            'description': 'Test sur 2 jours'
        }
    ]
    
    heures_creees = []
    for test_case in test_cases:
        # Calculer la durée selon la logique du formulaire
        from datetime import datetime, timedelta
        
        debut = datetime.combine(datetime.today(), test_case['heure_debut'])
        fin = datetime.combine(datetime.today(), test_case['heure_fin'])
        
        if debut == fin:
            duree_calculee = Decimal('24.00')
        else:
            if fin < debut:
                fin = fin + timedelta(days=1)
            duree_timedelta = fin - debut
            duree_calculee = Decimal(str(duree_timedelta.total_seconds() / 3600)).quantize(Decimal('0.01'))
        
        heure = HeureSupplementaire.objects.create(
            employe=employe,
            date=test_case['date'],
            heure_debut=test_case['heure_debut'],
            heure_fin=test_case['heure_fin'],
            duree=duree_calculee,
            total_a_payer=test_case['montant_manuel'],
            autorise_par='Test System'
        )
        
        heures_creees.append({
            'heure': heure,
            'description': test_case['description'],
            'duree_attendue': duree_calculee,
            'montant_attendu': duree_calculee * test_case['montant_manuel']
        })
        
        print(f"✓ Créé: {test_case['description']} - {duree_calculee}h × {test_case['montant_manuel']} = {duree_calculee * test_case['montant_manuel']}")
    
    return user, employe, heures_creees

def tester_calculs(employe, heures_creees):
    """Tester tous les calculs"""
    
    print("\n" + "=" * 60)
    print("TEST DES CALCULS")
    print("=" * 60)
    
    total_heures_attendu = Decimal('0')
    total_montant_attendu = Decimal('0')
    
    print("Vérification des calculs individuels:")
    print("-" * 40)
    
    for test_data in heures_creees:
        heure = test_data['heure']
        description = test_data['description']
        duree_attendue = test_data['duree_attendue']
        montant_attendu = test_data['montant_attendu']
        
        print(f"\n{description}:")
        print(f"  Durée stockée: {heure.duree}")
        print(f"  Durée attendue: {duree_attendue}")
        print(f"  Montant manuel: {heure.total_a_payer}")
        
        # Test calcul simple
        calcul_simple = heure.duree * heure.total_a_payer
        print(f"  Calcul simple: {heure.duree} × {heure.total_a_payer} = {calcul_simple}")
        
        # Test méthode du modèle
        calcul_methode = heure.calculer_montant_supplementaire_simple()
        print(f"  Méthode modèle: {calcul_methode}")
        
        # Vérifications
        if abs(heure.duree - duree_attendue) > Decimal('0.01'):
            print(f"  ❌ ERREUR: Durée incorrecte!")
        else:
            print(f"  ✓ Durée correcte")
        
        if abs(calcul_simple - montant_attendu) > Decimal('0.01'):
            print(f"  ❌ ERREUR: Calcul simple incorrect!")
        else:
            print(f"  ✓ Calcul simple correct")
        
        if abs(Decimal(str(calcul_methode)) - montant_attendu) > Decimal('0.01'):
            print(f"  ❌ ERREUR: Méthode modèle incorrecte!")
        else:
            print(f"  ✓ Méthode modèle correcte")
        
        total_heures_attendu += duree_attendue
        total_montant_attendu += montant_attendu
    
    print(f"\n" + "-" * 40)
    print(f"TOTAUX ATTENDUS:")
    print(f"  Total heures: {total_heures_attendu}")
    print(f"  Total montant: {total_montant_attendu}")
    
    return total_heures_attendu, total_montant_attendu

def tester_data_synchronizer(employe, total_heures_attendu, total_montant_attendu):
    """Tester DataSynchronizer"""
    
    print("\n" + "=" * 60)
    print("TEST DATASYNCHRONIZER")
    print("=" * 60)
    
    # Test DataSynchronizer
    donnees = DataSynchronizer.get_donnees_aggregees_employe(
        employe, 
        datetime.now().month, 
        datetime.now().year
    )
    
    print(f"DataSynchronizer - total_heures_supp: {donnees['total_heures_supp']}")
    print(f"DataSynchronizer - montant_heures_supp: {donnees['montant_heures_supp']}")
    
    # Vérifications
    if abs(float(donnees['total_heures_supp']) - float(total_heures_attendu)) > 0.01:
        print(f"❌ ERREUR: Total heures incorrect dans DataSynchronizer!")
        print(f"   Attendu: {total_heures_attendu}, Obtenu: {donnees['total_heures_supp']}")
    else:
        print(f"✓ Total heures correct dans DataSynchronizer")
    
    if abs(float(donnees['montant_heures_supp']) - float(total_montant_attendu)) > 0.01:
        print(f"❌ ERREUR: Total montant incorrect dans DataSynchronizer!")
        print(f"   Attendu: {total_montant_attendu}, Obtenu: {donnees['montant_heures_supp']}")
    else:
        print(f"✓ Total montant correct dans DataSynchronizer")

def nettoyer_donnees_test():
    """Nettoyer les données de test"""
    
    print("\n" + "=" * 60)
    print("NETTOYAGE DES DONNÉES DE TEST")
    print("=" * 60)
    
    try:
        employe = Employe.objects.get(matricule='TEST001')
        HeureSupplementaire.objects.filter(employe=employe).delete()
        print("✓ Heures supplémentaires de test supprimées")
        
        # Optionnel: supprimer l'employé de test
        # employe.delete()
        # print("✓ Employé de test supprimé")
        
    except Employe.DoesNotExist:
        print("✓ Aucune donnée de test à nettoyer")

if __name__ == "__main__":
    try:
        # Créer les données de test
        user, employe, heures_creees = creer_donnees_test()
        
        # Tester les calculs
        total_heures_attendu, total_montant_attendu = tester_calculs(employe, heures_creees)
        
        # Tester DataSynchronizer
        tester_data_synchronizer(employe, total_heures_attendu, total_montant_attendu)
        
        # Nettoyer
        nettoyer_donnees_test()
        
        print("\n" + "=" * 60)
        print("VÉRIFICATION TERMINÉE")
        print("=" * 60)
        
    except Exception as e:
        print(f"Erreur lors de la vérification: {e}")
        import traceback
        traceback.print_exc()
