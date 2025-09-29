from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .models_accounts import Entreprise

# Import des modèles d'entreprise
from .models_entreprise import (
    PeseeCamion, ParametrePaie, Employe, PresenceJournaliere, PaieEmploye,
    HeureSupplementaire, SalaireMensuel, FicheBordMachine, EntreeFicheBord,
    FicheOr, EntreeFicheOr
)

# Modèles basés sur la structure de la base de données existante

class Vehicule(models.Model):
    MOTEUR_CHOICES = [
        ('Essence', 'Essence'),
        ('Diesel', 'Diesel'),
        ('Hybride', 'Hybride'),
        ('Électrique', 'Électrique'),
    ]
    
    CATEGORIE_CHOICES = [
        ('Voiture', 'Voiture'),
        ('Moto', 'Moto'),
        ('4x4', '4x4'),
        ('Camion', 'Camion'),
        ('Bus', 'Bus'),
    ]
    
    STATUT_CHOICES = [
        ('Actif', 'Actif'),
        ('Maintenance', 'Maintenance'),
        ('Hors Service', 'Hors Service'),
    ]
    
    id_vehicule = models.CharField(max_length=20, primary_key=True, verbose_name="ID Véhicule")
    immatriculation = models.CharField(max_length=20, verbose_name="Immatriculation")
    marque = models.CharField(max_length=50, verbose_name="Marque")
    modele = models.CharField(max_length=50, verbose_name="Modèle")
    type_moteur = models.CharField(max_length=20, choices=MOTEUR_CHOICES, verbose_name="Type de moteur")
    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, verbose_name="Catégorie")
    date_mise_service = models.DateField(null=True, blank=True, verbose_name="Date de mise en service")
    date_acquisition = models.DateField(null=True, blank=True, verbose_name="Date d'acquisition")
    kilometrage_initial = models.IntegerField(default=0, verbose_name="Kilométrage initial")
    affectation = models.CharField(max_length=100, blank=True, verbose_name="Affectation")
    statut_actuel = models.CharField(max_length=20, choices=STATUT_CHOICES, verbose_name="Statut actuel")
    numero_chassis = models.CharField(max_length=50, blank=True, verbose_name="Numéro de châssis")
    numero_moteur = models.CharField(max_length=50, blank=True, verbose_name="Numéro de moteur")
    observations = models.TextField(blank=True, verbose_name="Observations")
    chauffeur_principal = models.ForeignKey('Chauffeur', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicules_assignes', verbose_name="Chauffeur principal")
    fournisseur = models.ForeignKey('fleet_app.FournisseurVehicule', on_delete=models.SET_NULL, null=True, blank=True, related_name='vehicules', verbose_name="Fournisseur")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Entreprise")
    
    def __str__(self):
        return f"{self.marque} {self.modele} ({self.immatriculation})"
    
    class Meta:
        verbose_name = "Véhicule"
        verbose_name_plural = "Véhicules"


class DocumentAdministratif(models.Model):
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=50, verbose_name="Type de document")
    numero = models.CharField(max_length=50, verbose_name="Numéro")
    date_emission = models.DateField(verbose_name="Date d'émission")
    date_expiration = models.DateField(verbose_name="Date d'expiration")
    fichier = models.FileField(upload_to='documents/', null=True, blank=True, verbose_name="Fichier")
    commentaires = models.TextField(blank=True, verbose_name="Commentaires")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    
    def __str__(self):
        return f"{self.type_document} - {self.vehicule}"
    
    def est_expire(self):
        return self.date_expiration < timezone.now().date()
    
    def jours_avant_expiration(self):
        delta = self.date_expiration - timezone.now().date()
        return delta.days
    
    class Meta:
        verbose_name = "Document administratif"
        verbose_name_plural = "Documents administratifs"


class DistanceParcourue(models.Model):
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='distances')
    date_debut = models.DateField(verbose_name="Date de début")
    km_debut = models.IntegerField(verbose_name="Kilométrage de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    km_fin = models.IntegerField(verbose_name="Kilométrage de fin")
    distance_parcourue = models.IntegerField(verbose_name="Distance parcourue")
    type_moteur = models.CharField(max_length=20, verbose_name="Type de moteur")
    limite_annuelle = models.IntegerField(null=True, blank=True, verbose_name="Limite annuelle")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    
    def __str__(self):
        return f"{self.vehicule} - {self.date_debut} à {self.date_fin}"
    
    class Meta:
        verbose_name = "Distance parcourue"
        verbose_name_plural = "Distances parcourues"


class ConsommationCarburant(models.Model):
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='consommations')
    date_plein1 = models.DateField(verbose_name="Date du premier plein")
    km_plein1 = models.IntegerField(verbose_name="Kilométrage au premier plein")
    date_plein2 = models.DateField(verbose_name="Date du second plein")
    km_plein2 = models.IntegerField(verbose_name="Kilométrage au second plein")
    litres_ajoutes = models.FloatField(verbose_name="Litres ajoutés")
    distance_parcourue = models.IntegerField(verbose_name="Distance parcourue")
    consommation_100km = models.FloatField(verbose_name="Consommation aux 100km")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    consommation_constructeur = models.FloatField(null=True, blank=True, verbose_name="Consommation constructeur")
    ecart_constructeur = models.FloatField(null=True, blank=True, verbose_name="Écart avec constructeur")
    
    def __str__(self):
        return f"{self.vehicule} - {self.date_plein1} à {self.date_plein2}"
    
    class Meta:
        verbose_name = "Consommation de carburant"
        verbose_name_plural = "Consommations de carburant"


