from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal
import datetime


"""
Note: Le modèle Entreprise est défini dans models_accounts.py (Entreprise).
Ne pas redéclarer ici pour éviter les conflits d'enregistrement Django.
"""

# Modèles métiers pour l'entreprise

class Employe(models.Model):
    """Modèle pour les employés"""
    matricule = models.CharField(max_length=20, unique=True, verbose_name="Matricule")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    fonction = models.CharField(max_length=100, verbose_name="Fonction")
    
    # Champs additionnels requis par les formulaires
    telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    date_embauche = models.DateField(blank=True, null=True, verbose_name="Date d'embauche")
    
    STATUT_CHOICES = [
        ('Actif', 'Actif'),
        ('Inactif', 'Inactif'),
        ('Suspendu', 'Suspendu'),
        ('Congé', 'En congé'),
        ('Formation', 'En formation'),
    ]
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, default='Actif', verbose_name="Statut")
    salaire_journalier = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire journalier")
    avances = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Avances")
    
    # Configuration heures supplémentaires
    montant_heure_supp_jour_ouvrable = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant heure supp. jour ouvrable")
    montant_heure_supp_dimanche_ferie = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant heure supp. dimanche/férié")
    mode_calcul_heures_supp = models.CharField(max_length=50, default='standard', verbose_name="Mode calcul heures supp.")
    taux_horaire_specifique = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Taux horaire spécifique")
    
    # Configuration frais kilométriques
    valeur_km = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valeur par km (GNF)")
    
    # Configuration charges sociales et taxes
    taux_cnss_salarie_custom = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux CNSS salarié personnalisé")
    taux_cnss_employeur_custom = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux CNSS employeur personnalisé")
    calcul_salaire_auto = models.BooleanField(default=True, verbose_name="Calcul salaire automatique")
    appliquer_rts = models.BooleanField(default=True, verbose_name="Appliquer RTS")
    appliquer_cnss = models.BooleanField(default=True, verbose_name="Appliquer CNSS")
    taux_vf_custom = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Taux VF personnalisé")
    appliquer_vf = models.BooleanField(default=False, verbose_name="Appliquer VF")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'Employes'
        verbose_name = 'Employé'
        verbose_name_plural = 'Employés'
    
    def __str__(self):
        return f"{self.matricule} - {self.prenom} {self.nom}"

class ParametrePaie(models.Model):
    """Paramètres de configuration pour la paie"""
    nom = models.CharField(max_length=100, verbose_name="Nom du paramètre")
    valeur = models.CharField(max_length=255, verbose_name="Valeur")
    cle = models.CharField(max_length=100, blank=True, null=True, verbose_name="Clé")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'ParametresPaie'
        verbose_name = 'Paramètre de paie'
        verbose_name_plural = 'Paramètres de paie'

class PaieEmploye(models.Model):
    """Paie mensuelle des employés"""
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    mois = models.IntegerField(verbose_name="Mois")
    annee = models.IntegerField(verbose_name="Année")
    
    # Salaires et montants de base
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire de base")
    salaire_brut = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire brut")
    salaire_net = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire net")
    salaire_net_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire net à payer")
    
    # Jours et présence
    jours_mois = models.IntegerField(default=0, verbose_name="Jours du mois")
    jours_presence = models.IntegerField(default=0, verbose_name="Jours de présence")
    jours_repos = models.IntegerField(default=0, verbose_name="Jours de repos")
    absences = models.IntegerField(default=0, verbose_name="Absences")
    dimanches = models.IntegerField(default=0, verbose_name="Dimanches")
    conge = models.IntegerField(default=0, verbose_name="Congés")
    
    # Montants calculés
    montant_jours_travailles = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant jours travaillés")
    
    # Heures supplémentaires
    heures_supplementaires = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Heures supplémentaires")
    montant_heures_supplementaires = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant heures supplémentaires")
    montant_heures_supplement_dimanches = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant heures supp. dimanches")
    
    # Indemnités
    indemnite_transport = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Indemnité transport")
    indemnite_logement = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Indemnité logement")
    cherete_vie = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Cherté de vie")
    
    # Primes
    prime_discipline = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime discipline")
    prime_ferie = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime férié")
    
    # Déductions et charges
    cnss = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="CNSS")
    rts = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="RTS")
    vf = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="VF")
    avance_sur_salaire = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Avance sur salaire")
    sanction_vol_carburant = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Sanction vol carburant")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'PaieEmployes'
        unique_together = ['employe', 'mois', 'annee']
        verbose_name = 'Paie employé'
        verbose_name_plural = 'Paies employés'
    
    def __str__(self):
        return f"Paie {self.employe.matricule} - {self.mois}/{self.annee}"

