from django import forms
from django.forms import inlineformset_factory
from .models_entreprise import (
    PeseeCamion, ParametrePaie, Employe, PresenceJournaliere, PaieEmploye,
    HeureSupplementaire, SalaireMensuel, FicheBordMachine, EntreeFicheBord,
    FicheOr, EntreeFicheOr, ConfigurationHeureSupplementaire
)


class PeseeCamionForm(forms.ModelForm):
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
        model = PeseeCamion
        fields = [
            'date', 'first_name', 'last_name', 'phone_number', 'plate',
            'entry_card_number', 'loading_zone', 'departure_time', 'weighing_start',
            'weighing_end', 'observation', 'quantity'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'plate': forms.TextInput(attrs={'class': 'form-control'}),
            'entry_card_number': forms.TextInput(attrs={'class': 'form-control'}),
            'loading_zone': forms.TextInput(attrs={'class': 'form-control'}),
            'departure_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'weighing_start': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'weighing_end': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class ParametrePaieForm(forms.ModelForm):
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
        model = ParametrePaie
        fields = ['cle', 'valeur', 'description']
        widgets = {
            'cle': forms.TextInput(attrs={'class': 'form-control'}),
            'valeur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class EmployeForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Configurer les choix pour le statut
        self.fields['statut'].choices = Employe.STATUT_CHOICES
        
        # Ajouter des classes CSS et des labels personnalisés
        self.fields['calcul_salaire_auto'].label = "Calculer automatiquement le salaire de base depuis les présences"
        self.fields['calcul_salaire_auto'].help_text = "Si activé, le salaire sera calculé à partir des pointages (P(Am), P(Pm), P(Am&Pm))"
        
        self.fields['appliquer_cnss'].label = "Appliquer CNSS"
        self.fields['appliquer_cnss'].help_text = "Caisse Nationale de Sécurité Sociale (5% salarié + 18% employeur)"
        
        self.fields['appliquer_rts'].label = "Appliquer RTS"
        self.fields['appliquer_rts'].help_text = "Retenue sur Traitement et Salaire (barème progressif)"
        
        self.fields['appliquer_vf'].label = "Appliquer VF"
        self.fields['appliquer_vf'].help_text = "Versement Forfaitaire (7-10% du chiffre d'affaires)"
        
        self.fields['taux_cnss_salarie_custom'].label = "Taux CNSS salarié personnalisé (%)"
        self.fields['taux_cnss_salarie_custom'].help_text = "Laisser vide pour utiliser 5% (taux standard)"
        
        self.fields['taux_cnss_employeur_custom'].label = "Taux CNSS employeur personnalisé (%)"
        self.fields['taux_cnss_employeur_custom'].help_text = "Laisser vide pour utiliser 18% (taux standard)"
        
        self.fields['taux_vf_custom'].label = "Taux VF personnalisé (%)"
        self.fields['taux_vf_custom'].help_text = "Entre 7% et 10% (laisser vide pour 7%)"
        
        # Rendre certains champs optionnels
        self.fields['taux_cnss_salarie_custom'].required = False
        self.fields['taux_cnss_employeur_custom'].required = False
        self.fields['taux_vf_custom'].required = False
        self.fields['taux_horaire_specifique'].required = False
        # Le salaire peut être vide si calcul automatique
        self.fields['salaire_journalier'].required = False
        # Clarifier le libellé du salaire pour l'utilisateur
        self.fields['salaire_journalier'].label = "Salaire de base (GNF - journalier)"
        self.fields['salaire_journalier'].help_text = (
            "Montant de base par jour. Laissez vide si vous cochez 'Calculer automatiquement le salaire'."
        )
        
        # Définir les valeurs initiales pour les champs cachés
        self.fields['montant_heure_supp_jour_ouvrable'].initial = 0
        self.fields['montant_heure_supp_dimanche_ferie'].initial = 0
        self.fields['mode_calcul_heures_supp'].initial = 'standard'
        # Ne pas exiger ces champs dans le formulaire simple (ils sont gérés avec des valeurs par défaut)
        self.fields['montant_heure_supp_jour_ouvrable'].required = False
        self.fields['montant_heure_supp_dimanche_ferie'].required = False
        self.fields['mode_calcul_heures_supp'].required = False
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    
    class Meta:
        model = Employe
        fields = [
            'matricule', 'prenom', 'nom', 'fonction',
            'telephone', 'date_embauche', 'statut', 'salaire_journalier',
            'taux_horaire_specifique', 'calcul_salaire_auto',
            # Champs obligatoires manquants
            'montant_heure_supp_jour_ouvrable', 'montant_heure_supp_dimanche_ferie', 'mode_calcul_heures_supp',
            # Charges sociales guinéennes
            'appliquer_cnss', 'appliquer_rts', 'appliquer_vf',
            'taux_cnss_salarie_custom', 'taux_cnss_employeur_custom', 'taux_vf_custom'
        ]
        widgets = {
            'matricule': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: EMP-001 ou 2025-0001'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Mamadou'}),
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Diallo'}),
            'fonction': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Chauffeur, Mécanicien, Comptable'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+224 6XX XX XX XX'}),
            'date_embauche': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'placeholder': 'AAAA-MM-JJ'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
            'salaire_journalier': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'placeholder': 'Sera calculé automatiquement si option activée'
            }),
            'taux_horaire_specifique': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'placeholder': 'Laisser vide pour utiliser le calcul standard'
            }),
            
            # Calcul automatique du salaire
            'calcul_salaire_auto': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'calculSalaireAuto'
            }),
            
            # Charges sociales - Cases à cocher
            'appliquer_cnss': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'appliquerCNSS'
            }),
            'appliquer_rts': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'appliquerRTS'
            }),
            'appliquer_vf': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'appliquerVF'
            }),
            
            # Taux personnalisés
            'taux_cnss_salarie_custom': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '5.00 (défaut)'
            }),
            'taux_cnss_employeur_custom': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '18.00 (défaut)'
            }),
            'taux_vf_custom': forms.NumberInput(attrs={
                'class': 'form-control form-control-sm',
                'step': '0.01',
                'min': '7',
                'max': '10',
                'placeholder': '7.00 à 10.00'
            }),
            
            # Champs heures supplémentaires (cachés avec valeurs par défaut)
            'montant_heure_supp_jour_ouvrable': forms.HiddenInput(),
            'montant_heure_supp_dimanche_ferie': forms.HiddenInput(),
            'mode_calcul_heures_supp': forms.HiddenInput(),
        }
        
    def clean(self):
        """Validation personnalisée pour s'assurer que les valeurs par défaut sont définies"""
        cleaned_data = super().clean()
        
        # S'assurer que tous les champs numériques ont des valeurs par défaut
        numeric_fields = [
            'taux_cnss_salarie_custom', 'taux_cnss_employeur_custom', 'taux_vf_custom',
            'taux_horaire_specifique', 'montant_heure_supp_jour_ouvrable', 
            'montant_heure_supp_dimanche_ferie'
        ]
        
        for field in numeric_fields:
            if not cleaned_data.get(field):
                cleaned_data[field] = 0
        
        # S'assurer que mode_calcul_heures_supp a une valeur
        if not cleaned_data.get('mode_calcul_heures_supp'):
            cleaned_data['mode_calcul_heures_supp'] = 'standard'
        
        # Salaire journalier: requis si pas de calcul auto
        calcul_auto = cleaned_data.get('calcul_salaire_auto')
        salaire = cleaned_data.get('salaire_journalier')
        if calcul_auto:
            # autoriser vide => 0
            if not salaire:
                cleaned_data['salaire_journalier'] = 0
        else:
            if salaire in [None, "", 0, 0.0, 0.00]:
                self.add_error('salaire_journalier', "Veuillez renseigner le salaire de base ou activer le calcul automatique.")
            
        return cleaned_data


class PresenceJournaliereForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['employe'].queryset = Employe.objects.filter(user=self.user)
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.user and not instance.pk:
            instance.user = self.user
        if commit:
            instance.save()
        return instance
    
    class Meta:
        model = PresenceJournaliere
        fields = ['employe', 'date', 'statut']
        widgets = {
            'employe': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'statut': forms.Select(attrs={'class': 'form-select'}),
        }


class PaieEmployeForm(forms.ModelForm):
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
        model = PaieEmploye
        fields = [
            'salaire_base', 'jours_presence', 'absences', 'dimanches', 'montant_jours_travailles',
            'montant_heures_supplement_dimanches', 'heures_supplementaires',
            'montant_heures_supplementaires', 'prime_ferie', 'conge',
            'avance_sur_salaire', 'sanction_vol_carburant',
            'prime_discipline', 'cherete_vie', 'indemnite_transport', 'indemnite_logement',
            'jours_repos', 'jours_mois', 'salaire_brut', 'cnss', 'rts', 'vf', 'salaire_net', 'salaire_net_a_payer'
        ]
        widgets = {
            'salaire_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'jours_presence': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'absences': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'dimanches': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'montant_jours_travailles': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'montant_heures_supplement_dimanches': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'heures_supplementaires': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'montant_heures_supplementaires': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prime_ferie': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'conge': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'avance_sur_salaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'sanction_vol_carburant': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prime_discipline': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cherete_vie': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'indemnite_transport': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'indemnite_logement': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'jours_repos': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'jours_mois': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
            'salaire_brut': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'cnss': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'rts': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'vf': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'salaire_net': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
            'salaire_net_a_payer': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
        }


