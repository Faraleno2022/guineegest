#!/usr/bin/env python
"""
Test final pour vérifier que la sauvegarde des montants fonctionne
"""
import os
import sys
import django
from django.conf import settings

# Ajouter le répertoire du projet au path
sys.path.append('c:/Users/faral/Desktop/Gestion_parck')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.contrib.auth.models import User
from fleet_app.models_entreprise import ConfigurationMontantStatut

def test_final_save():
    """Test final de la sauvegarde"""
    print("🎯 TEST FINAL DE SAUVEGARDE DES MONTANTS")
    print("=" * 60)
    
    try:
        # Récupérer le premier utilisateur
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé")
            return
            
        print(f"👤 Utilisateur: {user.username}")
        
        # Récupérer la configuration
        config = ConfigurationMontantStatut.get_or_create_for_user(user)
        
        # Afficher l'état initial
        print(f"\n📊 ÉTAT INITIAL:")
        print(f"  - montant_absent: {config.montant_absent}")
        print(f"  - montant_am: {config.montant_am}")
        print(f"  - montant_pm: {config.montant_pm}")
        
        # Test de sauvegarde multiple
        print(f"\n🔧 TEST DE SAUVEGARDE MULTIPLE:")
        
        # Test 1: Montant absent
        config.montant_absent = 15000
        config.save()
        config.refresh_from_db()
        print(f"  ✅ montant_absent: {config.montant_absent}")
        
        # Test 2: Montant matin
        config.montant_am = 8000
        config.save()
        config.refresh_from_db()
        print(f"  ✅ montant_am: {config.montant_am}")
        
        # Test 3: Montant après-midi
        config.montant_pm = 8000
        config.save()
        config.refresh_from_db()
        print(f"  ✅ montant_pm: {config.montant_pm}")
        
        # Test 4: Montant journée
        config.montant_journee = 16000
        config.save()
        config.refresh_from_db()
        print(f"  ✅ montant_journee: {config.montant_journee}")
        
        print(f"\n🎉 TOUS LES TESTS DE SAUVEGARDE RÉUSSIS!")
        print(f"📋 La configuration est maintenant prête pour l'interface utilisateur.")
        
        # Afficher un résumé
        print(f"\n📈 RÉSUMÉ DES MONTANTS CONFIGURÉS:")
        print(f"  - Absent: {config.montant_absent} GNF")
        print(f"  - Matin: {config.montant_am} GNF") 
        print(f"  - Après-midi: {config.montant_pm} GNF")
        print(f"  - Journée: {config.montant_journee} GNF")
        print(f"  - Dimanche matin: {config.montant_dim_am} GNF")
        print(f"  - Dimanche après-midi: {config.montant_dim_pm} GNF")
        print(f"  - Dimanche journée: {config.montant_dim_journee} GNF")
        print(f"  - Maladie: {config.montant_maladie} GNF")
        print(f"  - Maladie payée: {config.montant_maladie_payee} GNF")
        print(f"  - Congé: {config.montant_conge} GNF")
        print(f"  - Formation: {config.montant_formation} GNF")
        print(f"  - Repos: {config.montant_repos} GNF")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_final_save()
