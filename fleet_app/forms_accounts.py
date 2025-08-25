from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from .models_accounts import Profil, PersonnePhysique, Entreprise, TYPE_COMPTE_CHOICES, FORME_JURIDIQUE_CHOICES, ROLE_CHOICES


class TypeCompteForm(forms.Form):
    """Formulaire pour choisir le type de compte"""
    type_compte = forms.ChoiceField(
        choices=TYPE_COMPTE_CHOICES,
        widget=forms.RadioSelect(),
        label=_("Type de compte")
    )


class ProfilForm(forms.ModelForm):
    """Formulaire pour les informations communes à tous les types de compte"""
    class Meta:
        model = Profil
        fields = ['telephone', 'email', 'adresse', 'role']
        widgets = {
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Numéro de téléphone')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Adresse e-mail')}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Adresse complète')}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }


class PersonnePhysiqueForm(forms.ModelForm):
    """Formulaire pour les informations spécifiques aux personnes physiques"""
    class Meta:
        model = PersonnePhysique
        fields = ['nom_prenom', 'date_naissance', 'photo']
        widgets = {
            'nom_prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nom et prénom(s)')}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class EntrepriseForm(forms.ModelForm):
    """Formulaire pour les informations spécifiques aux entreprises"""
    class Meta:
        model = Entreprise
        fields = ['nom_entreprise', 'forme_juridique', 'nom_responsable', 'rccm_nif', 'logo']
        widgets = {
            'nom_entreprise': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nom de l\'entreprise')}),
            'forme_juridique': forms.Select(attrs={'class': 'form-select'}),
            'nom_responsable': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nom du gérant ou directeur')}),
            'rccm_nif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Numéro RCCM ou NIF')}),
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CompteUtilisateurForm(UserCreationForm):
    """Formulaire pour créer un compte utilisateur avec nom d'utilisateur et mot de passe"""
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nom d\'utilisateur')}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Mot de passe')})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': _('Confirmation du mot de passe')})


class ConditionsForm(forms.Form):
    """Formulaire pour l'acceptation des conditions"""
    conditions_acceptees = forms.BooleanField(
        required=True,
        label=_("J'ai lu et j'accepte les conditions générales d'utilisation"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    informations_certifiees = forms.BooleanField(
        required=True,
        label=_("Je certifie l'exactitude des informations fournies"),
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
