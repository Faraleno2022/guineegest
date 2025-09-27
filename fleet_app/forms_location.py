from django import forms
from django.utils import timezone

from .models_location import (
    FournisseurVehicule,
    LocationVehicule,
    FeuillePontageLocation,
    FactureLocation,
)
from .models import Vehicule


class FournisseurVehiculeForm(forms.ModelForm):
    class Meta:
        model = FournisseurVehicule
        fields = ["nom", "contact", "telephone", "email", "adresse"]


class LocationVehiculeForm(forms.ModelForm):
    class Meta:
        model = LocationVehicule
        fields = [
            "vehicule",
            "type_location",
            "fournisseur",
            "date_debut",
            "date_fin",
            "tarif_journalier",
            "statut",
            "motif",
        ]
        widgets = {
            "date_debut": forms.DateInput(attrs={"type": "date"}),
            "date_fin": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["vehicule"].queryset = Vehicule.objects.filter(user=user)
            self.fields["fournisseur"].queryset = FournisseurVehicule.objects.filter(user=user)


class FeuillePontageLocationForm(forms.ModelForm):
    class Meta:
        model = FeuillePontageLocation
        fields = ["location", "date", "statut", "commentaire"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "value": timezone.now().date()}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["location"].queryset = LocationVehicule.objects.filter(user=user)


class FactureLocationForm(forms.ModelForm):
    class Meta:
        model = FactureLocation
        fields = ["location", "numero", "date", "montant_ht", "tva", "montant_ttc", "statut"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields["location"].queryset = LocationVehicule.objects.filter(user=user)
