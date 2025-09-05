from django import forms
from .models import Vehicule, DistanceParcourue, ConsommationCarburant, DisponibiliteVehicule, CoutFonctionnement, CoutFinancier, IncidentSecurite, UtilisationActif, UtilisationVehicule, Chauffeur, FeuilleDeRoute, DocumentAdministratif
from .models_entreprise import Employe, ConfigurationMontantStatut, PresenceJournaliere
from .models_alertes import Alerte

class EmployeForm(forms.ModelForm):
    # Champs additionnels non présents dans le modèle mais attendus dans le template
    date_naissance = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de naissance"
    )
    lieu_naissance = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Lieu de naissance"
    )
    adresse = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        label="Adresse"
    )
    date_depart = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label="Date de départ"
    )
    numero_cnss = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        label="Numéro CNSS"
    )
    observations = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        label="Observations"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs non affichés dans le template comme optionnels
        self.fields['avances'].required = False
        self.fields['mode_calcul_heures_supp'].required = False
        self.fields['montant_heure_supp_jour_ouvrable'].required = False
        self.fields['montant_heure_supp_dimanche_ferie'].required = False
    
    class Meta:
        model = Employe
        fields = [
            'matricule', 'nom', 'prenom', 'fonction', 'telephone', 
            'date_embauche', 'salaire_journalier', 'statut', 
            'taux_horaire_specifique', 'avances', 
            'montant_heure_supp_jour_ouvrable', 'montant_heure_supp_dimanche_ferie',
            'mode_calcul_heures_supp'
        ]
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'salaire_journalier': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'taux_horaire_specifique': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'avances': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_heure_supp_jour_ouvrable': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'montant_heure_supp_dimanche_ferie': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'mode_calcul_heures_supp': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'matricule': 'Matricule',
            'nom': 'Nom',
            'prenom': 'Prénom',
            'fonction': 'Fonction',
            'telephone': 'Téléphone',
            'date_embauche': 'Date d\'embauche',
            'salaire_journalier': 'Salaire de Base (GNF)',
            'statut': 'Statut',
            'taux_horaire_specifique': 'Taux Horaire Spécifique (GNF)',
            'avances': 'Avances sur salaire (GNF)',
            'montant_heure_supp_jour_ouvrable': 'Montant heure supp jour ouvrable (GNF)',
            'montant_heure_supp_dimanche_ferie': 'Montant heure supp dimanche/férié (GNF)',
            'mode_calcul_heures_supp': 'Mode de calcul des heures supplémentaires',
        }

class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['id_vehicule', 'immatriculation', 'marque', 'modele', 'type_moteur', 'categorie', 
                 'date_mise_service', 'date_acquisition', 'kilometrage_initial', 'affectation', 
                 'statut_actuel', 'numero_chassis', 'numero_moteur', 'observations', 'chauffeur_principal']
        widgets = {
            'id_vehicule': forms.TextInput(attrs={'class': 'form-control'}),
            'immatriculation': forms.TextInput(attrs={'class': 'form-control'}),
            'marque': forms.TextInput(attrs={'class': 'form-control'}),
            'modele': forms.TextInput(attrs={'class': 'form-control'}),
            'type_moteur': forms.Select(attrs={'class': 'form-select'}),
            'categorie': forms.Select(attrs={'class': 'form-select'}),
            'date_mise_service': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_acquisition': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'kilometrage_initial': forms.NumberInput(attrs={'class': 'form-control'}),
            'affectation': forms.TextInput(attrs={'class': 'form-control'}),
            'statut_actuel': forms.Select(attrs={'class': 'form-select'}),
            'numero_chassis': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_moteur': forms.TextInput(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'chauffeur_principal': forms.Select(attrs={'class': 'form-select'}),
        }