class PresenceJournaliere(models.Model):
    """Présence journalière des employés"""
    # Liste normalisée des statuts utilisables dans tout le projet
    STATUT_CHOICES = [
        ('P(Am)', 'Présent matin'),
        ('P(Pm)', 'Présent après‑midi'),
        ('P(Am_&_Pm)', 'Présent matin & après‑midi'),
        ('P(dim_Am)', 'Présent dimanche matin'),
        ('P(dim_Pm)', 'Présent dimanche après‑midi'),
        ('P(dim_Am_&_Pm)', 'Présent dimanche matin & après‑midi'),
        ('A', 'Absent'),
        ('M', 'Malade'),
        ('M(Payer)', 'Malade (payé)'),
        ('OFF', 'Repos'),
    ]

    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    date = models.DateField(verbose_name="Date")
    present = models.BooleanField(default=True, verbose_name="Présent")
    statut = models.CharField(max_length=50, choices=STATUT_CHOICES, blank=True, null=True, verbose_name="Statut", default='P(Am_&_Pm)')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'PresenceJournaliere'
        unique_together = ['employe', 'date']

class SalaireMensuel(models.Model):
    """Salaire mensuel configuré"""
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    mois = models.IntegerField(verbose_name="Mois")
    annee = models.IntegerField(verbose_name="Année")
    
    # Salaires de base
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    salaire_base = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire de base")
    brut = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire brut")
    salaire_net = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire net")
    net_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Net à payer")
    
    # Jours et présence
    jours_mois = models.IntegerField(default=0, verbose_name="Jours du mois")
    jours_travailles = models.IntegerField(default=0, verbose_name="Jours travaillés")
    jours_absents = models.IntegerField(default=0, verbose_name="Jours absents")
    jours_off = models.IntegerField(default=0, verbose_name="Jours off")
    dimanches_travailles = models.IntegerField(default=0, verbose_name="Dimanches travaillés")
    
    # Heures supplémentaires
    heures_temps_supp = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Heures temps supplémentaire")
    montant_temps_supp = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant temps supplémentaire")
    
    # Indemnités
    ind_transport = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Indemnité transport")
    ind_logement = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Indemnité logement")
    cherte_vie = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Cherté de vie")
    
    # Primes
    prime_discipline = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime discipline")
    prime_ferie = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime férié")
    prime_dimanche = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prime dimanche")
    
    # Déductions et charges
    cnss = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="CNSS")
    rts = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="RTS")
    vf = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="VF")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'SalaireMensuel'
        verbose_name = 'Salaire mensuel'
        verbose_name_plural = 'Salaires mensuels'
        unique_together = ['employe', 'mois', 'annee']
    
    def __str__(self):
        return f"Salaire {self.employe.matricule} - {self.mois}/{self.annee}"

class PeseeCamion(models.Model):
    """Pesée des camions"""
    date = models.DateField(verbose_name='Date')
    first_name = models.CharField(max_length=100, verbose_name='Prénom')
    last_name = models.CharField(max_length=100, verbose_name='Nom')
    phone_number = models.CharField(max_length=20, verbose_name='Numéro de téléphone')
    plate = models.CharField(max_length=20, verbose_name="Plaque d'immatriculation")
    entry_card_number = models.CharField(max_length=20, verbose_name="Numéro de carte d'entrée")
    loading_zone = models.CharField(max_length=100, verbose_name='Zone de chargement')
    departure_time = models.TimeField(verbose_name='Heure de départ')
    weighing_start = models.TimeField(verbose_name='Heure de début de pesée')
    weighing_end = models.TimeField(verbose_name='Heure de fin de pesée')
    observation = models.TextField(blank=True, verbose_name='Observations')
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Quantité (tonnes)')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'PeseeCamions'
        verbose_name = 'Pesée de camion'
        verbose_name_plural = 'Pesées de camions'

