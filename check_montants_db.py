#!/usr/bin/env python
"""
Script pour vérifier les montants actuels dans la base de données
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models_entreprise import ConfigurationMontantStatut
from django.contrib.auth.models import User

def check_current_values():
    """Affiche les valeurs actuelles dans la base de données"""
    
    print("🔍 Vérification des montants actuels dans la base de données...")
    
    configurations = ConfigurationMontantStatut.objects.all()
    
    for config in configurations:
        user_name = config.user.username if config.user else "Utilisateur inconnu"
        
        print(f"\n👤 Configuration pour {user_name}:")
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
        
        # Tester get_montants_dict()
        montants_dict = config.get_montants_dict()
        print(f"\n📊 get_montants_dict() pour {user_name}:")
        for key, value in montants_dict.items():
            print(f"   {key}: {value}")

def force_reset_all():
    """Force la réinitialisation de TOUS les montants à zéro"""
    
    print("\n🔄 Réinitialisation forcée de tous les montants...")
    
    configurations = ConfigurationMontantStatut.objects.all()
    
    for config in configurations:
        user_name = config.user.username if config.user else "Utilisateur inconnu"
        
        print(f"\n👤 Réinitialisation pour {user_name}:")
        
        # Forcer TOUS les montants à zéro
        config.montant_am = 0
        config.montant_pm = 0
        config.montant_journee = 0
        config.montant_dim_am = 0
        config.montant_dim_pm = 0
        config.montant_dim_journee = 0
        config.montant_absent = 0
        config.montant_maladie = 0
        config.montant_maladie_payee = 0
        config.montant_conge = 0
        config.montant_formation = 0
        config.montant_repos = 0
        
        config.save()
        print(f"   ✅ Tous les montants réinitialisés à 0")
    
    print(f"\n✅ {configurations.count()} configurations réinitialisées")

if __name__ == "__main__":
    print("=" * 60)
    print("🔍 INSPECTION DES MONTANTS EN BASE")
    print("=" * 60)
    
    # Étape 1: Vérifier les valeurs actuelles
    check_current_values()
    
    print("\n" + "=" * 60)
    print("🔄 RÉINITIALISATION FORCÉE")
    print("=" * 60)
    
    # Étape 2: Forcer la réinitialisation
    force_reset_all()
    
    print("\n" + "=" * 60)
    print("🔍 VÉRIFICATION POST-RÉINITIALISATION")
    print("=" * 60)
    
    # Étape 3: Vérifier à nouveau
    check_current_values()