class DistanceForm(forms.ModelForm):
    class Meta:
        model = DistanceParcourue
        fields = ['vehicule', 'date_debut', 'date_fin', 'km_debut', 'km_fin', 'distance_parcourue', 'limite_annuelle']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'km_debut': forms.NumberInput(attrs={'class': 'form-control km-input', 'min': '0', 'step': '1', 'placeholder': 'Kilométrage initial', 'required': 'required'}),
            'km_fin': forms.NumberInput(attrs={'class': 'form-control km-input', 'min': '0', 'step': '1', 'placeholder': 'Kilométrage final', 'required': 'required'}),
            'distance_parcourue': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly', 'placeholder': 'Calculé automatiquement'}),
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'limite_annuelle': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Optionnel'}),
        }
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Récupérer automatiquement le type de moteur du véhicule sélectionné
        if instance.vehicule:
            instance.type_moteur = instance.vehicule.type_moteur
        # Calculer automatiquement la distance si possible
        if instance.km_debut is not None and instance.km_fin is not None and instance.km_fin >= instance.km_debut:
            instance.distance_parcourue = instance.km_fin - instance.km_debut
        if commit:
            instance.save()
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre la distance non requise (calculée automatiquement)
        self.fields['distance_parcourue'].required = False

    def clean(self):
        cleaned = super().clean()
        km_debut = cleaned.get('km_debut')
        km_fin = cleaned.get('km_fin')

        if km_debut is not None and km_fin is not None:
            if km_fin < km_debut:
                self.add_error('km_fin', "Le kilométrage final doit être supérieur ou égal au kilométrage initial.")
            else:
                cleaned['distance_parcourue'] = (km_fin - km_debut)

        return cleaned


class AlerteForm(forms.ModelForm):
    class Meta:
        model = Alerte
        fields = ['vehicule', 'titre', 'description', 'niveau']
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'titre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
        }

# Formulaire de consommation supprimé car remplacé par ConsommationCarburantForm

# Formulaires pour les feuilles de route
class FeuilleRouteForm(forms.ModelForm):
    class Meta:
        model = FeuilleDeRoute
        fields = ['vehicule', 'chauffeur', 'date_depart', 'heure_depart', 'km_depart', 'destination', 'objet_deplacement']
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur': forms.Select(attrs={'class': 'form-select'}),
            'date_depart': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_depart': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'km_depart': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'objet_deplacement': forms.Select(attrs={'class': 'form-select'}),
        }

class FeuilleRouteUpdateForm(forms.ModelForm):
    class Meta:
        model = FeuilleDeRoute
        fields = ['km_depart', 'carburant_depart', 'date_retour', 'heure_retour', 'km_retour', 'carburant_retour', 'signature_chauffeur']
        widgets = {
            'km_depart': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'readonly': 'readonly'}),
            'carburant_depart': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01', 'readonly': 'readonly'}),
            'date_retour': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_retour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'km_retour': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'carburant_retour': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'signature_chauffeur': forms.CheckboxInput(attrs={'class': 'form-check-input', 'disabled': 'disabled'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Case visible, cochée par défaut et désactivée (informationnelle)
        self.fields['signature_chauffeur'].initial = True
        # S'assurer que l'attribut disabled est bien présent au rendu
        self.fields['signature_chauffeur'].widget.attrs.update({'disabled': 'disabled'})
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        # Calculer automatiquement la distance parcourue
        if instance.km_depart is not None and instance.km_retour is not None and instance.km_retour > instance.km_depart:
            instance.distance_parcourue = instance.km_retour - instance.km_depart
            
            # Calculer automatiquement le carburant utilisé
            if instance.carburant_depart is not None and instance.carburant_retour is not None:
                instance.carburant_utilise = instance.carburant_depart - instance.carburant_retour
                
                # Calculer automatiquement la consommation aux 100km
                if instance.distance_parcourue > 0:
                    instance.consommation = (instance.carburant_utilise * 100) / instance.distance_parcourue
        
        if commit:
            instance.save()
        return instance

class DisponibiliteForm(forms.ModelForm):
    class Meta:
        model = DisponibiliteVehicule
        fields = ['vehicule', 'date_debut', 'date_fin', 'heures_disponibles', 'heures_totales', 'disponibilite_pourcentage', 'raison_indisponibilite']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heures_disponibles': forms.NumberInput(attrs={'class': 'form-control'}),
            'heures_totales': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'disponibilite_pourcentage': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'raison_indisponibilite': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs calculés optionnels
        self.fields['heures_totales'].required = False
        self.fields['disponibilite_pourcentage'].required = False

    def clean(self):
        cleaned = super().clean()
        date_debut = cleaned.get('date_debut')
        date_fin = cleaned.get('date_fin')
        heures_dispo = cleaned.get('heures_disponibles')

        # Valider dates
        if date_debut and date_fin and date_fin < date_debut:
            self.add_error('date_fin', "La date de fin doit être postérieure ou égale à la date de début.")

        # Calculer heures totales et disponibilité
        if date_debut and date_fin:
            # Heures totales sur la période (inclusif) = (jours + 1) * 24
            delta_jours = (date_fin - date_debut).days + 1
            if delta_jours < 0:
                delta_jours = 0
            heures_totales = delta_jours * 24
            cleaned['heures_totales'] = heures_totales

            if heures_dispo is not None and heures_totales > 0:
                if heures_dispo > heures_totales:
                    self.add_error('heures_disponibles', "Les heures disponibles ne peuvent pas dépasser les heures totales de la période.")
                    heures_dispo = heures_totales
                dispo_pct = (heures_dispo * 100) / heures_totales
                if dispo_pct > 100:
                    dispo_pct = 100
                cleaned['disponibilite_pourcentage'] = round(dispo_pct, 2)
            else:
                cleaned['disponibilite_pourcentage'] = 0

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        # Recalcul de sécurité au cas où
        if instance.date_debut and instance.date_fin:
            delta_jours = (instance.date_fin - instance.date_debut).days + 1
            if delta_jours < 0:
                delta_jours = 0
            instance.heures_totales = delta_jours * 24
            if instance.heures_totales and instance.heures_totales > 0 and instance.heures_disponibles is not None:
                if instance.heures_disponibles > instance.heures_totales:
                    instance.heures_disponibles = instance.heures_totales
                instance.disponibilite_pourcentage = (instance.heures_disponibles * 100) / instance.heures_totales
        if commit:
            instance.save()
        return instance

class CoutFonctionnementForm(forms.ModelForm):
    class Meta:
        model = CoutFonctionnement
        fields = ['vehicule', 'date', 'type_cout', 'montant', 'kilometrage', 'cout_par_km', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type_cout': forms.TextInput(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'kilometrage': forms.NumberInput(attrs={'class': 'form-control'}),
            'cout_par_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
        }

class CoutFinancierForm(forms.ModelForm):
    class Meta:
        model = CoutFinancier
        fields = ['vehicule', 'date', 'type_cout', 'montant', 'kilometrage', 'cout_par_km', 'periode_amortissement', 'description']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'type_cout': forms.TextInput(attrs={'class': 'form-control'}),
            'montant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'kilometrage': forms.NumberInput(attrs={'class': 'form-control'}),
            'cout_par_km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001'}),
            'periode_amortissement': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
        }

