"""
Formulaire dédié pour la configuration des montants des statuts de présence
"""

from django import forms
from .models_entreprise import ConfigurationMontantStatut


class ConfigurationMontantsForm(forms.ModelForm):
    """
    Formulaire pour configurer tous les montants des statuts de présence
    """
    
    class Meta:
        model = ConfigurationMontantStatut
        fields = [
            'montant_am',
            'montant_pm', 
            'montant_journee',
            'montant_dim_am',
            'montant_dim_pm',
            'montant_dim_journee',
            'montant_absent',
            'montant_maladie',
            'montant_maladie_payee',
            'montant_conge',
            'montant_formation',
            'montant_repos',
        ]
        
        widgets = {
            'montant_am': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_pm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_journee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_dim_am': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_dim_pm': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_dim_journee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_absent': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_maladie': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_maladie_payee': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_conge': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_formation': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
            'montant_repos': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0',
                'step': '0.01',
                'min': '0'
            }),
        }
        
        labels = {
            'montant_am': 'P(Am) - Présent matin',
            'montant_pm': 'P(Pm) - Présent après-midi',
            'montant_journee': 'P(Am&Pm) - Présent journée complète',
            'montant_dim_am': 'P(dim_Am) - Dimanche matin',
            'montant_dim_pm': 'P(dim_Pm) - Dimanche après-midi',
            'montant_dim_journee': 'P(dim_Am_&_Pm) - Dimanche journée',
            'montant_absent': 'A - Absent',
            'montant_maladie': 'M - Maladie',
            'montant_maladie_payee': 'M(Payer) - Maladie payée',
            'montant_conge': 'C - Congé',
            'montant_formation': 'F - Formation',
            'montant_repos': 'OFF - Repos autorisé',
        }
        
        help_texts = {
            'montant_am': 'Montant pour une présence le matin uniquement',
            'montant_pm': 'Montant pour une présence l\'après-midi uniquement',
            'montant_journee': 'Montant pour une présence toute la journée',
            'montant_dim_am': 'Montant pour une présence le dimanche matin',
            'montant_dim_pm': 'Montant pour une présence le dimanche après-midi',
            'montant_dim_journee': 'Montant pour une présence le dimanche toute la journée',
            'montant_absent': 'Montant pour une absence (généralement 0)',
            'montant_maladie': 'Montant pour une maladie non payée (généralement 0)',
            'montant_maladie_payee': 'Montant pour une maladie payée',
            'montant_conge': 'Montant pour un congé',
            'montant_formation': 'Montant pour une formation',
            'montant_repos': 'Montant pour un repos autorisé (généralement 0)',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Ajouter des classes CSS pour une meilleure présentation
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': field.widget.attrs.get('class', '') + ' form-control-lg'
            })

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
