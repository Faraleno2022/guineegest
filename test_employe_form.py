#!/usr/bin/env python
"""
Script de test pour diagnostiquer le problème avec le formulaire EmployeForm
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models_entreprise import Employe
from fleet_app.forms import EmployeForm

def test_employe_form():
    """Test du formulaire EmployeForm"""
    print("=== TEST DU FORMULAIRE EMPLOYE ===")
    
    # 1. Tester si l'employé ID 12 existe
    try:
        employe = Employe.objects.get(pk=12)
        print(f"✅ Employé trouvé: {employe.prenom} {employe.nom}")
        print(f"   - Matricule: {employe.matricule}")
        print(f"   - Fonction: {employe.fonction}")
        print(f"   - Téléphone: {employe.telephone}")
        print(f"   - Statut: {employe.statut}")
        print(f"   - Salaire: {employe.salaire_journalier}")
    except Employe.DoesNotExist:
        print("❌ Employé avec ID 12 non trouvé")
        return
    
    # 2. Tester la création du formulaire avec instance
    try:
        form = EmployeForm(instance=employe)
        print("✅ Formulaire créé avec succès")
        
        # 3. Vérifier les champs du formulaire
        print("\n=== CHAMPS DU FORMULAIRE ===")
        for field_name, field in form.fields.items():
            initial_value = form.initial.get(field_name, 'Non défini')
            print(f"   - {field_name}: {initial_value}")
            
        # 4. Vérifier les valeurs initiales
        print("\n=== VALEURS INITIALES ===")
        print(f"   - form.initial: {form.initial}")
        
        # 5. Tester le rendu HTML des champs principaux
        print("\n=== RENDU HTML DES CHAMPS ===")
        try:
            print(f"   - Matricule HTML: {form['matricule']}")
            print(f"   - Nom HTML: {form['nom']}")
            print(f"   - Prénom HTML: {form['prenom']}")
        except Exception as e:
            print(f"❌ Erreur lors du rendu HTML: {e}")
            
    except Exception as e:
        print(f"❌ Erreur lors de la création du formulaire: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_employe_form()