class FicheBordMachine(models.Model):
    """Fiche de bord des machines"""
    date = models.DateField(verbose_name="Date")
    machine = models.CharField(max_length=100, verbose_name="Machine")
    
    # Informations de base
    site = models.CharField(max_length=100, verbose_name="Site")
    chauffeur = models.CharField(max_length=100, verbose_name="Chauffeur")
    
    # Période
    mois = models.IntegerField(verbose_name="Mois")
    annee = models.IntegerField(verbose_name="Année")
    
    # Compteurs et travail
    compteur_debut = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Compteur début")
    compteur_fin = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Compteur fin")
    distance_parcourue = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Distance parcourue")
    heures_travail = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Heures de travail")
    carburant_consomme = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Carburant consommé")
    
    # Services et maintenance
    dernier_service_date = models.DateField(blank=True, null=True, verbose_name="Date dernier service")
    dernier_service_heure = models.TimeField(blank=True, null=True, verbose_name="Heure dernier service")
    dernier_service_compteur = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Compteur dernier service")
    
    prochain_service_date = models.DateField(blank=True, null=True, verbose_name="Date prochain service")
    prochain_service_heure = models.TimeField(blank=True, null=True, verbose_name="Heure prochain service")
    prochain_service_compteur = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Compteur prochain service")
    
    # Observations
    observations = models.TextField(blank=True, null=True, verbose_name="Observations")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'FicheBordMachine'
        verbose_name = 'Fiche de bord machine'
        verbose_name_plural = 'Fiches de bord machines'
        unique_together = ['machine', 'mois', 'annee']
    
    def __str__(self):
        return f"Fiche {self.machine} - {self.mois}/{self.annee}"

class EntreeFicheBord(models.Model):
    """Entrées des fiches de bord"""
    fiche = models.ForeignKey(FicheBordMachine, on_delete=models.CASCADE, verbose_name="Fiche")
    fiche_bord = models.ForeignKey(FicheBordMachine, on_delete=models.CASCADE, related_name="entrees", verbose_name="Fiche de bord")
    
    # Informations de base
    date = models.DateField(verbose_name="Date")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    matricule = models.CharField(max_length=50, verbose_name="Matricule")
    responsable = models.CharField(max_length=100, verbose_name="Responsable")
    
    # Heures de travail
    heure = models.TimeField(verbose_name="Heure")
    demarrage_heure = models.TimeField(verbose_name="Heure de démarrage")
    arret_heure = models.TimeField(verbose_name="Heure d'arrêt")
    duree_travail_heure = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Durée travail (heures)")
    
    # Compteurs
    demarrage_compteur = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Compteur démarrage")
    arret_compteur = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Compteur arrêt")
    duree_travail_compteur = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Durée travail compteur")
    
    # Carburant
    carburant_heure = models.TimeField(blank=True, null=True, verbose_name="Heure carburant")
    carburant_quantite = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Quantité carburant")
    carburant_prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Prix unitaire carburant")
    carburant_cout_total = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Coût total carburant")
    
    # Description et observations
    description = models.TextField(verbose_name="Description")
    observation = models.TextField(blank=True, null=True, verbose_name="Observations")
    
    class Meta:
        db_table = 'EntreeFicheBord'
        verbose_name = 'Entrée fiche de bord'
        verbose_name_plural = 'Entrées fiches de bord'
    
    def __str__(self):
        return f"Entrée {self.nom} - {self.date}"

class FicheOr(models.Model):
    """Fiche de production d'or"""
    date = models.DateField(verbose_name="Date")
    mois = models.IntegerField(verbose_name="Mois")
    annee = models.IntegerField(verbose_name="Année")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'FicheOr'
        verbose_name = 'Fiche Or'
        verbose_name_plural = 'Fiches Or'
        unique_together = ['mois', 'annee']
    
    def __str__(self):
        return f"Fiche Or - {self.mois}/{self.annee}"

