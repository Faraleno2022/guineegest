import os
import django
import sys

# Configuration Django
sys.path.append(r'C:\Users\faral\Desktop\Gestion_parck')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.forms_entreprise import EmployeForm

def test_form_validation():
    """Test la validation du formulaire avec des données minimales"""
    
    # Données de test minimales avec tous les champs requis
    test_data = {
        'matricule': 'EMP001',
        'nom': 'Test',
        'prenom': 'Employé',
        'fonction': 'Chauffeur',
        'salaire_journalier': '50000',
        'statut': 'Actif',
        'date_embauche': '2024-01-01',
        'calcul_salaire_auto': False,
        'appliquer_cnss': False,
        'appliquer_rts': False,
        'appliquer_vf': False,
        'taux_horaire_specifique': '0',
        'taux_cnss_salarie_custom': '0',
        'taux_cnss_employeur_custom': '0',
        'taux_vf_custom': '0',
        'montant_heure_supp_jour_ouvrable': '0',
        'montant_heure_supp_dimanche_ferie': '0',
        'mode_calcul_heures_supp': 'standard'
    }
    
    print("=== Test de validation du formulaire ===")
    form = EmployeForm(test_data)
    
    print(f"Formulaire valide: {form.is_valid()}")
    
    if not form.is_valid():
        print("\nErreurs du formulaire:")
        for field, errors in form.errors.items():
            print(f"  {field}: {errors}")
    
    print(f"\nChamps du formulaire: {list(form.fields.keys())}")
    print(f"Champs obligatoires: {[name for name, field in form.fields.items() if field.required]}")

if __name__ == '__main__':
    test_form_validation()
