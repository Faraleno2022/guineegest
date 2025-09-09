from django import forms
from .models_inventaire import Produit, EntreeStock, SortieStock, Commande, LigneCommande
from .models_facturation import Facture, LigneFacture
import re
import os
from django.core.exceptions import ValidationError

class ProduitForm(forms.ModelForm):
    """Formulaire pour la création et modification de produits"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    
    class Meta:
        model = Produit
        fields = ['id_produit', 'nom', 'categorie', 'unite', 'seuil_minimum', 'prix_unitaire', 'fournisseur', 'date_ajout']
        widgets = {
            'date_ajout': forms.DateInput(attrs={'type': 'date'}),
            'prix_unitaire': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
            'seuil_minimum': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
        }
    
    def clean_id_produit(self):
        """Valide que l'ID du produit suit le format PRDxxx"""
        id_produit = self.cleaned_data.get('id_produit')
        if not re.match(r'^PRD\d{3}$', id_produit):
            raise ValidationError("L'ID du produit doit être au format PRDxxx où xxx est un nombre à 3 chiffres.")
        return id_produit


class EntreeStockForm(forms.ModelForm):
    """Formulaire pour les entrées en stock"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['produit'].queryset = Produit.objects.filter(user=self.user)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    
    class Meta:
        model = EntreeStock
        fields = ['id_entree', 'date', 'produit', 'quantite', 'prix_unitaire', 'fournisseur', 'reference_facture']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'quantite': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
            'prix_unitaire': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
        }
    
    def clean_id_entree(self):
        """Valide que l'ID de l'entrée suit le format ENTxxx"""
        id_entree = self.cleaned_data.get('id_entree')
        if not re.match(r'^ENT\d{3}$', id_entree):
            raise ValidationError("L'ID de l'entrée doit être au format ENTxxx où xxx est un nombre à 3 chiffres.")
        return id_entree
    
    def clean_reference_facture(self):
        """Valide que la référence de facture suit le format FAC-YYYY-xxxx"""
        reference = self.cleaned_data.get('reference_facture')
        if not re.match(r'^FAC\d{4}-\d{4}$', reference):
            raise ValidationError("La référence de facture doit être au format FACyyyy-xxxx.")
        return reference


class SortieStockForm(forms.ModelForm):
    """Formulaire pour les sorties de stock"""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['produit'].queryset = Produit.objects.filter(user=self.user)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    
    class Meta:
        model = SortieStock
        fields = ['id_sortie', 'date', 'produit', 'quantite', 'destination', 'motif']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'quantite': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
            'motif': forms.Textarea(attrs={'rows': 2}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def clean_id_sortie(self):
        """Valide que l'ID de la sortie suit le format SRTxxx"""
        id_sortie = self.cleaned_data.get('id_sortie')
        if not re.match(r'^SRT\d{3}$', id_sortie):
            raise ValidationError("L'ID de la sortie doit être au format SRTxxx où xxx est un nombre à 3 chiffres.")
        return id_sortie
    
    # Méthode supprimée car le champ reference_bon n'existe pas dans le modèle SortieStock
    
    def clean(self):
        """Vérifie qu'il y a assez de stock pour cette sortie"""
        cleaned_data = super().clean()
        produit = cleaned_data.get('produit')
        quantite = cleaned_data.get('quantite')
        
        if produit and quantite:
            stock_actuel = produit.get_stock_actuel()
            
            # Si c'est une mise à jour, on ajoute la quantité précédente
            instance = getattr(self, 'instance', None)
            if instance and instance.pk:
                stock_actuel += instance.quantite
                
            if quantite > stock_actuel:
                self.add_error('quantite', f"Stock insuffisant. Stock actuel: {stock_actuel} {produit.unite}.")
        
        return cleaned_data


class RechercheInventaireForm(forms.Form):
    """Formulaire de recherche pour l'inventaire"""
    
    CHOIX_RECHERCHE = [
        ('', '-- Sélectionner un critère --'),
        ('id_produit', 'ID Produit'),
        ('nom', 'Nom du produit'),
        ('categorie', 'Catégorie'),
        ('fournisseur', 'Fournisseur'),
    ]
    
    critere = forms.ChoiceField(choices=CHOIX_RECHERCHE, required=False)
    terme = forms.CharField(max_length=100, required=False)
    date_debut = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    date_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    def clean(self):
        """Valide que si un terme est fourni, un critère l'est aussi"""
        cleaned_data = super().clean()
        terme = cleaned_data.get('terme')
        critere = cleaned_data.get('critere')
        
        if terme and not critere:
            self.add_error('critere', "Veuillez sélectionner un critère de recherche.")
            
        return cleaned_data


