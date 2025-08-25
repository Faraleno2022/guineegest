#!/usr/bin/env python
"""
Script pour créer un employé de test pour le système de pointage
"""

import os
import sys
import django
from django.contrib.auth.models import User

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

def creer_employe_test():
    """
    Crée un employé de test
    """
    try:
        from fleet_app.models_entreprise import Employe
        
        # Récupérer le premier utilisateur (admin)
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé. Veuillez d'abord créer un utilisateur admin.")
            return False
        
        print(f"👤 Utilisateur trouvé: {user.username}")
        
        # Vérifier si l'employé existe déjà
        employe_existant = Employe.objects.filter(matricule='TEST001').first()
        if employe_existant:
            print(f"✅ Employé de test existe déjà: {employe_existant.nom} {employe_existant.prenom}")
            return True
        
        # Créer l'employé de test
        employe = Employe.objects.create(
            user=user,
            matricule='TEST001',
            nom='DUPONT',
            prenom='Jean',
            fonction='Testeur',
            telephone='123456789',
            date_embauche='2024-01-01',
            salaire_journalier=50000,
            statut='Actif',
            taux_horaire_specifique=5000,
            avances=0
        )
        
        print(f"✅ Employé de test créé avec succès:")
        print(f"   - Nom: {employe.nom} {employe.prenom}")
        print(f"   - Matricule: {employe.matricule}")
        print(f"   - Fonction: {employe.fonction}")
        print(f"   - Salaire journalier: {employe.salaire_journalier} GNF")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'employé: {str(e)}")
        return False

def main():
    """
    Fonction principale
    """
    print("=" * 50)
    print("🧪 CRÉATION D'EMPLOYÉ DE TEST")
    print("=" * 50)
    print()
    
    success = creer_employe_test()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ EMPLOYÉ DE TEST CRÉÉ AVEC SUCCÈS")
        print("\n💡 Vous pouvez maintenant:")
        print("   1. Aller sur /pointage/")
        print("   2. Cliquer sur les cellules pour pointer")
        print("   3. Tester les différents statuts")
    else:
        print("❌ ÉCHEC DE LA CRÉATION")
    print("=" * 50)

if __name__ == "__main__":
    main()
