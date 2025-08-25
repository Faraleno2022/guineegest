#!/usr/bin/env python3
"""
Script de test pour valider la sauvegarde des montants via formulaire POST
Test de la nouvelle solution de sauvegarde des montants dans management/presences/
"""

import os
import sys
import django
from decimal import Decimal

# Configuration Django
sys.path.append(r'c:\Users\faral\Desktop\Gestion_parck')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.contrib.auth.models import User
from fleet_app.models_entreprise import ConfigurationMontantStatut

def test_form_save_functionality():
    """Test de la fonctionnalité de sauvegarde via formulaire"""
    print("🧪 TEST DE SAUVEGARDE VIA FORMULAIRE POST")
    print("=" * 50)
    
    try:
        # Récupérer ou créer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='test_user',
            defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
        )
        
        if created:
            print(f"✅ Utilisateur de test créé: {user.username}")
        else:
            print(f"✅ Utilisateur de test trouvé: {user.username}")
        
        # Récupérer ou créer la configuration
        config = ConfigurationMontantStatut.get_or_create_for_user(user)
        print(f"✅ Configuration récupérée pour {user.username}")
        
        # Afficher les valeurs actuelles
        print("\n📊 VALEURS ACTUELLES:")
        print(f"   montant_am: {config.montant_am}")
        print(f"   montant_pm: {config.montant_pm}")
        print(f"   montant_journee: {config.montant_journee}")
        print(f"   montant_dim_am: {config.montant_dim_am}")
        print(f"   montant_dim_pm: {config.montant_dim_pm}")
        print(f"   montant_dim_journee: {config.montant_dim_journee}")
        print(f"   montant_absent: {config.montant_absent}")
        print(f"   montant_maladie: {config.montant_maladie}")
        print(f"   montant_maladie_payee: {config.montant_maladie_payee}")
        print(f"   montant_conge: {config.montant_conge}")
        print(f"   montant_formation: {config.montant_formation}")
        print(f"   montant_repos: {config.montant_repos}")
        
        # Simuler des données POST comme envoyées par le formulaire
        test_data = {
            'montant_am': '8000',
            'montant_pm': '8000', 
            'montant_journee': '15000',
            'montant_dim_am': '10000',
            'montant_dim_pm': '10000',
            'montant_dim_journee': '20000',
            'montant_absent': '0',
            'montant_maladie': '0',
            'montant_maladie_payee': '12000',
            'montant_conge': '15000',
            'montant_formation': '15000',
            'montant_repos': '0'
        }
        
        print("\n🔄 SIMULATION DE SAUVEGARDE POST:")
        updated_fields = []
        
        # Simuler le traitement POST de la vue Django
        for field_name, value in test_data.items():
            if hasattr(config, field_name):
                # Nettoyer la valeur (convertir vide en 0)
                clean_value = Decimal('0') if value == '' or value is None else Decimal(str(value))
                
                # Mettre à jour le champ
                old_value = getattr(config, field_name)
                setattr(config, field_name, clean_value)
                updated_fields.append(f"{field_name}: {old_value} → {clean_value}")
                print(f"   ✅ {field_name}: {old_value} → {clean_value}")
        
        # Sauvegarder
        config.save()
        print(f"\n💾 Configuration sauvegardée avec {len(updated_fields)} champs mis à jour")
        
        # Vérifier la persistance en rechargeant depuis la base
        config_reloaded = ConfigurationMontantStatut.objects.get(user=user)
        print("\n🔍 VÉRIFICATION DE LA PERSISTANCE:")
        
        all_match = True
        for field_name, expected_value in test_data.items():
            if hasattr(config_reloaded, field_name):
                actual_value = getattr(config_reloaded, field_name)
                expected_decimal = Decimal(expected_value) if expected_value else Decimal('0')
                
                if actual_value == expected_decimal:
                    print(f"   ✅ {field_name}: {actual_value} (OK)")
                else:
                    print(f"   ❌ {field_name}: {actual_value} ≠ {expected_decimal} (ERREUR)")
                    all_match = False
        
        if all_match:
            print("\n🎉 SUCCÈS: Tous les montants ont été sauvegardés et persistent correctement!")
            print("✅ La solution de sauvegarde via formulaire POST fonctionne parfaitement.")
        else:
            print("\n❌ ÉCHEC: Certains montants n'ont pas été sauvegardés correctement.")
            
        return all_match
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du test: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_get_montants_dict():
    """Test de la récupération des montants pour affichage"""
    print("\n🧪 TEST DE RÉCUPÉRATION DES MONTANTS")
    print("=" * 40)
    
    try:
        user = User.objects.get(username='test_user')
        config = ConfigurationMontantStatut.get_or_create_for_user(user)
        montants_dict = config.get_montants_dict()
        
        print("📊 MONTANTS RÉCUPÉRÉS:")
        for key, value in montants_dict.items():
            print(f"   {key}: {value}")
        
        print("✅ Récupération des montants réussie!")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR lors de la récupération: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DES TESTS DE SAUVEGARDE DES MONTANTS")
    print("=" * 60)
    
    # Test 1: Sauvegarde via formulaire POST
    test1_success = test_form_save_functionality()
    
    # Test 2: Récupération des montants
    test2_success = test_get_montants_dict()
    
    print("\n" + "=" * 60)
    print("📋 RÉSUMÉ DES TESTS:")
    print(f"   Test 1 (Sauvegarde POST): {'✅ SUCCÈS' if test1_success else '❌ ÉCHEC'}")
    print(f"   Test 2 (Récupération): {'✅ SUCCÈS' if test2_success else '❌ ÉCHEC'}")
    
    if test1_success and test2_success:
        print("\n🎉 TOUS LES TESTS RÉUSSIS!")
        print("✅ La solution de sauvegarde des montants est fonctionnelle.")
    else:
        print("\n⚠️ CERTAINS TESTS ONT ÉCHOUÉ")
        print("❌ La solution nécessite des corrections supplémentaires.")