class EntreeFicheOr(models.Model):
    """Entrées des fiches d'or"""
    fiche = models.ForeignKey(FicheOr, on_delete=models.CASCADE, verbose_name="Fiche")
    fiche_or = models.ForeignKey(FicheOr, on_delete=models.CASCADE, related_name="entrees", verbose_name="Fiche Or")
    
    # Informations de base
    date = models.DateField(verbose_name="Date")
    lieu = models.CharField(max_length=100, verbose_name="Lieu")
    
    # Heures de travail
    heure_demarrage = models.TimeField(verbose_name="Heure de démarrage")
    heure_arret = models.TimeField(verbose_name="Heure d'arrêt")
    demarrage_travail = models.TimeField(verbose_name="Démarrage travail")
    arret_travail = models.TimeField(verbose_name="Arrêt travail")
    duree_heures = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Durée (heures)")
    
    # Effectifs
    effectif_demarrage = models.IntegerField(default=0, verbose_name="Effectif démarrage")
    effectif_arret = models.IntegerField(default=0, verbose_name="Effectif arrêt")
    
    # Production
    quantite = models.DecimalField(max_digits=10, decimal_places=3, verbose_name="Quantité")
    quantite_obtenue = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Quantité obtenue")
    qualite_carat = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Qualité (carat)")
    total_obtenu = models.DecimalField(max_digits=10, decimal_places=3, default=0, verbose_name="Total obtenu")
    
    class Meta:
        db_table = 'EntreeFicheOr'
        verbose_name = 'Entrée fiche Or'
        verbose_name_plural = 'Entrées fiches Or'
    
    def __str__(self):
        return f"Entrée {self.lieu} - {self.date}"

class HeureSupplementaire(models.Model):
    """Heures supplémentaires des employés"""
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    date = models.DateField(verbose_name="Date")
    heure_debut = models.TimeField(verbose_name="Heure de début")
    heure_fin = models.TimeField(verbose_name="Heure de fin")
    autorise_par = models.CharField(max_length=100, blank=True, null=True, verbose_name="Autorisé par")
    
    # Champs de calcul
    duree = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Durée (heures)")
    taux_horaire = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Taux horaire personnalisé")
    total_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total à payer")
    
    # Champs de statut
    type_jour = models.CharField(max_length=20, default='ouvrable', choices=[
        ('ouvrable', 'Jour ouvrable'),
        ('dimanche', 'Dimanche'),
        ('ferie', 'Jour férié')
    ], verbose_name="Type de jour")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'HeuresSupplementaires'
        verbose_name = 'Heure supplémentaire'
        verbose_name_plural = 'Heures supplémentaires'
        unique_together = ['employe', 'date', 'heure_debut']
    
    def __str__(self):
        return f"{self.employe.matricule} - {self.date} ({self.duree}h)"
    
    def obtenir_taux_horaire_employe(self):
        """Obtient le taux horaire configuré pour l'employé selon le type de jour"""
        if self.type_jour == 'dimanche' or self.type_jour == 'ferie':
            return self.employe.montant_heure_supp_dimanche_ferie or 0
        else:
            return self.employe.montant_heure_supp_jour_ouvrable or 0
    
    def get_montant_supp(self):
        """Retourne le montant horaire à utiliser (manuel ou configuré)"""
        if self.taux_horaire and self.taux_horaire > 0:
            return float(self.taux_horaire)
        return float(self.obtenir_taux_horaire_employe())
    
    def get_montant_pour_saisie(self):
        """Retourne la valeur pour le champ de saisie manuelle"""
        if self.taux_horaire and self.taux_horaire > 0:
            return float(self.taux_horaire)
        return None
    
    def get_total_calcule(self):
        """Retourne le total calculé dynamiquement: duree * taux effectif"""
        try:
            return round(float(self.duree or 0) * float(self.get_montant_supp() or 0), 2)
        except Exception:
            return 0
    
    def save(self, *args, **kwargs):
        """Calcul automatique de la durée et du total lors de la sauvegarde"""
        skip_auto_calc = kwargs.pop('skip_auto_calc', False)
        
        if not skip_auto_calc:
            # Calcul de la durée en heures
            if self.heure_debut and self.heure_fin:
                debut = self.heure_debut
                fin = self.heure_fin
                
                # Conversion en minutes pour le calcul
                debut_minutes = debut.hour * 60 + debut.minute
                fin_minutes = fin.hour * 60 + fin.minute
                
                # Gestion du passage à minuit
                if fin_minutes < debut_minutes:
                    fin_minutes += 24 * 60
                
                duree_minutes = fin_minutes - debut_minutes
                self.duree = round(duree_minutes / 60, 2)
            
            # Calcul du total à payer
            montant_horaire = self.get_montant_supp()
            self.total_a_payer = round(float(self.duree) * montant_horaire, 2)
        
        super().save(*args, **kwargs)


