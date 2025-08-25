from django import forms
from .models import DocumentAdministratif

class DocumentAdministratifForm(forms.ModelForm):
    class Meta:
        model = DocumentAdministratif
        fields = ['vehicule', 'type_document', 'numero', 'date_emission', 'date_expiration', 'fichier', 'commentaires']
        widgets = {
            'vehicule': forms.HiddenInput(),
            'type_document': forms.TextInput(attrs={'class': 'form-control'}),
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'date_emission': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_expiration': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fichier': forms.FileInput(attrs={'class': 'form-control'}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
