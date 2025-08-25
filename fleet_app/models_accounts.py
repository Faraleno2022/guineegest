from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

# Choix pour les types de compte
TYPE_COMPTE_CHOICES = [
    ('personne', 'Personne Physique'),
    ('entreprise', 'Entreprise / Organisation'),
]

# Choix pour les formes juridiques
FORME_JURIDIQUE_CHOICES = [
    ('sarl', 'SARL'),
    ('sa', 'SA'),
    ('ong', 'ONG'),
    ('ei', 'Entreprise Individuelle'),
    ('autre', 'Autre'),
]

# Choix pour les rôles
ROLE_CHOICES = [
    ('admin', 'Administrateur'),
    ('standard', 'Utilisateur standard'),
    ('rh', 'Responsable RH'),
    ('stock', 'Gestionnaire stock'),
    ('comptable', 'Comptable'),
    ('autre', 'Autre'),
]

class Profil(models.Model):
    """Modèle de base pour tous les profils"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    type_compte = models.CharField(max_length=20, choices=TYPE_COMPTE_CHOICES, verbose_name=_("Type de compte"))
    telephone = models.CharField(max_length=20, verbose_name=_("Téléphone"))
    email = models.EmailField(verbose_name=_("E-mail"))
    adresse = models.TextField(blank=True, null=True, verbose_name=_("Adresse"))
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, verbose_name=_("Fonction ou Rôle"))
    conditions_acceptees = models.BooleanField(default=False, verbose_name=_("Conditions acceptées"))
    informations_certifiees = models.BooleanField(default=False, verbose_name=_("Informations certifiées"))
    compte_complete = models.BooleanField(default=False, verbose_name=_("Compte complété"))
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    date_modification = models.DateTimeField(auto_now=True, verbose_name=_("Dernière modification"))
    
    class Meta:
        verbose_name = _("Profil")
        verbose_name_plural = _("Profils")
    
    def __str__(self):
        return f"{self.user.username} - {self.get_type_compte_display()}"


class PersonnePhysique(models.Model):
    """Modèle pour les comptes de type Personne Physique"""
    profil = models.OneToOneField(Profil, on_delete=models.CASCADE, related_name='personne_physique')
    nom_prenom = models.CharField(max_length=100, verbose_name=_("Nom et Prénom(s)"))
    date_naissance = models.DateField(blank=True, null=True, verbose_name=_("Date de naissance"))
    photo = models.ImageField(upload_to='profils/personnes/', blank=True, null=True, verbose_name=_("Photo de profil"))
    
    class Meta:
        verbose_name = _("Personne Physique")
        verbose_name_plural = _("Personnes Physiques")
    
    def __str__(self):
        return self.nom_prenom


class Entreprise(models.Model):
    """Modèle pour les comptes de type Entreprise / Organisation"""
    profil = models.OneToOneField(Profil, on_delete=models.CASCADE, related_name='entreprise')
    nom_entreprise = models.CharField(max_length=200, verbose_name=_("Nom de l'entreprise"))
    forme_juridique = models.CharField(max_length=20, choices=FORME_JURIDIQUE_CHOICES, verbose_name=_("Forme juridique"))
    nom_responsable = models.CharField(max_length=100, verbose_name=_("Nom du responsable"))
    rccm_nif = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("RCCM / NIF"))
    logo = models.ImageField(upload_to='profils/entreprises/', blank=True, null=True, verbose_name=_("Logo de l'entreprise"))
    
    # Champs additionnels pour les bulletins de paie
    adresse = models.TextField(blank=True, verbose_name=_("Adresse complète"))
    telephone = models.CharField(max_length=50, blank=True, verbose_name=_("Téléphone"))
    email = models.EmailField(blank=True, verbose_name=_("Email"))
    site_web = models.URLField(blank=True, verbose_name=_("Site web"))
    
    # Informations légales séparées
    rccm = models.CharField(max_length=100, blank=True, verbose_name=_("RCCM (Registre de Commerce)"))
    nif = models.CharField(max_length=100, blank=True, verbose_name=_("NIF (Numéro d'Identification Fiscale)"))
    cnss = models.CharField(max_length=100, blank=True, verbose_name=_("Numéro CNSS"))
    
    # Informations bancaires
    banque = models.CharField(max_length=200, blank=True, verbose_name=_("Nom de la banque"))
    numero_compte = models.CharField(max_length=100, blank=True, verbose_name=_("Numéro de compte"))
    
    class Meta:
        verbose_name = _("Entreprise")
        verbose_name_plural = _("Entreprises")
    
    def __str__(self):
        return self.nom_entreprise