class DisponibiliteVehicule(models.Model):
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='disponibilites')
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    heures_disponibles = models.IntegerField(verbose_name="Heures disponibles")
    heures_totales = models.IntegerField(verbose_name="Heures totales")
    disponibilite_pourcentage = models.FloatField(verbose_name="Pourcentage de disponibilité")
    raison_indisponibilite = models.TextField(blank=True, verbose_name="Raison d'indisponibilité")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    
    # Champs conservés pour compatibilité avec l'existant
    periode = models.CharField(max_length=50, verbose_name="Période", blank=True)
    jours_total_periode = models.IntegerField(verbose_name="Jours totaux de la période", default=0)
    jours_hors_service = models.IntegerField(verbose_name="Jours hors service", default=0)
    
    def __str__(self):
        return f"{self.vehicule} - {self.date_debut} à {self.date_fin} - {self.disponibilite_pourcentage}%"
    
    class Meta:
        verbose_name = "Disponibilité de véhicule"
        verbose_name_plural = "Disponibilités de véhicules"


class UtilisationActif(models.Model):
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey('Vehicule', on_delete=models.CASCADE, related_name='utilisations')
    date_debut = models.DateField(verbose_name="Date de début", null=True)
    date_fin = models.DateField(verbose_name="Date de fin", null=True)
    conducteur = models.ForeignKey('Chauffeur', on_delete=models.SET_NULL, null=True, related_name='utilisations_actifs', verbose_name="Conducteur")
    departement = models.CharField(max_length=100, verbose_name="Département", null=True)
    motif_utilisation = models.TextField(verbose_name="Motif d'utilisation", null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    
    # Champs existants dans la base de données
    periode = models.CharField(max_length=100, null=True)
    jours_utilises = models.IntegerField(null=True)
    jours_disponibles = models.IntegerField(null=True)
    
    def __str__(self):
        return f"{self.vehicule} - {self.date_debut} à {self.date_fin} - {self.conducteur}"
    
    class Meta:
        verbose_name = "Utilisation d'actif"
        verbose_name_plural = "Utilisations d'actifs"


class IncidentSecurite(models.Model):
    TYPE_CHOICES = [
        ('Accident', 'Accident'),
        ('Incident', 'Incident'),
        ('Défaut critique', 'Défaut critique'),
    ]
    
    GRAVITE_CHOICES = [
        ('Faible', 'Faible'),
        ('Moyenne', 'Moyenne'),
        ('Élevée', 'Élevée'),
    ]
    
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='incidents')
    date_incident = models.DateField(verbose_name="Date de l'incident")
    conducteur = models.ForeignKey('Chauffeur', on_delete=models.SET_NULL, null=True, blank=True, related_name='incidents', verbose_name="Conducteur")
    type_incident = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type d'incident")
    gravite = models.CharField(max_length=50, choices=GRAVITE_CHOICES, verbose_name="Gravité")
    lieu = models.CharField(max_length=200, verbose_name="Lieu de l'incident", blank=True, null=True)
    description = models.TextField(verbose_name="Description de l'incident", blank=True, null=True)
    mesures_prises = models.TextField(verbose_name="Mesures prises", blank=True, null=True)
    commentaires = models.TextField(blank=True, null=True, verbose_name="Commentaires")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    
    def __str__(self):
        return f"{self.vehicule} - {self.type_incident} - {self.date_incident}"
    
    class Meta:
        verbose_name = "Incident de sécurité"
        verbose_name_plural = "Incidents de sécurité"
        db_table = 'IncidentsSecurite'


