#!/usr/bin/env python3
"""
Script de nettoyage pour supprimer définitivement les anciennes valeurs système
Réinitialise tous les montants par défaut (50000, 100000, etc.) à zéro pour tous les utilisateurs
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

# Anciennes valeurs système à supprimer
SYSTEM_DEFAULT_VALUES = [
    Decimal('50000'),   # montant_am, montant_pm
    Decimal('100000'),  # montant_journee, montant_maladie_payee, montant_conge, montant_formation
    Decimal('75000'),   # montant_dim_am, montant_dim_pm
    Decimal('150000'),  # montant_dim_journee
]

def cleanup_system_defaults():
    """Nettoie toutes les valeurs système par défaut pour tous les utilisateurs"""
    print("🧹 NETTOYAGE DES VALEURS SYSTÈME PAR DÉFAUT")
    print("=" * 60)
    
    try:
        # Récupérer toutes les configurations existantes
        all_configs = ConfigurationMontantStatut.objects.all()
        total_configs = all_configs.count()
        
        print(f"📊 {total_configs} configuration(s) trouvée(s) dans la base de données")
        
        if total_configs == 0:
            print("ℹ️ Aucune configuration trouvée. Rien à nettoyer.")
            return True
        
        cleaned_configs = 0
        total_fields_cleaned = 0
        
        for config in all_configs:
            print(f"\n👤 Nettoyage pour l'utilisateur: {config.user.username}")
            
            fields_cleaned = []
            
            # Vérifier et nettoyer chaque champ
            field_checks = [
                ('montant_am', config.montant_am),
                ('montant_pm', config.montant_pm),
                ('montant_journee', config.montant_journee),
                ('montant_dim_am', config.montant_dim_am),
                ('montant_dim_pm', config.montant_dim_pm),
                ('montant_dim_journee', config.montant_dim_journee),
                ('montant_absent', config.montant_absent),
                ('montant_maladie', config.montant_maladie),
                ('montant_maladie_payee', config.montant_maladie_payee),
                ('montant_conge', config.montant_conge),
                ('montant_formation', config.montant_formation),
                ('montant_repos', config.montant_repos),
            ]
            
            for field_name, current_value in field_checks:
                # Si la valeur actuelle est une ancienne valeur système, la réinitialiser à 0
                if current_value in SYSTEM_DEFAULT_VALUES:
                    setattr(config, field_name, Decimal('0'))
                    fields_cleaned.append(f"{field_name}: {current_value} → 0")
                    print(f"   🧹 {field_name}: {current_value} → 0")
            
            # Sauvegarder si des champs ont été nettoyés
            if fields_cleaned:
                config.save()
                cleaned_configs += 1
                total_fields_cleaned += len(fields_cleaned)
                print(f"   ✅ {len(fields_cleaned)} champ(s) nettoyé(s) et sauvegardé(s)")
            else:
                print("   ℹ️ Aucune valeur système trouvée, rien à nettoyer")
        
        print(f"\n📋 RÉSUMÉ DU NETTOYAGE:")
        print(f"   Configurations traitées: {total_configs}")
        print(f"   Configurations modifiées: {cleaned_configs}")
        print(f"   Total de champs nettoyés: {total_fields_cleaned}")
        
        if cleaned_configs > 0:
            print(f"\n🎉 NETTOYAGE TERMINÉ AVEC SUCCÈS!")
            print(f"✅ {total_fields_cleaned} valeur(s) système supprimée(s)")
            print("✅ Tous les montants sont maintenant à 0 par défaut")
        else:
            print(f"\nℹ️ AUCUN NETTOYAGE NÉCESSAIRE")
            print("✅ Aucune valeur système trouvée dans la base")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERREUR lors du nettoyage: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def verify_cleanup():
    """Vérifie que le nettoyage a été effectué correctement"""
    print("\n🔍 VÉRIFICATION DU NETTOYAGE")
    print("=" * 40)
    
    try:
        all_configs = ConfigurationMontantStatut.objects.all()
        
        system_values_found = []
        
        for config in all_configs:
            field_checks = [
                ('montant_am', config.montant_am),
                ('montant_pm', config.montant_pm),
                ('montant_journee', config.montant_journee),
                ('montant_dim_am', config.montant_dim_am),
                ('montant_dim_pm', config.montant_dim_pm),
                ('montant_dim_journee', config.montant_dim_journee),
                ('montant_absent', config.montant_absent),
                ('montant_maladie', config.montant_maladie),
                ('montant_maladie_payee', config.montant_maladie_payee),
                ('montant_conge', config.montant_conge),
                ('montant_formation', config.montant_formation),
                ('montant_repos', config.montant_repos),
            ]
            
            for field_name, current_value in field_checks:
                if current_value in SYSTEM_DEFAULT_VALUES:
                    system_values_found.append(f"{config.user.username}.{field_name}: {current_value}")
        
        if system_values_found:
            print("❌ VALEURS SYSTÈME ENCORE PRÉSENTES:")
            for value in system_values_found:
                print(f"   {value}")
            return False
        else:
            print("✅ AUCUNE VALEUR SYSTÈME TROUVÉE")
            print("✅ Le nettoyage a été effectué avec succès")
            return True
            
    except Exception as e:
        print(f"❌ ERREUR lors de la vérification: {str(e)}")
        return False

def show_current_values():
    """Affiche les valeurs actuelles pour tous les utilisateurs"""
    print("\n📊 VALEURS ACTUELLES DANS LA BASE")
    print("=" * 50)
    
    try:
        all_configs = ConfigurationMontantStatut.objects.all()
        
        for config in all_configs:
            print(f"\n👤 {config.user.username}:")
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
            
    except Exception as e:
        print(f"❌ ERREUR lors de l'affichage: {str(e)}")

if __name__ == "__main__":
    print("🚀 DÉMARRAGE DU NETTOYAGE DES VALEURS SYSTÈME")
    print("=" * 70)
    
    # Afficher les valeurs actuelles
    show_current_values()
    
    # Effectuer le nettoyage
    cleanup_success = cleanup_system_defaults()
    
    # Vérifier le nettoyage
    if cleanup_success:
        verify_success = verify_cleanup()
        
        if verify_success:
            print("\n🎉 MISSION ACCOMPLIE!")
            print("✅ Toutes les valeurs système ont été supprimées")
            print("✅ Seuls les montants définis par l'utilisateur seront utilisés")
        else:
            print("\n⚠️ NETTOYAGE INCOMPLET")
            print("❌ Certaines valeurs système persistent")
    else:
        print("\n❌ ÉCHEC DU NETTOYAGE")
        print("❌ Le nettoyage n'a pas pu être effectué")
