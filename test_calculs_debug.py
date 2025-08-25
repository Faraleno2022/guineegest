#!/usr/bin/env python
"""
Script de test pour vérifier les calculs des heures supplémentaires
et identifier les problèmes de récupération des informations
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models_entreprise import HeureSupplementaire, Employe, DataSynchronizer
from django.contrib.auth.models import User
from datetime import datetime, date
from decimal import Decimal

def test_calculs_heures_supplementaires():
    """Test des calculs des heures supplémentaires"""
    
    print("=" * 60)
    print("TEST DES CALCULS DES HEURES SUPPLÉMENTAIRES")
    print("=" * 60)
    
    # Récupérer tous les utilisateurs
    users = User.objects.all()
    print(f"Nombre d'utilisateurs trouvés: {users.count()}")
    
    for user in users:
        print(f"\n--- UTILISATEUR: {user.username} ---")
        
        # Récupérer les employés de cet utilisateur
        employes = Employe.objects.filter(user=user)
        print(f"Nombre d'employés: {employes.count()}")
        
        for employe in employes:
            print(f"\n  Employé: {employe.matricule} - {employe.prenom} {employe.nom}")
            
            # Récupérer les heures supplémentaires de cet employé
            heures_supp = HeureSupplementaire.objects.filter(employe=employe)
            print(f"  Nombre d'heures supplémentaires: {heures_supp.count()}")
            
            if heures_supp.exists():
                print("  Détail des heures supplémentaires:")
                total_heures = Decimal('0')
                total_montant_calcule = Decimal('0')
                total_montant_stocke = Decimal('0')
                
                for heure in heures_supp:
                    print(f"    - Date: {heure.date}")
                    print(f"      Début: {heure.heure_debut}, Fin: {heure.heure_fin}")
                    print(f"      Durée stockée: {heure.duree}")
                    print(f"      Montant manuel (total_a_payer): {heure.total_a_payer}")
                    
                    # Calculer le montant selon la règle simplifiée
                    montant_calcule = float(heure.duree) * float(heure.total_a_payer) if heure.total_a_payer else 0
                    print(f"      Montant calculé (durée × montant): {montant_calcule}")
                    
                    # Utiliser la méthode du modèle
                    montant_methode = heure.calculer_montant_supplementaire_simple()
                    print(f"      Montant via méthode: {montant_methode}")
                    
                    total_heures += heure.duree
                    total_montant_calcule += Decimal(str(montant_calcule))
                    total_montant_stocke += heure.total_a_payer if heure.total_a_payer else Decimal('0')
                    print()
                
                print(f"  TOTAUX pour {employe.matricule}:")
                print(f"    Total heures: {total_heures}")
                print(f"    Total montant calculé: {total_montant_calcule}")
                print(f"    Total montant stocké: {total_montant_stocke}")
                
                # Tester DataSynchronizer
                print(f"  TEST DataSynchronizer:")
                donnees = DataSynchronizer.get_donnees_aggregees_employe(
                    employe, 
                    datetime.now().month, 
                    datetime.now().year
                )
                print(f"    DataSynchronizer - total_heures_supp: {donnees['total_heures_supp']}")
                print(f"    DataSynchronizer - montant_heures_supp: {donnees['montant_heures_supp']}")
                
                # Vérifier la cohérence
                if abs(float(donnees['total_heures_supp']) - float(total_heures)) > 0.01:
                    print(f"    ⚠️  PROBLÈME: Incohérence dans le total des heures!")
                
                if abs(float(donnees['montant_heures_supp']) - float(total_montant_calcule)) > 0.01:
                    print(f"    ⚠️  PROBLÈME: Incohérence dans le montant calculé!")
                
                print("-" * 40)

def test_problemes_specifiques():
    """Test des problèmes spécifiques identifiés"""
    
    print("\n" + "=" * 60)
    print("TEST DES PROBLÈMES SPÉCIFIQUES")
    print("=" * 60)
    
    # Test 1: Vérifier les champs manquants
    print("1. Vérification des champs du modèle HeureSupplementaire:")
    heure_test = HeureSupplementaire.objects.first()
    if heure_test:
        print(f"   - duree: {hasattr(heure_test, 'duree')} ✓" if hasattr(heure_test, 'duree') else "   - duree: ❌")
        print(f"   - total_a_payer: {hasattr(heure_test, 'total_a_payer')} ✓" if hasattr(heure_test, 'total_a_payer') else "   - total_a_payer: ❌")
        print(f"   - nombre_heures: {hasattr(heure_test, 'nombre_heures')} ❌" if not hasattr(heure_test, 'nombre_heures') else "   - nombre_heures: ✓")
        print(f"   - duree_calculee: {hasattr(heure_test, 'duree_calculee')} ❌" if not hasattr(heure_test, 'duree_calculee') else "   - duree_calculee: ✓")
    
    # Test 2: Vérifier les calculs de durée
    print("\n2. Test des calculs de durée:")
    from datetime import time
    test_cases = [
        (time(8, 0), time(12, 2)),  # 4h02min = 4.033h
        (time(8, 0), time(8, 0)),   # Cas spécial = 24h
        (time(22, 0), time(6, 0)),  # Sur 2 jours = 8h
    ]
    
    for debut, fin in test_cases:
        from datetime import datetime, timedelta
        from decimal import Decimal, ROUND_HALF_UP
        
        debut_dt = datetime.combine(datetime.today(), debut)
        fin_dt = datetime.combine(datetime.today(), fin)
        
        if debut_dt == fin_dt:
            duree_calculee = 24.0
        else:
            if fin_dt < debut_dt:
                fin_dt = fin_dt + timedelta(days=1)
            duree_timedelta = fin_dt - debut_dt
            duree_calculee = duree_timedelta.total_seconds() / 3600
        
        duree_decimal = Decimal(str(duree_calculee)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        print(f"   {debut} à {fin} = {duree_decimal} heures")

if __name__ == "__main__":
    try:
        test_calculs_heures_supplementaires()
        test_problemes_specifiques()
        print("\n" + "=" * 60)
        print("TEST TERMINÉ")
        print("=" * 60)
    except Exception as e:
        print(f"Erreur lors du test: {e}")
        import traceback
        traceback.print_exc()