class CoutFonctionnement(models.Model):
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='couts_fonctionnement')
    date = models.DateField(verbose_name="Date")
    type_cout = models.CharField(max_length=50, verbose_name="Type de coût")
    montant = models.FloatField(verbose_name="Montant")
    km_actuel = models.IntegerField(verbose_name="Kilométrage actuel", default=0)
    cout_par_km = models.FloatField(verbose_name="Coût par km")
    description = models.TextField(blank=True, verbose_name="Description")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    
    def __str__(self):
        return f"{self.vehicule} - {self.type_cout} - {self.date}"
    
    class Meta:
        verbose_name = "Coût de fonctionnement"
        verbose_name_plural = "Coûts de fonctionnement"


class CoutFinancier(models.Model):
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='couts_financiers')
    date = models.DateField(verbose_name="Date")
    type_cout = models.CharField(max_length=50, verbose_name="Type de coût")
    montant = models.FloatField(verbose_name="Montant")
    kilometrage = models.IntegerField(verbose_name="Kilométrage")
    cout_par_km = models.FloatField(verbose_name="Coût par km")
    periode_amortissement = models.IntegerField(verbose_name="Période d'amortissement")
    description = models.TextField(blank=True, verbose_name="Description")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    
    def __str__(self):
        return f"{self.vehicule} - {self.type_cout} - {self.date}"
    
    class Meta:
        verbose_name = "Coût financier"
        verbose_name_plural = "Coûts financiers"