class CommandeForm(forms.ModelForm):
    """Formulaire pour la création et modification de commandes"""
    
    class Meta:
        model = Commande
        fields = ['fournisseur', 'date_creation', 'date_livraison_prevue', 'adresse_fournisseur', 
                  'telephone_fournisseur', 'email_fournisseur', 'remise', 'notes', 'statut']
        widgets = {
            'date_creation': forms.DateInput(attrs={'type': 'date'}),
            'date_livraison_prevue': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'adresse_fournisseur': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Rendre le champ statut non-requis pour les nouvelles commandes
        if not self.instance.pk:
            self.fields['statut'].required = False
            self.fields['statut'].initial = 'Brouillon'

    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Assigner l'utilisateur pour les nouvelles commandes
        if self.user and not instance.pk:
            instance.user = self.user
        
        if commit:
            instance.save()
            # Recalculer les montants après sauvegarde
            instance.calculer_montants()
        return instance


class LigneCommandeForm(forms.ModelForm):
    """Formulaire pour les lignes de commande"""
    # Champs non-modèle pour l'affichage des informations du produit
    nom_produit = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}), label="Nom du produit")
    categorie = forms.CharField(required=False, widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}), label="Catégorie")
    
    class Meta:
        model = LigneCommande
        fields = ['produit', 'quantite', 'prix_unitaire']
        widgets = {
            'quantite': forms.NumberInput(attrs={'min': '1', 'step': '1', 'class': 'form-control'}),
            'prix_unitaire': forms.NumberInput(attrs={'min': '0', 'step': '1', 'class': 'form-control'}),
            'produit': forms.Select(attrs={'class': 'form-select', 'id': 'id_produit'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les produits par utilisateur
        if self.user:
            self.fields['produit'].queryset = Produit.objects.filter(user=self.user)
        
        # Pré-remplir les champs si on a un produit
        if 'initial' not in kwargs and self.instance.pk and self.instance.produit:
            self.fields['prix_unitaire'].initial = self.instance.produit.prix_unitaire
            self.fields['nom_produit'].initial = self.instance.produit.nom
            self.fields['categorie'].initial = self.instance.produit.categorie


class RechercheCommandeForm(forms.Form):
    """Formulaire de recherche pour les commandes"""
    
    CHOIX_STATUT = [
        ('', 'Tous les statuts'),
        ('Brouillon', 'Brouillon'),
        ('En attente', 'En attente de validation'),
        ('Validée', 'Validée'),
        ('En cours', 'En cours de traitement'),
        ('Livrée', 'Livrée'),
        ('Annulée', 'Annulée'),
    ]
    
    numero = forms.CharField(max_length=15, required=False, label="Numéro de commande")
    fournisseur = forms.CharField(max_length=100, required=False, label="Fournisseur")
    statut = forms.ChoiceField(choices=CHOIX_STATUT, required=False)
    date_debut = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Date début")
    date_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Date fin")


class FactureForm(forms.ModelForm):
    """Formulaire pour la création et modification de factures"""
    
    class Meta:
        model = Facture
        fields = ['reference', 'date_emission', 'date_echeance', 'tiers_nom', 'tiers_adresse',
                  'tiers_telephone', 'tiers_email', 'mode_paiement', 'delai_paiement',
                  'banque', 'rib', 'remise', 'notes', 'statut']
        widgets = {
            'date_emission': forms.DateInput(attrs={'type': 'date'}),
            'date_echeance': forms.DateInput(attrs={'type': 'date'}),
            'tiers_adresse': forms.Textarea(attrs={'rows': 2}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Rendre le champ statut non-requis pour les nouvelles factures
        if not self.instance.pk:
            self.fields['statut'].required = False
            self.fields['statut'].initial = 'brouillon'
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Assigner l'utilisateur actuel
        if self.user and not instance.pk:
            instance.utilisateur = self.user
            
        if commit:
            instance.save()
        return instance


class LigneFactureForm(forms.ModelForm):
    """Formulaire pour les lignes de facture"""
    
    class Meta:
        model = LigneFacture
        fields = ['produit', 'description', 'quantite', 'prix_unitaire']
        widgets = {
            'quantite': forms.NumberInput(attrs={'min': '1', 'step': '1'}),
            'prix_unitaire': forms.NumberInput(attrs={'min': '0', 'step': '1'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les produits par utilisateur
        if self.user:
            self.fields['produit'].queryset = Produit.objects.filter(user=self.user)
        
        # Pré-remplir le prix unitaire et la description si on a un produit
        if 'initial' not in kwargs and self.instance.pk and self.instance.produit:
            self.fields['prix_unitaire'].initial = self.instance.produit.prix_unitaire
            self.fields['description'].initial = self.instance.produit.nom
    
    def clean_prix_unitaire(self):
        """S'assure que le prix unitaire est correctement converti en Decimal"""
        from decimal import Decimal
        prix_unitaire = self.cleaned_data.get('prix_unitaire')
        
        # Si c'est déjà un Decimal, le retourner tel quel
        if isinstance(prix_unitaire, Decimal):
            return prix_unitaire
            
        # Si c'est une chaîne, nettoyer et convertir
        if isinstance(prix_unitaire, str):
            # Supprimer les caractères non numériques (espaces, symboles monétaires, etc.)
            prix_unitaire = re.sub(r'[^0-9.]', '', prix_unitaire)
            
        # Convertir en Decimal
        try:
            return Decimal(prix_unitaire)
        except (ValueError, TypeError):
            raise ValidationError("Le prix unitaire doit être un nombre valide.")


class RechercheFactureForm(forms.Form):
    """Formulaire de recherche pour les factures"""
    
    CHOIX_STATUT = [
        ('', 'Tous les statuts'),
        ('brouillon', 'Brouillon'),
        ('validee', 'Validée'),
        ('envoyee', 'Envoyée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    numero = forms.CharField(max_length=20, required=False, label="Numéro de facture")
    tiers = forms.CharField(max_length=100, required=False, label="Client/Tiers")
    statut = forms.ChoiceField(choices=CHOIX_STATUT, required=False)
    date_debut = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Date début")
    date_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}), label="Date fin")


class DocumentSigneForm(forms.ModelForm):
    """Formulaire pour joindre un document signé à une facture"""
    
    class Meta:
        model = Facture
        fields = ['document_signe']
        widgets = {
            'document_signe': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
    def clean_document_signe(self):
        """Valide que le fichier est d'un type acceptable (PDF, image, etc.)"""
        document = self.cleaned_data.get('document_signe')
        if document:
            # Vérifier l'extension du fichier
            ext = os.path.splitext(document.name)[1].lower()
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff']
            
            if ext not in valid_extensions:
                raise ValidationError("Le fichier doit être au format PDF ou image (.jpg, .png, .tiff).")
                
            # Vérifier la taille du fichier (max 5 MB)
            if document.size > 5 * 1024 * 1024:  # 5 MB en octets
                raise ValidationError("La taille du fichier ne doit pas dépasser 5 MB.")
                
        return document


class DocumentSigneCommandeForm(forms.ModelForm):
    """Formulaire pour joindre un document signé à une commande"""
    
    class Meta:
        model = Commande
        fields = ['document_signe']
        widgets = {
            'document_signe': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
    def clean_document_signe(self):
        """Valide que le fichier est d'un type acceptable (PDF, image, etc.)"""
        document = self.cleaned_data.get('document_signe')
        if document:
            # Vérifier l'extension du fichier
            ext = os.path.splitext(document.name)[1].lower()
            valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.tif', '.tiff']
            
            if ext not in valid_extensions:
                raise ValidationError("Le fichier doit être au format PDF ou image (.jpg, .png, .tiff).")
                
            # Vérifier la taille du fichier (max 5 MB)
            if document.size > 5 * 1024 * 1024:  # 5 MB en octets
                raise ValidationError("La taille du fichier ne doit pas dépasser 5 MB.")
                
        return document
