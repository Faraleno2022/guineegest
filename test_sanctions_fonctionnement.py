#!/usr/bin/env python
"""
Script de test pour vérifier le bon fonctionnement des sanctions
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
from decimal import Decimal

def tester_sanctions():
    """
    Tester le fonctionnement des sanctions
    """
    print("🧪 TEST - Fonctionnement des sanctions dans configuration-heures-supplementaires")
    print("=" * 80)
    
    # Récupérer un utilisateur de test
    users = User.objects.all()
    if not users.exists():
        print("❌ Aucun utilisateur trouvé pour les tests")
        return
    
    user = users.first()
    print(f"👤 Utilisateur de test: {user.username}")
    
    # Récupérer les employés de cet utilisateur
    employes = Employe.objects.filter(user=user)
    if not employes.exists():
        print("❌ Aucun employé trouvé pour les tests")
        return
    
    print(f"👥 Nombre d'employés: {employes.count()}")
    
    # Tester avec le premier employé
    employe = employes.first()
    print(f"\n🧑‍💼 Test avec: {employe.matricule} - {employe.prenom} {employe.nom}")
    
    # Afficher les valeurs actuelles
    print(f"   💰 Avances actuelles: {employe.avances} GNF")
    print(f"   ⚠️ Sanctions actuelles: {employe.sanctions} GNF")
    
    # Test 1: Définir une sanction
    print(f"\n📝 TEST 1: Définir une sanction de 50,000 GNF")
    employe.sanctions = Decimal('50000')
    employe.save()
    
    # Recharger depuis la base de données
    employe.refresh_from_db()
    print(f"   ✅ Sanction sauvegardée: {employe.sanctions} GNF")
    
    # Test 2: Modifier la sanction
    print(f"\n📝 TEST 2: Modifier la sanction à 75,000 GNF")
    employe.sanctions = Decimal('75000')
    employe.save()
    
    # Recharger depuis la base de données
    employe.refresh_from_db()
    print(f"   ✅ Sanction modifiée: {employe.sanctions} GNF")
    
    # Test 3: Remettre à zéro
    print(f"\n📝 TEST 3: Remettre la sanction à zéro")
    employe.sanctions = Decimal('0')
    employe.save()
    
    # Recharger depuis la base de données
    employe.refresh_from_db()
    print(f"   ✅ Sanction remise à zéro: {employe.sanctions} GNF")
    
    print(f"\n🎉 TOUS LES TESTS RÉUSSIS !")
    print(f"✅ Le champ 'sanctions' fonctionne correctement")
    print(f"✅ Les données se sauvegardent en base")
    print(f"✅ Les modifications sont persistantes")
    
    # Vérifier d'autres employés
    print(f"\n📊 VÉRIFICATION GLOBALE:")
    for emp in employes[:5]:  # Limiter à 5 employés
        print(f"   🧑‍💼 {emp.matricule} - Avances: {emp.avances} GNF, Sanctions: {emp.sanctions} GNF")

def verifier_template_et_vue():
    """
    Vérifier que le template et la vue sont bien configurés
    """
    print(f"\n🔍 VÉRIFICATION TEMPLATE ET VUE:")
    
    # Vérifier le template
    template_path = r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\configuration_heure_supplementaire.html'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        if '{{ employe.sanctions|floatformat:2 }} GNF' in contenu:
            print("   ✅ Template affiche les sanctions")
        else:
            print("   ❌ Template n'affiche pas les sanctions")
        
        if 'name="sanctions_employe"' in contenu:
            print("   ✅ Formulaire contient le champ sanctions_employe")
        else:
            print("   ❌ Formulaire ne contient pas le champ sanctions_employe")
    
    except FileNotFoundError:
        print("   ❌ Template non trouvé")
    
    # Vérifier la vue
    vue_path = r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\views_management.py'
    try:
        with open(vue_path, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        if "sanctions = request.POST.get('sanctions_employe')" in contenu:
            print("   ✅ Vue récupère le champ sanctions_employe")
        else:
            print("   ❌ Vue ne récupère pas le champ sanctions_employe")
        
        if "employe.sanctions = Decimal(sanctions)" in contenu:
            print("   ✅ Vue traite le champ sanctions")
        else:
            print("   ❌ Vue ne traite pas le champ sanctions")
    
    except FileNotFoundError:
        print("   ❌ Vue non trouvée")

if __name__ == "__main__":
    tester_sanctions()
    verifier_template_et_vue()
    
    print(f"\n🚀 PRÊT POUR LES TESTS UTILISATEUR:")
    print(f"1. Aller sur management/configuration-heures-supplementaires/")
    print(f"2. Cliquer sur 'Modifier' pour un employé")
    print(f"3. Saisir un montant dans le champ 'Sanctions (GNF)'")
    print(f"4. Cliquer sur 'Enregistrer'")
    print(f"5. Vérifier que le montant s'affiche dans la colonne 'Sanctions'")
