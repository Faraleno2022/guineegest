#!/usr/bin/env python
"""
Test simplifié pour vérifier les calculs des heures supplémentaires
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models_entreprise import HeureSupplementaire
from django.db.models import Sum
from decimal import Decimal

def test_calculs_simples():
    """Test des calculs des heures supplémentaires"""
    
    print("=" * 60)
    print("TEST SIMPLIFIÉ DES CALCULS")
    print("=" * 60)
    
    # Récupérer toutes les heures supplémentaires
    heures_supp = HeureSupplementaire.objects.all()
    print(f"Nombre total d'heures supplémentaires: {heures_supp.count()}")
    
    if heures_supp.exists():
        print("\nDétail des calculs:")
        print("-" * 60)
        
        for heure in heures_supp:
            print(f"ID: {heure.id}")
            print(f"Employé: {heure.employe.matricule} - {heure.employe.prenom} {heure.employe.nom}")
            print(f"Date: {heure.date}")
            print(f"Heures: {heure.heure_debut} à {heure.heure_fin}")
            print(f"Durée stockée: {heure.duree}")
            print(f"Montant manuel (total_a_payer): {heure.total_a_payer}")
            
            # Test du calcul simple
            if heure.duree and heure.total_a_payer:
                calcul_simple = float(heure.duree) * float(heure.total_a_payer)
                print(f"Calcul simple (durée × montant): {calcul_simple}")
                
                # Test de la méthode du modèle
                try:
                    calcul_methode = heure.calculer_montant_supplementaire_simple()
                    print(f"Méthode du modèle: {calcul_methode}")
                    
                    if abs(calcul_simple - calcul_methode) > 0.01:
                        print("⚠️  PROBLÈME: Différence entre calcul simple et méthode!")
                    else:
                        print("✓ Calculs cohérents")
                        
                except Exception as e:
                    print(f"❌ Erreur méthode: {e}")
            else:
                print("⚠️  Données manquantes pour le calcul")
            
            print("-" * 40)
    
    # Test des agrégations
    print("\nTest des agrégations:")
    total_duree = heures_supp.aggregate(total=Sum('duree'))['total'] or 0
    total_montant_stocke = heures_supp.aggregate(total=Sum('total_a_payer'))['total'] or 0
    
    print(f"Total durée (agrégation): {total_duree}")
    print(f"Total montant stocké (agrégation): {total_montant_stocke}")
    
    # Calcul manuel du montant total
    total_montant_calcule = 0
    for heure in heures_supp:
        if heure.duree and heure.total_a_payer:
            total_montant_calcule += float(heure.duree) * float(heure.total_a_payer)
    
    print(f"Total montant calculé (manuel): {total_montant_calcule}")
    
    if abs(float(total_montant_stocke) - total_montant_calcule) > 0.01:
        print("⚠️  PROBLÈME: Différence entre montant stocké et calculé!")
        print("   Cela indique que total_a_payer ne contient pas les bons montants")
    else:
        print("✓ Agrégations cohérentes")

if __name__ == "__main__":
    try:
        test_calculs_simples()
        print("\n" + "=" * 60)
        print("TEST TERMINÉ")
        print("=" * 60)
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
