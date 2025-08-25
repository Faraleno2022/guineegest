#!/usr/bin/env python
"""
Script de test simple pour vérifier la sauvegarde des montants via la vue Django
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

def test_montant_save():
    """Test de sauvegarde des montants"""
    print("🧪 TEST DE SAUVEGARDE DES MONTANTS")
    print("=" * 50)
    
    # Récupérer le premier utilisateur
    try:
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé dans la base de données")
            return
            
        print(f"👤 Utilisateur de test: {user.username}")
        
        # Récupérer ou créer la configuration
        config = ConfigurationMontantStatut.get_or_create_for_user(user)
        print(f"📋 Configuration récupérée: {config}")
        
        # Afficher les valeurs actuelles
        print("\n📊 VALEURS ACTUELLES:")
        print(f"  - montant_absent: {config.montant_absent}")
        print(f"  - montant_am: {config.montant_am}")
        print(f"  - montant_pm: {config.montant_pm}")
        print(f"  - montant_journee: {config.montant_journee}")
        
        # Test de modification
        print("\n🔧 TEST DE MODIFICATION:")
        old_absent = config.montant_absent
        config.montant_absent = 25000
        config.save()
        print(f"  - montant_absent: {old_absent} → {config.montant_absent}")
        
        # Vérification de la sauvegarde
        config.refresh_from_db()
        print(f"  - Vérification après refresh: {config.montant_absent}")
        
        if config.montant_absent == 25000:
            print("✅ SAUVEGARDE RÉUSSIE!")
        else:
            print("❌ ÉCHEC DE LA SAUVEGARDE!")
            
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_montant_save()
