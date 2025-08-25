from django import forms
from .models_entreprise import ConfigurationMontantStatut


class ConfigurationMontantStatutForm(forms.ModelForm):
    """
    Formulaire pour configurer les montants personnalisés des statuts de présence
    """
    class Meta:
        model = ConfigurationMontantStatut
        fields = [
            'montant_am', 'montant_pm', 'montant_journee',
            'montant_dim_am', 'montant_dim_pm', 'montant_dim_journee',
            'montant_absent', 'montant_maladie', 'montant_maladie_payee',
            'montant_conge', 'montant_formation', 'montant_repos'
        ]
        widgets = {
            'montant_am': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_pm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_journee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_dim_am': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_dim_pm': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_dim_journee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_absent': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_maladie': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_maladie_payee': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_conge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_formation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_repos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
        }
        labels = {
            'montant_am': 'Présent matin (P(Am))',
            'montant_pm': 'Présent après-midi (P(Pm))',
            'montant_journee': 'Présent journée (P(Am&Pm))',
            'montant_dim_am': 'Dimanche matin (P(dim_Am))',
            'montant_dim_pm': 'Dimanche après-midi (P(dim_Pm))',
            'montant_dim_journee': 'Dimanche journée (P(dim_Am_&_Pm))',
            'montant_absent': 'Absent (A)',
            'montant_maladie': 'Maladie (M)',
            'montant_maladie_payee': 'Maladie payée (M(Payer))',
            'montant_conge': 'Congé (C)',
            'montant_formation': 'Formation (F)',
            'montant_repos': 'Repos autorisé (OFF)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Ajouter des placeholders avec les valeurs par défaut
        default_values = {
            'montant_am': '50000',
            'montant_pm': '50000', 
            'montant_journee': '100000',
            'montant_dim_am': '75000',
            'montant_dim_pm': '75000',
            'montant_dim_journee': '150000',
            'montant_absent': '0',
            'montant_maladie': '0',
            'montant_maladie_payee': '100000',
            'montant_conge': '100000',
            'montant_formation': '100000',
            'montant_repos': '0',
        }
        
        for field_name, default_value in default_values.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs['placeholder'] = f'Par défaut: {default_value} GNF'
