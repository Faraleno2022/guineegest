#!/usr/bin/env python
"""
Script de diagnostic pour identifier le problème avec les sanctions
dans la page configuration-heures-supplementaires
"""

import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models_entreprise import Employe
from django.contrib.auth.models import User

def diagnostiquer_probleme_sanctions():
    """
    Diagnostiquer le problème avec l'affichage des sanctions
    """
    print("🔍 DIAGNOSTIC - Problème avec les sanctions dans configuration-heures-supplementaires")
    print("=" * 80)
    
    # Vérifier les utilisateurs et leurs employés
    users = User.objects.all()
    print(f"👥 Nombre d'utilisateurs: {users.count()}")
    
    for user in users:
        print(f"\n👤 Utilisateur: {user.username}")
        employes = Employe.objects.filter(user=user)
        print(f"   📊 Nombre d'employés: {employes.count()}")
        
        for employe in employes[:3]:  # Limiter à 3 employés par utilisateur
            print(f"   🧑‍💼 {employe.matricule} - {employe.prenom} {employe.nom}")
            print(f"      💰 Avances: {employe.avances} GNF")
            print(f"      ⚠️ Sanctions: {employe.sanctions} GNF")
            
            # Vérifier si les champs existent
            if hasattr(employe, 'avances'):
                print(f"      ✅ Champ 'avances' existe")
            else:
                print(f"      ❌ Champ 'avances' manquant")
                
            if hasattr(employe, 'sanctions'):
                print(f"      ✅ Champ 'sanctions' existe")
            else:
                print(f"      ❌ Champ 'sanctions' manquant")
    
    print("\n🔧 RECOMMANDATIONS:")
    print("1. Vérifier que le champ 'sanctions' existe dans le modèle Employe")
    print("2. Vérifier que le template récupère bien {{ employe.sanctions }}")
    print("3. Vérifier que la vue traite bien le champ 'sanctions_employe'")
    print("4. Vérifier que le formulaire envoie bien le champ 'sanctions_employe'")

if __name__ == "__main__":
    diagnostiquer_probleme_sanctions()