class FraisKilometrique(models.Model):
    """Frais kilométriques (Bus/Km) des employés"""
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    date = models.DateField(verbose_name="Date")
    kilometres = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Kilomètres parcourus")
    valeur_par_km = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Valeur par km (GNF)")
    total_a_payer = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Total à payer")
    description = models.TextField(blank=True, null=True, verbose_name="Description/Trajet")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'FraisKilometriques'
        verbose_name = 'Frais kilométrique'
        verbose_name_plural = 'Frais kilométriques'
        ordering = ['-date', '-id']
    
    def __str__(self):
        return f"{self.employe.matricule} - {self.date} ({self.kilometres}km)"
    
    def obtenir_valeur_km_employe(self):
        """Obtient la valeur par km configurée pour l'employé"""
        return self.employe.valeur_km or 0
    
    def get_valeur_km(self):
        """Retourne la valeur par km à utiliser (manuelle ou configurée)"""
        if self.valeur_par_km and self.valeur_par_km > 0:
            return float(self.valeur_par_km)
        return float(self.obtenir_valeur_km_employe())
    
    def get_valeur_pour_saisie(self):
        """Retourne la valeur pour le champ de saisie manuelle"""
        if self.valeur_par_km and self.valeur_par_km > 0:
            return float(self.valeur_par_km)
        return None
    
    def get_total_calcule(self):
        """Retourne le total calculé dynamiquement: kilometres * valeur_par_km"""
        try:
            return round(float(self.kilometres or 0) * float(self.get_valeur_km() or 0), 2)
        except Exception:
            return 0
    
    def save(self, *args, **kwargs):
        """Calcul automatique du total lors de la sauvegarde"""
        skip_auto_calc = kwargs.pop('skip_auto_calc', False)
        
        if not skip_auto_calc:
            # Calcul du total à payer
            valeur_km = self.get_valeur_km()
            self.total_a_payer = round(float(self.kilometres) * valeur_km, 2)
        
        super().save(*args, **kwargs)


class ConfigurationMontantStatut(models.Model):
    """Configuration des montants par statut"""
    statut = models.CharField(max_length=100, verbose_name="Statut")
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'ConfigurationMontantStatut'

class ConfigurationMontantEmploye(models.Model):
    """Configuration des montants par employé"""
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    montant = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'ConfigurationMontantEmploye'

class ConfigurationSalaire(models.Model):
    """Configuration des montants journaliers par statut de présence"""
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE, verbose_name="Employé")
    statut_presence = models.CharField(max_length=50, verbose_name="Statut de présence", default='P(Am_&_Pm)')
    montant_journalier = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant journalier (GNF)")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'ConfigurationSalaire'
        unique_together = ['employe', 'statut_presence']

class ConfigurationChargesSociales(models.Model):
    """Configuration des charges sociales"""
    nom = models.CharField(max_length=100, verbose_name="Nom")
    taux = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Taux (%)")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'ConfigurationChargesSociales'

class ConfigurationHeureSupplementaire(models.Model):
    """Configuration des heures supplémentaires"""
    # Configuration de base
    salaire_mensuel_base = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Salaire mensuel de base")
    heures_normales_mois = models.DecimalField(max_digits=5, decimal_places=2, default=173.33, verbose_name="Heures normales par mois")
    
    # Configuration jours ouvrables
    taux_jour_ouvrable = models.DecimalField(max_digits=5, decimal_places=2, default=1.5, verbose_name="Taux jour ouvrable")
    montant_jour_ouvrable = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant jour ouvrable")
    
    # Configuration dimanche et férié
    taux_dimanche_ferie = models.DecimalField(max_digits=5, decimal_places=2, default=2.0, verbose_name="Taux dimanche/férié")
    montant_dimanche_ferie = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Montant dimanche/férié")
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Date de modification")
    
    class Meta:
        db_table = 'ConfigurationHeureSupplementaire'
        verbose_name = 'Configuration heure supplémentaire'
        verbose_name_plural = 'Configurations heures supplémentaires'
    
    def __str__(self):
        return f"Config HS - Base: {self.salaire_mensuel_base} GNF"

class DataSynchronizer(models.Model):
    """Synchroniseur de données"""
    nom = models.CharField(max_length=100, verbose_name="Nom")
    derniere_sync = models.DateTimeField(auto_now=True, verbose_name="Dernière synchronisation")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        db_table = 'DataSynchronizer'