class UtilisationVehicule(models.Model):
    DEPARTEMENT_CHOICES = [
        ('Commercial', 'Commercial'),
        ('Technique', 'Technique'),
        ('Administratif', 'Administratif'),
        ('Direction', 'Direction'),
        ('Logistique', 'Logistique'),
        ('Maintenance', 'Maintenance'),
        ('Autre', 'Autre'),
    ]
    
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='utilisations_vehicule', verbose_name="Véhicule")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(verbose_name="Date de fin")
    conducteur = models.ForeignKey('Chauffeur', on_delete=models.SET_NULL, null=True, related_name='utilisations', verbose_name="Conducteur")
    departement = models.CharField(max_length=50, choices=DEPARTEMENT_CHOICES, verbose_name="Département")
    motif = models.CharField(max_length=200, verbose_name="Motif d'utilisation")
    km_depart = models.IntegerField(verbose_name="Kilométrage au départ")
    km_retour = models.IntegerField(verbose_name="Kilométrage au retour")
    observations = models.TextField(blank=True, verbose_name="Observations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    
    def __str__(self):
        return f"{self.vehicule} - {self.conducteur} - {self.date_debut}"
    
    class Meta:
        verbose_name = "Utilisation de véhicule"
        verbose_name_plural = "Utilisations de véhicules"
        db_table = 'UtilisationsVehicules'


# Le modèle Alerte a été déplacé vers models_alertes.py pour éviter les conflits
# from .models_alertes import Alerte


class Chauffeur(models.Model):
    id_chauffeur = models.AutoField(primary_key=True)
    nom = models.CharField(max_length=100, verbose_name="Nom")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    numero_permis = models.CharField(max_length=50, verbose_name="Numéro de permis")
    date_embauche = models.DateField(verbose_name="Date d'embauche")
    date_expiration_permis = models.DateField(null=True, blank=True, verbose_name="Date d'expiration du permis")
    telephone = models.CharField(max_length=20, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    statut = models.CharField(max_length=20, default='Actif', verbose_name="Statut")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Utilisateur")
    
    def __str__(self):
        return f"{self.nom} {self.prenom}"
    
    class Meta:
        verbose_name = "Chauffeur"
        verbose_name_plural = "Chauffeurs"
        db_table = 'Chauffeurs'


class FeuilleDeRoute(models.Model):
    OBJET_CHOICES = [
        ('Livraison', 'Livraison'),
        ('Mission', 'Mission'),
        ('Personnel', 'Personnel'),
    ]
    
    id = models.AutoField(primary_key=True)
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name='feuilles_route', verbose_name="Véhicule")
    chauffeur = models.ForeignKey(Chauffeur, on_delete=models.CASCADE, related_name='feuilles_route', verbose_name="Chauffeur")
    date_depart = models.DateField(verbose_name="Date de départ")
    heure_depart = models.TimeField(verbose_name="Heure de départ")
    destination = models.CharField(max_length=200, verbose_name="Destination")
    objet_deplacement = models.CharField(max_length=20, choices=OBJET_CHOICES, verbose_name="Objet du déplacement")
    signature_gestionnaire = models.BooleanField(default=False, verbose_name="Signé par le gestionnaire")
    
    # Informations à remplir par le chauffeur
    km_depart = models.IntegerField(null=True, blank=True, verbose_name="Kilométrage au départ")
    carburant_depart = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Carburant au départ (L)")
    km_retour = models.IntegerField(null=True, blank=True, verbose_name="Kilométrage au retour")
    carburant_retour = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Carburant au retour (L)")
    date_retour = models.DateField(null=True, blank=True, verbose_name="Date de retour")
    heure_retour = models.TimeField(null=True, blank=True, verbose_name="Heure de retour")
    signature_chauffeur = models.BooleanField(default=False, verbose_name="Signé par le chauffeur")
    
    # Champs calculés
    distance_parcourue = models.IntegerField(null=True, blank=True, verbose_name="Distance parcourue (km)")
    carburant_utilise = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Carburant utilisé (L)")
    consommation = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Consommation (L/100km)")
    alerte_surconsommation = models.BooleanField(default=False, verbose_name="Alerte de surconsommation")
    
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_modification = models.DateTimeField(auto_now=True, verbose_name="Dernière modification")
    
    def save(self, *args, **kwargs):
        # Calculer les champs automatiques si les données sont disponibles
        if self.km_depart is not None and self.km_retour is not None:
            self.distance_parcourue = self.km_retour - self.km_depart
            
        if self.carburant_depart is not None and self.carburant_retour is not None:
            self.carburant_utilise = self.carburant_depart - self.carburant_retour
            
        if self.distance_parcourue and self.distance_parcourue > 0 and self.carburant_utilise:
            self.consommation = (self.carburant_utilise * 100) / self.distance_parcourue
            
            # Vérifier si la consommation dépasse la moyenne + 3
            # Valeur moyenne de consommation (à ajuster selon les besoins)
            conso_moyenne = 8  # L/100km (à remplacer par la valeur du constructeur si disponible)
            if self.consommation > (conso_moyenne + 3):
                self.alerte_surconsommation = True
            else:
                self.alerte_surconsommation = False
                
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Feuille de route {self.id} - {self.vehicule} - {self.date_depart}"
    
    class Meta:
        verbose_name = "Feuille de route"
        verbose_name_plural = "Feuilles de route"
        db_table = 'FeuillesDeRoute'


class ArchiveMensuelle(models.Model):
    """
    Modèle pour archiver les données mensuelles avant réinitialisation
    """
    STATUT_CHOICES = [
        ('En cours', 'En cours'),
        ('Clôturé', 'Clôturé'),
        ('Archivé', 'Archivé'),
    ]
    
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, verbose_name="Utilisateur")
    mois = models.IntegerField(verbose_name="Mois (1-12)")
    annee = models.IntegerField(verbose_name="Année")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='En cours', verbose_name="Statut")
    
    # Statistiques générales
    nb_employes_actifs = models.IntegerField(default=0, verbose_name="Nombre d'employés actifs")
    nb_jours_travailles = models.IntegerField(default=0, verbose_name="Nombre de jours travaillés")
    
    # Données de présence archivées (JSON)
    donnees_presences = models.JSONField(default=dict, verbose_name="Données de présences archivées")
    
    # Données de paies archivées (JSON)
    donnees_paies = models.JSONField(default=dict, verbose_name="Données de paies archivées")
    
    # Données d'heures supplémentaires archivées (JSON)
    donnees_heures_supp = models.JSONField(default=dict, verbose_name="Données d'heures supplémentaires archivées")
    
    # Totaux financiers
    total_salaire_brut = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total salaire brut")
    total_deductions = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total déductions")
    total_net_paye = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total net payé")
    
    # Métadonnées
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_cloture = models.DateTimeField(null=True, blank=True, verbose_name="Date de clôture")
    commentaires = models.TextField(blank=True, verbose_name="Commentaires")
    
    def __str__(self):
        return f"Archive {self.mois:02d}/{self.annee} - {self.user.username} ({self.statut})"
    
    def get_periode_label(self):
        import calendar
        return f"{calendar.month_name[self.mois]} {self.annee}"
    
    def peut_etre_cloturee(self):
        return self.statut == 'En cours'
    
    def peut_etre_restauree(self):
        return self.statut in ['Clôturé', 'Archivé']
    
    class Meta:
        verbose_name = "Archive mensuelle"
        verbose_name_plural = "Archives mensuelles"
        unique_together = ['user', 'mois', 'annee']
        ordering = ['-annee', '-mois']


class GalleryImage(models.Model):
    """
    Images de galerie simples uploadées via l'admin et affichées sur une page publique.
    Les fichiers sont stockés sous MEDIA_ROOT/gallery/.
    """
    title = models.CharField(max_length=200, blank=True, verbose_name="Titre")
    image = models.ImageField(upload_to='gallery/', verbose_name="Image")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")

    def __str__(self):
        return self.title or f"Image #{self.pk}"

    class Meta:
        verbose_name = "Image de la galerie"
        verbose_name_plural = "Images de la galerie"