class HeureSupplementaireForm(forms.ModelForm):
    """
    Formulaire simplifié pour ajouter des heures supplémentaires
    Le poste et taux horaire sont récupérés automatiquement selon l'employé
    """
    
    class Meta:
        model = HeureSupplementaire
        fields = ['employe', 'date', 'heure_debut', 'heure_fin', 'autorise_par']
        widgets = {
            'employe': forms.Select(attrs={
                'class': 'form-select',
                'required': True,
                'id': 'id_employe'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'required': True
            }),
            'heure_debut': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'value': '08:00'
            }),
            'heure_fin': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
                'value': '10:00'
            }),
            'autorise_par': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la personne qui autorise'
            })
        }
        labels = {
            'employe': 'Employé',
            'date': 'Date',
            'heure_debut': 'Heure de début',
            'heure_fin': 'Heure de fin',
            'autorise_par': 'Autorisé par'
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Debug pour diagnostiquer le problème
        print(f"=== DEBUG HeureSupplementaireForm ===")
        print(f"User reçu: {user}")
        
        if user:
            # Récupérer tous les employés de l'utilisateur
            employes = Employe.objects.filter(user=user).order_by('matricule')
            print(f"Nombre d'employés trouvés: {employes.count()}")
            
            # Construire les choices manuellement pour un contrôle total
            choices = [('', 'Sélectionnez un employé')]
            for emp in employes:
                choice_label = f"{emp.prenom} {emp.nom} ({emp.matricule})"
                choices.append((emp.id, choice_label))
                print(f"Employé ajouté: {choice_label}")
            
            # Appliquer les choices au widget
            self.fields['employe'].choices = choices
            
            # Pré-remplir les champs par défaut
            self.fields['date'].initial = '2025-07-20'
            
            # Pré-remplir "autorise_par"
            if user.first_name and user.last_name:
                self.fields['autorise_par'].initial = f"{user.first_name} {user.last_name}"
            else:
                self.fields['autorise_par'].initial = user.username
        else:
            print("ERREUR: Aucun utilisateur fourni au formulaire!")
            self.fields['employe'].choices = [('', 'Aucun employé disponible')]
        
        print("=== FIN DEBUG HeureSupplementaireForm ===")
    
    def clean(self):
        cleaned_data = super().clean()
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        
        # Calculer automatiquement la durée si les heures sont fournies
        if heure_debut and heure_fin:
            from datetime import datetime, timedelta
            from decimal import Decimal, ROUND_HALF_UP
            
            debut = datetime.combine(datetime.today(), heure_debut)
            fin = datetime.combine(datetime.today(), heure_fin)
            
            # Cas spécial: si début = fin, considérer que c'est une journée complète (24h)
            if debut == fin:
                duree_heures = 24.0
                print(f"DEBUG clean() - Cas spécial début=fin: {heure_debut}, durée = 24h")
            else:
                # Validation: l'heure de fin doit être après l'heure de début
                # (sauf cas spécial début=fin géré ci-dessus)
                if fin < debut:
                    # Accepter les heures sur deux jours (ex: 22:00 à 06:00)
                    fin = fin + timedelta(days=1)
                
                duree_timedelta = fin - debut
                duree_heures = duree_timedelta.total_seconds() / 3600
            
            # Convertir en Decimal pour cohérence avec save()
            cleaned_data['duree'] = Decimal(str(duree_heures)).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            print(f"DEBUG clean() - Durée calculée: {duree_heures} heures")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        print(f"📝 FORM SAVE: Employé={instance.employe}, Début={instance.heure_debut}, Fin={instance.heure_fin}")
        
        # Laisser le modèle gérer tous les calculs automatiquement
        # Le modèle HeureSupplementaire.save() calculera :
        # - La durée automatiquement
        # - Le taux horaire selon la configuration
        # - Le total à payer
        
        if commit:
            instance.save()  # Déclenche HeureSupplementaire.save() avec tous les calculs
            print(f"✅ FORM SAVE: Sauvegarde réussie - Durée={instance.duree}, Total={instance.total_a_payer}")
        
        return instance


class SalaireMensuelForm(forms.ModelForm):
    class Meta:
        model = SalaireMensuel
        fields = ['employe', 'mois', 'annee', 'salaire_base', 'rts', 'cnss', 'vf', 'prime_discipline',
                 'heures_temps_supp', 'montant_temps_supp', 'cherte_vie', 'ind_transport', 'ind_logement',
                 'brut', 'salaire_net', 'jours_mois', 'jours_travailles', 'dimanches_travailles',
                 'prime_dimanche', 'jours_off', 'jours_absents', 'prime_ferie', 'net_a_payer']
        widgets = {
            'employe': forms.Select(attrs={'class': 'form-select'}),
            'mois': forms.Select(attrs={'class': 'form-select', 'choices': [(i, i) for i in range(1, 13)]}),
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'salaire_base': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'rts': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cnss': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vf': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prime_discipline': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'heures_temps_supp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
            'montant_temps_supp': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cherte_vie': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ind_transport': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ind_logement': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'brut': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'salaire_net': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'jours_mois': forms.NumberInput(attrs={'class': 'form-control'}),
            'jours_travailles': forms.NumberInput(attrs={'class': 'form-control'}),
            'dimanches_travailles': forms.NumberInput(attrs={'class': 'form-control'}),
            'prime_dimanche': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'jours_off': forms.NumberInput(attrs={'class': 'form-control'}),
            'jours_absents': forms.NumberInput(attrs={'class': 'form-control'}),
            'prime_ferie': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'net_a_payer': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class FicheBordMachineForm(forms.ModelForm):
    class Meta:
        model = FicheBordMachine
        fields = ['mois', 'annee', 'dernier_service_date', 'dernier_service_heure', 'dernier_service_compteur',
                 'prochain_service_date', 'prochain_service_heure', 'prochain_service_compteur']
        widgets = {
            'mois': forms.Select(attrs={'class': 'form-select', 'choices': [(i, i) for i in range(1, 13)]}),
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'dernier_service_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'dernier_service_heure': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'dernier_service_compteur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'prochain_service_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'prochain_service_heure': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'prochain_service_compteur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }


class EntreeFicheBordForm(forms.ModelForm):
    class Meta:
        model = EntreeFicheBord
        fields = ['fiche_bord', 'date', 'nom', 'matricule', 'demarrage_heure', 'demarrage_compteur',
                 'arret_heure', 'arret_compteur', 'duree_travail_heure', 'duree_travail_compteur',
                 'carburant_quantite', 'carburant_heure', 'carburant_prix_unitaire',
                 'carburant_cout_total', 'responsable', 'observation']
        widgets = {
            'fiche_bord': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'matricule': forms.TextInput(attrs={'class': 'form-control'}),
            'demarrage_heure': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'demarrage_compteur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'arret_heure': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'arret_compteur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'duree_travail_heure': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'duree_travail_compteur': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'carburant_quantite': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'carburant_heure': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'carburant_prix_unitaire': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'carburant_cout_total': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'responsable': forms.TextInput(attrs={'class': 'form-control'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class FicheOrForm(forms.ModelForm):
    class Meta:
        model = FicheOr
        fields = ['mois', 'annee']
        widgets = {
            'mois': forms.Select(attrs={'class': 'form-select', 'choices': [(i, i) for i in range(1, 13)]}),
            'annee': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
        }

class FicheOrFormManuel(forms.Form):
    """Formulaire manuel pour la saisie des fiches d'or sans migration du modèle"""
    date = forms.DateField(
        label="Date",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    site = forms.CharField(
        label="Site",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    responsable = forms.CharField(
        label="Responsable",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    equipe = forms.CharField(
        label="Équipe",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    quantite_totale = forms.DecimalField(
        label="Quantité totale (g)",
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_quantite_totale'})
    )
    prix_unitaire = forms.DecimalField(
        label="Prix unitaire (GNF/g)",
        max_digits=12,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'id': 'id_prix_unitaire'})
    )
    valeur_estimee = forms.DecimalField(
        label="Valeur estimée (GNF)",
        max_digits=15,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly', 'id': 'id_valeur_estimee'})
    )
    observations = forms.CharField(
        label="Observations",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class EntreeFicheOrForm(forms.ModelForm):
    class Meta:
        model = EntreeFicheOr
        fields = ['fiche_or', 'date', 'lieu', 'demarrage_travail', 'heure_demarrage', 'effectif_demarrage',
                 'arret_travail', 'heure_arret', 'effectif_arret', 'duree_heures', 'quantite_obtenue',
                 'qualite_carat', 'total_obtenu']
        widgets = {
            'fiche_or': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'demarrage_travail': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'heure_demarrage': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'effectif_demarrage': forms.NumberInput(attrs={'class': 'form-control'}),
            'arret_travail': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'heure_arret': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'effectif_arret': forms.NumberInput(attrs={'class': 'form-control'}),
            'duree_heures': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'quantite_obtenue': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'qualite_carat': forms.Select(attrs={'class': 'form-select'}),
            'total_obtenu': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'readonly': 'readonly'}),
        }


class ConfigurationHeureSupplementaireForm(forms.ModelForm):
    """
    Formulaire pour configurer les taux de majoration des heures supplémentaires
    selon le modèle guinéen
    """
    class Meta:
        model = ConfigurationHeureSupplementaire
        fields = ['taux_jour_ouvrable', 'taux_dimanche_ferie', 'montant_jour_ouvrable', 'montant_dimanche_ferie', 'salaire_mensuel_base', 'heures_normales_mois']
        widgets = {
            'taux_jour_ouvrable': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '1.0',
                'placeholder': 'Ex: 1.5 pour +50%'
            }),
            'taux_dimanche_ferie': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '1.0',
                'placeholder': 'Ex: 2.0 pour +100%'
            }),
            'montant_jour_ouvrable': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant fixe par heure en GNF'
            }),
            'montant_dimanche_ferie': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'placeholder': 'Montant fixe par heure en GNF'
            }),
            'salaire_mensuel_base': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '0',
                'placeholder': 'Salaire mensuel de base en GNF'
            }),
            'heures_normales_mois': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01',
                'min': '1.0',
                'placeholder': 'Ex: 173.33 pour 40h/semaine'
            }),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        
        print(f"DEBUG - clean() - Données avant nettoyage: {cleaned_data}")
        
        # Fournir des valeurs par défaut pour les champs vides afin d'éviter les erreurs NOT NULL
        if not cleaned_data.get('taux_jour_ouvrable'):
            cleaned_data['taux_jour_ouvrable'] = 1.5
            print(f"DEBUG - clean() - taux_jour_ouvrable défini à 1.5")
        if not cleaned_data.get('taux_dimanche_ferie'):
            cleaned_data['taux_dimanche_ferie'] = 2.0
            print(f"DEBUG - clean() - taux_dimanche_ferie défini à 2.0")
        if not cleaned_data.get('montant_jour_ouvrable'):
            cleaned_data['montant_jour_ouvrable'] = 0
            print(f"DEBUG - clean() - montant_jour_ouvrable défini à 0")
        if not cleaned_data.get('montant_dimanche_ferie'):
            cleaned_data['montant_dimanche_ferie'] = 0
            print(f"DEBUG - clean() - montant_dimanche_ferie défini à 0")
        if not cleaned_data.get('salaire_mensuel_base'):
            cleaned_data['salaire_mensuel_base'] = 0
            print(f"DEBUG - clean() - salaire_mensuel_base défini à 0")
        if not cleaned_data.get('heures_normales_mois'):
            cleaned_data['heures_normales_mois'] = 173.33
            print(f"DEBUG - clean() - heures_normales_mois défini à 173.33")
            
        print(f"DEBUG - clean() - Données après nettoyage: {cleaned_data}")
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Rendre tous les champs optionnels
        for field_name, field in self.fields.items():
            field.required = False
            # Ajouter une indication visuelle que les champs sont optionnels
            if 'placeholder' in field.widget.attrs:
                field.widget.attrs['placeholder'] += ' (optionnel)'
        
        if user:
            # Ajouter l'utilisateur à l'instance du formulaire
            self.instance.user = user
            
            # Récupérer l'entreprise associée à l'utilisateur si elle existe
            try:
                from .models import Entreprise
                entreprise = Entreprise.objects.filter(user=user).first()
                if entreprise:
                    self.instance.entreprise = entreprise
            except Exception as e:
                print(f"Erreur lors de la récupération de l'entreprise: {e}")
                
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Debug: afficher les données avant sauvegarde
        print(f"DEBUG - Données à sauvegarder:")
        print(f"  - taux_jour_ouvrable: {instance.taux_jour_ouvrable}")
        print(f"  - taux_dimanche_ferie: {instance.taux_dimanche_ferie}")
        print(f"  - montant_jour_ouvrable: {instance.montant_jour_ouvrable}")
        print(f"  - montant_dimanche_ferie: {instance.montant_dimanche_ferie}")
        print(f"  - salaire_mensuel_base: {instance.salaire_mensuel_base}")
        print(f"  - heures_normales_mois: {instance.heures_normales_mois}")
        print(f"  - user: {instance.user}")
        print(f"  - instance.id: {instance.id}")
        
        if commit:
            instance.save()
            print(f"DEBUG - Instance sauvegardée avec ID: {instance.id}")
            
            # Vérifier que les données sont bien en base
            from .models_entreprise import ConfigurationHeureSupplementaire
            saved_config = ConfigurationHeureSupplementaire.objects.get(id=instance.id)
            print(f"DEBUG - Données en base après sauvegarde:")
            print(f"  - taux_jour_ouvrable: {saved_config.taux_jour_ouvrable}")
            print(f"  - taux_dimanche_ferie: {saved_config.taux_dimanche_ferie}")
            print(f"  - montant_jour_ouvrable: {saved_config.montant_jour_ouvrable}")
            
        return instance

class FicheBordMachineForm(forms.ModelForm):
    class Meta:
        model = FicheBordMachine
        fields = ['date', 'machine', 'chauffeur', 'site', 'heures_travail', 
                 'compteur_debut', 'compteur_fin', 'distance_parcourue', 
                 'carburant_consomme', 'observations']
        widgets = {
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'machine': forms.TextInput(attrs={'class': 'form-control'}),
            'chauffeur': forms.TextInput(attrs={'class': 'form-control'}),
            'site': forms.TextInput(attrs={'class': 'form-control'}),
            'heures_travail': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'compteur_debut': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'compteur_fin': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'distance_parcourue': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'carburant_consomme': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'observations': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
