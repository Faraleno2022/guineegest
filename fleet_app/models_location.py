from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from .models_accounts import Entreprise

from .models import Vehicule


class FournisseurVehicule(models.Model):
    nom = models.CharField(max_length=150, verbose_name="Nom du fournisseur")
    contact = models.CharField(max_length=150, blank=True, null=True, verbose_name="Contact")
    telephone = models.CharField(max_length=30, blank=True, null=True, verbose_name="Téléphone")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    adresse = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Entreprise")

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Fournisseur de véhicule"
        verbose_name_plural = "Fournisseurs de véhicules"


class LocationVehicule(models.Model):
    TYPE_CHOICES = [
        ("Interne", "Interne"),
        ("Externe", "Externe"),
    ]
    STATUT_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
        ("Clôturée", "Clôturée"),
    ]

    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, related_name="locations", verbose_name="Véhicule")
    type_location = models.CharField(max_length=10, choices=TYPE_CHOICES, verbose_name="Type de location")
    fournisseur = models.ForeignKey(FournisseurVehicule, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Fournisseur")
    date_debut = models.DateField(verbose_name="Date de début")
    date_fin = models.DateField(blank=True, null=True, verbose_name="Date de fin")
    tarif_journalier = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tarif journalier")
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default="Active", verbose_name="Statut")
    motif = models.CharField(max_length=255, blank=True, null=True, verbose_name="Motif/Objet")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Entreprise")

    def __str__(self):
        return f"{self.vehicule} - {self.type_location} ({self.statut})"

    @property
    def jours_actifs(self):
        # Nombre de jours de pontage 'Travail'
        return self.feuilles.filter(statut="Travail").count()

    @property
    def jours_entretien(self):
        return self.feuilles.filter(statut="Entretien").count()

    @property
    def jours_hors_service(self):
        return self.feuilles.filter(statut="Hors service").count()

    class Meta:
        verbose_name = "Location de véhicule"
        verbose_name_plural = "Locations de véhicules"


class FeuillePontageLocation(models.Model):
    STATUT_CHOICES = [
        ("Travail", "Travail"),
        ("Entretien", "Entretien"),
        ("Hors service", "Hors service"),
        ("Inactif", "Inactif"),
    ]

    location = models.ForeignKey(LocationVehicule, on_delete=models.CASCADE, related_name="feuilles", verbose_name="Location")
    date = models.DateField(default=timezone.now, verbose_name="Date")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="Travail", verbose_name="Statut du jour")
    commentaire = models.CharField(max_length=255, blank=True, null=True, verbose_name="Commentaire")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Entreprise")

    def __str__(self):
        return f"{self.location} - {self.date} ({self.statut})"

    class Meta:
        verbose_name = "Feuille de pontage"
        verbose_name_plural = "Feuilles de pontage"
        unique_together = ("location", "date")


class FactureLocation(models.Model):
    STATUT_CHOICES = [
        ("Brouillon", "Brouillon"),
        ("Payée", "Payée"),
        ("Annulée", "Annulée"),
    ]

    location = models.ForeignKey(LocationVehicule, on_delete=models.CASCADE, related_name="factures", verbose_name="Location")
    numero = models.CharField(max_length=50, verbose_name="Numéro de facture")
    date = models.DateField(default=timezone.now, verbose_name="Date de facture")
    montant_ht = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant HT")
    tva = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="TVA")
    montant_ttc = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Montant TTC")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="Brouillon", verbose_name="Statut")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Utilisateur")
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Entreprise")
    # Stockage des jours du mois pour traçabilité
    jours_travail_mois = models.IntegerField(default=0, verbose_name="Jours de travail (mois)")
    jours_non_travail_mois = models.IntegerField(default=0, verbose_name="Jours non travaillés (mois)")

    def __str__(self):
        return f"Facture {self.numero} - {self.location}"

    class Meta:
        verbose_name = "Facture location"
        verbose_name_plural = "Factures location"