class IncidentSecuriteForm(forms.ModelForm):
    class Meta:
        model = IncidentSecurite
        fields = ['vehicule', 'date_incident', 'conducteur', 'type_incident', 'gravite', 'lieu', 'description', 'mesures_prises', 'commentaires']
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'date_incident': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'conducteur': forms.Select(attrs={'class': 'form-select'}),
            'type_incident': forms.Select(attrs={'class': 'form-select'}),
            'gravite': forms.Select(attrs={'class': 'form-select'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'mesures_prises': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'commentaires': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class ConsommationCarburantForm(forms.ModelForm):
    class Meta:
        model = ConsommationCarburant
        fields = ['vehicule', 'date_plein1', 'km_plein1', 'date_plein2', 'km_plein2', 'litres_ajoutes', 'distance_parcourue', 'consommation_100km', 'consommation_constructeur']
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'date_plein1': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'km_plein1': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_plein2': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'km_plein2': forms.NumberInput(attrs={'class': 'form-control'}),
            'litres_ajoutes': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'distance_parcourue': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'consommation_100km': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'consommation_constructeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre optionnels les champs calculés pour permettre la saisie minimale
        self.fields['distance_parcourue'].required = False
        self.fields['consommation_100km'].required = False
        self.fields['consommation_constructeur'].required = False

    def clean(self):
        cleaned = super().clean()
        km1 = cleaned.get('km_plein1')
        km2 = cleaned.get('km_plein2')
        litres = cleaned.get('litres_ajoutes')

        # Validations de cohérence
        if km1 is not None and km2 is not None:
            if km2 <= km1:
                self.add_error('km_plein2', "Le kilométrage au second plein doit être supérieur au premier plein.")

        if litres is not None and litres <= 0:
            self.add_error('litres_ajoutes', "Les litres ajoutés doivent être supérieurs à 0.")

        # Calculs automatiques si possible
        if km1 is not None and km2 is not None and litres is not None and km2 > km1 and litres > 0:
            distance = km2 - km1
            cleaned['distance_parcourue'] = cleaned.get('distance_parcourue') or distance
            if distance > 0:
                conso = (litres * 100) / distance
                cleaned['consommation_100km'] = cleaned.get('consommation_100km') or round(conso, 2)

        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        # S'assurer que les champs calculés sont bien renseignés
        if instance.km_plein1 is not None and instance.km_plein2 is not None and instance.km_plein2 > instance.km_plein1:
            instance.distance_parcourue = instance.distance_parcourue or (instance.km_plein2 - instance.km_plein1)
            if instance.distance_parcourue and instance.distance_parcourue > 0 and instance.litres_ajoutes:
                instance.consommation_100km = instance.consommation_100km or ((instance.litres_ajoutes * 100) / instance.distance_parcourue)
        if commit:
            instance.save()
        return instance

class UtilisationActifForm(forms.ModelForm):
    class Meta:
        model = UtilisationActif
        fields = ['vehicule', 'date_debut', 'date_fin', 'conducteur', 'departement', 'motif_utilisation']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'conducteur': forms.Select(attrs={'class': 'form-select'}),
            'departement': forms.TextInput(attrs={'class': 'form-control'}),
            'motif_utilisation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
        }

class UtilisationVehiculeForm(forms.ModelForm):
    class Meta:
        model = UtilisationVehicule
        fields = ['vehicule', 'date_debut', 'date_fin', 'conducteur', 'departement', 'motif', 'km_depart', 'km_retour', 'observations']
        widgets = {
            'date_debut': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'conducteur': forms.Select(attrs={'class': 'form-select'}),
            'departement': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.TextInput(attrs={'class': 'form-control'}),
            'km_depart': forms.NumberInput(attrs={'class': 'form-control'}),
            'km_retour': forms.NumberInput(attrs={'class': 'form-control'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
        }


class ChauffeurForm(forms.ModelForm):
    class Meta:
        model = Chauffeur
        fields = ['nom', 'prenom', 'numero_permis', 'date_embauche', 'telephone', 'email', 'statut']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_permis': forms.TextInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'statut': forms.TextInput(attrs={'class': 'form-control'}),
        }


class FeuilleDeRouteForm(forms.ModelForm):
    class Meta:
        model = FeuilleDeRoute
        fields = ['vehicule', 'chauffeur', 'date_depart', 'heure_depart', 'destination', 'objet_deplacement']
        widgets = {
            'vehicule': forms.Select(attrs={'class': 'form-select'}),
            'chauffeur': forms.Select(attrs={'class': 'form-select'}),
            'date_depart': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_depart': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'destination': forms.TextInput(attrs={'class': 'form-control'}),
            'objet_deplacement': forms.Select(attrs={'class': 'form-select'}),
        }


class FeuilleDeRouteUpdateForm(forms.ModelForm):
    class Meta:
        model = FeuilleDeRoute
        fields = ['km_depart', 'carburant_depart', 'km_retour', 'carburant_retour', 'date_retour', 'heure_retour', 'signature_chauffeur']
        widgets = {
            'km_depart': forms.NumberInput(attrs={'class': 'form-control'}),
            'carburant_depart': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'km_retour': forms.NumberInput(attrs={'class': 'form-control'}),
            'carburant_retour': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'date_retour': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'heure_retour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'signature_chauffeur': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PointageJournalierForm(forms.ModelForm):
    """Formulaire pour le pointage journalier des employés"""
    
    class Meta:
        model = PresenceJournaliere
        fields = ['employe', 'date', 'statut']
        widgets = {
            'employe': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'employe': 'Employé',
            'date': 'Date',
            'statut': 'Statut de présence',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les employés par utilisateur
        if user:
            self.fields['employe'].queryset = Employe.objects.filter(user=user, statut='Actif')
        
        # Définir la date par défaut à aujourd'hui
        if not self.instance.pk:
            from django.utils import timezone
            self.fields['date'].initial = timezone.now().date()
    
    def clean(self):
        cleaned_data = super().clean()
        employe = cleaned_data.get('employe')
        date = cleaned_data.get('date')
        
        if employe and date:
            # Vérifier si un pointage existe déjà pour cet employé à cette date
            existing = PresenceJournaliere.objects.filter(
                employe=employe, 
                date=date
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise forms.ValidationError(
                    f"Un pointage existe déjà pour {employe} le {date.strftime('%d/%m/%Y')}"
                )
        
        return cleaned_data


class PointageRapideForm(forms.Form):
    """Formulaire pour pointer rapidement plusieurs employés"""
    date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Date de pointage'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Définir la date par défaut à aujourd'hui
        from django.utils import timezone
        self.fields['date'].initial = timezone.now().date()
        
        # Ajouter un champ de statut pour chaque employé actif
        if user:
            employes = Employe.objects.filter(user=user, statut='Actif').order_by('nom', 'prenom')
            for employe in employes:
                field_name = f'statut_{employe.id}'
                self.fields[field_name] = forms.ChoiceField(
                    choices=[('', '-- Sélectionner --')] + PresenceJournaliere.STATUT_CHOICES,
                    required=False,
                    widget=forms.Select(attrs={'class': 'form-select'}),
                    label=f'{employe.nom} {employe.prenom}'
                )
    
    def save(self, user):
        """Sauvegarde les pointages pour tous les employés sélectionnés"""
        date = self.cleaned_data['date']
        pointages_crees = 0
        pointages_mis_a_jour = 0
        
        employes = Employe.objects.filter(user=user, statut='Actif')
        for employe in employes:
            field_name = f'statut_{employe.id}'
            statut = self.cleaned_data.get(field_name)
            
            if statut:  # Si un statut a été sélectionné
                pointage, created = PresenceJournaliere.objects.update_or_create(
                    employe=employe,
                    date=date,
                    defaults={'statut': statut}
                )
                
                if created:
                    pointages_crees += 1
                else:
                    pointages_mis_a_jour += 1
        
        return pointages_crees, pointages_mis_a_jour


class ConfigurationSalaireForm(forms.Form):
    """
    Formulaire dynamique pour configurer les montants de salaire par statut de présence
    """
    employe = forms.ModelChoiceField(
        queryset=None,
        empty_label="-- Sélectionner un employé --",
        widget=forms.Select(attrs={
            'class': 'form-select form-select-lg',
            'id': 'id_employe',
            'onchange': 'this.form.submit()'
        }),
        label="Employé",
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        employe_id = kwargs.pop('employe_id', None)
        super().__init__(*args, **kwargs)
        
        if user:
            from .models_entreprise import Employe, PresenceJournaliere, ConfigurationSalaire
            
            # Filtrer les employés actifs par utilisateur
            self.fields['employe'].queryset = Employe.objects.filter(
                user=user, statut='Actif'
            ).order_by('nom', 'prenom')
            
            # Si un employé est sélectionné, créer les champs dynamiques
            if employe_id:
                # S'assurer que l'ID est un entier valide
                try:
                    employe_id_int = int(employe_id)
                except (TypeError, ValueError):
                    employe_id_int = None
                
                if employe_id_int:
                    try:
                        employe = Employe.objects.get(id=employe_id_int, user=user)
                        self.fields['employe'].initial = employe
                        
                        # Créer un champ pour chaque statut de présence
                        for statut_code, statut_label in PresenceJournaliere.STATUT_CHOICES:
                            field_name = f'montant_{statut_code.replace("(", "_").replace(")", "_").replace("&", "et")}'
                            
                            # Récupérer la configuration existante
                            montant_initial = 0
                            try:
                                config = ConfigurationSalaire.objects.get(
                                    employe=employe, 
                                    statut_presence=statut_code,
                                    actif=True
                                )
                                montant_initial = config.montant_journalier
                            except ConfigurationSalaire.DoesNotExist:
                                pass
                            
                            self.fields[field_name] = forms.DecimalField(
                                max_digits=10,
                                decimal_places=2,
                                min_value=0,
                                required=False,
                                initial=montant_initial,
                                label=statut_label,
                                help_text=f'Code: {statut_code}',
                                widget=forms.NumberInput(attrs={
                                    'class': 'form-control form-control-lg',
                                    'placeholder': '0.00',
                                    'step': '0.01',
                                    'data-statut': statut_code
                                })
                            )
                        
                    except Employe.DoesNotExist:
                        pass
    
    def save(self, user):
        """
        Sauvegarde les configurations de salaire
        """
        from .models_entreprise import Employe, ConfigurationSalaire, PresenceJournaliere
        
        employe = self.cleaned_data.get('employe')
        if not employe:
            return 0
            
        configurations_mises_a_jour = 0
        
        for statut_code, statut_label in PresenceJournaliere.STATUT_CHOICES:
            field_name = f'montant_{statut_code.replace("(", "_").replace(")", "_").replace("&", "et")}'
            
            if field_name in self.cleaned_data:
                montant = self.cleaned_data[field_name] or 0
                
                # Mettre à jour ou créer la configuration
                config, created = ConfigurationSalaire.objects.update_or_create(
                    employe=employe,
                    statut_presence=statut_code,
                    defaults={
                        'montant_journalier': montant,
                        'actif': True
                    }
                )
                configurations_mises_a_jour += 1
        
        return configurations_mises_a_jour
