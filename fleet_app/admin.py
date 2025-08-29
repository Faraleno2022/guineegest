from django.contrib import admin
from .models import *
from .models_alertes import Alerte
from .models_accounts import Profil, Entreprise, PersonnePhysique
from .models_entreprise import (
    Employe,
    PaieEmploye,
    PresenceJournaliere,
    SalaireMensuel,
    HeureSupplementaire,
    ConfigurationMontantStatut,
    ConfigurationMontantEmploye,
    ConfigurationSalaire,
    ConfigurationChargesSociales,
    ConfigurationHeureSupplementaire,
)

# Enregistrement des modèles dans l'administration Django

@admin.register(Vehicule)
class VehiculeAdmin(admin.ModelAdmin):
    list_display = ('id_vehicule', 'immatriculation', 'marque', 'modele', 'type_moteur', 'categorie', 'statut_actuel')
    list_filter = ('type_moteur', 'categorie', 'statut_actuel')
    search_fields = ('id_vehicule', 'immatriculation', 'marque', 'modele')

@admin.register(DocumentAdministratif)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'type_document', 'numero', 'date_emission', 'date_expiration')
    list_filter = ('type_document', 'date_expiration')
    search_fields = ('vehicule__immatriculation', 'type_document', 'numero')
    date_hierarchy = 'date_expiration'

@admin.register(DistanceParcourue)
class DistanceAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'date_debut', 'date_fin', 'km_debut', 'km_fin', 'distance_parcourue')
    list_filter = ('vehicule__type_moteur',)
    search_fields = ('vehicule__immatriculation',)
    date_hierarchy = 'date_fin'

@admin.register(ConsommationCarburant)
class ConsommationAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'date_plein1', 'date_plein2', 'litres_ajoutes', 'distance_parcourue', 'consommation_100km')
    list_filter = ('vehicule__type_moteur',)
    search_fields = ('vehicule__immatriculation',)
    date_hierarchy = 'date_plein2'

@admin.register(DisponibiliteVehicule)
class DisponibiliteAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'periode', 'jours_total_periode', 'jours_hors_service', 'disponibilite_pourcentage')
    list_filter = ('vehicule__categorie',)
    search_fields = ('vehicule__immatriculation', 'periode')

@admin.register(UtilisationActif)
class UtilisationAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'periode', 'jours_disponibles', 'jours_utilises')
    list_filter = ('vehicule__categorie',)
    search_fields = ('vehicule__immatriculation', 'periode')

@admin.register(IncidentSecurite)
class IncidentAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'date_incident', 'type_incident', 'gravite')
    list_filter = ('type_incident', 'gravite')
    search_fields = ('vehicule__immatriculation', 'commentaires')
    date_hierarchy = 'date_incident'

@admin.register(CoutFonctionnement)
class CoutFonctionnementAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'date', 'type_cout', 'montant', 'kilometrage', 'cout_par_km')
    list_filter = ('type_cout',)
    search_fields = ('vehicule__immatriculation', 'type_cout')
    date_hierarchy = 'date'

@admin.register(CoutFinancier)
class CoutFinancierAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'date', 'type_cout', 'montant', 'kilometrage', 'cout_par_km', 'periode_amortissement')
    list_filter = ('type_cout',)
    search_fields = ('vehicule__immatriculation', 'type_cout')
    date_hierarchy = 'date'

@admin.register(Alerte)
class AlerteAdmin(admin.ModelAdmin):
    list_display = ('vehicule', 'titre', 'date_creation', 'niveau', 'statut')
    list_filter = ('niveau', 'statut')
    search_fields = ('vehicule__immatriculation', 'titre', 'description')
    date_hierarchy = 'date_creation'

# Administration des comptes utilisateurs
@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_compte', 'telephone', 'email', 'role', 'compte_complete')
    list_filter = ('type_compte', 'role', 'compte_complete')
    search_fields = ('user__username', 'user__email', 'telephone', 'email')
    date_hierarchy = 'date_creation'

@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('nom_entreprise', 'forme_juridique', 'nom_responsable', 'telephone', 'email')
    list_filter = ('forme_juridique',)
    search_fields = ('nom_entreprise', 'nom_responsable', 'rccm', 'nif')
    fieldsets = (
        ('Informations générales', {
            'fields': ('profil', 'nom_entreprise', 'forme_juridique', 'nom_responsable', 'logo')
        }),
        ('Coordonnées', {
            'fields': ('adresse', 'telephone', 'email', 'site_web')
        }),
        ('Informations légales', {
            'fields': ('rccm', 'nif', 'cnss', 'rccm_nif')
        }),
        ('Informations bancaires', {
            'fields': ('banque', 'numero_compte'),
            'classes': ('collapse',)
        })
    )

@admin.register(PersonnePhysique)
class PersonnePhysiqueAdmin(admin.ModelAdmin):
    list_display = ('nom_prenom', 'date_naissance')
    search_fields = ('nom_prenom',)
    date_hierarchy = 'date_naissance'

# ==========================
# Administration Entreprise
# ==========================

class UserOwnedAdminMixin:
    """Restreint l'accès aux objets de l'utilisateur et renseigne le champ user à l'enregistrement."""
    user_field_name = 'user'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Si le modèle a un champ user, filtrer par request.user
        if hasattr(self.model, self.user_field_name):
            return qs.filter(**{self.user_field_name: request.user})
        return qs

    def save_model(self, request, obj, form, change):
        # Renseigner automatiquement le user s'il existe sur le modèle
        if hasattr(obj, self.user_field_name) and getattr(obj, self.user_field_name) is None:
            setattr(obj, self.user_field_name, request.user)
        super().save_model(request, obj, form, change)


@admin.register(Employe)
class EmployeAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = (
        'matricule', 'prenom', 'nom', 'fonction', 'salaire_base',
        'montant_heure_supp_jour_ouvrable', 'montant_heure_supp_dimanche_ferie',
    )
    list_filter = ('fonction',)
    search_fields = ('matricule', 'prenom', 'nom', 'fonction')


@admin.register(PaieEmploye)
class PaieEmployeAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = (
        'employe', 'mois', 'annee', 'salaire_brut', 'salaire_net_a_payer',
        'heures_supplementaires', 'montant_heures_supplementaires',
    )
    list_filter = ('annee', 'mois')
    search_fields = ('employe__matricule', 'employe__prenom', 'employe__nom')
    date_hierarchy = None


@admin.register(HeureSupplementaire)
class HeureSupplementaireAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = ('employe', 'date', 'type_jour', 'duree', 'taux_horaire', 'total_a_payer')
    list_filter = ('type_jour',)
    search_fields = ('employe__matricule', 'employe__prenom', 'employe__nom')
    date_hierarchy = 'date'


@admin.register(ConfigurationMontantStatut)
class ConfigurationMontantStatutAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = ('statut', 'montant')
    list_filter = ('statut',)
    search_fields = ('statut',)


@admin.register(ConfigurationMontantEmploye)
class ConfigurationMontantEmployeAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = ('employe', 'montant')
    search_fields = ('employe__matricule', 'employe__prenom', 'employe__nom')


@admin.register(ConfigurationSalaire)
class ConfigurationSalaireAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = ('employe', 'salaire_base')
    search_fields = ('employe__matricule', 'employe__prenom', 'employe__nom')


@admin.register(ConfigurationChargesSociales)
class ConfigurationChargesSocialesAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = ('nom', 'taux', 'actif')
    list_filter = ('actif',)
    search_fields = ('nom',)


@admin.register(ConfigurationHeureSupplementaire)
class ConfigurationHeureSupplementaireAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    fieldsets = (
        ('Base', {'fields': ('salaire_mensuel_base', 'heures_normales_mois')}),
        ('Jour ouvrable', {'fields': ('taux_jour_ouvrable', 'montant_jour_ouvrable')}),
        ('Dimanche / Férié', {'fields': ('taux_dimanche_ferie', 'montant_dimanche_ferie')}),
    )
    list_display = (
        'salaire_mensuel_base', 'heures_normales_mois',
        'taux_jour_ouvrable', 'montant_jour_ouvrable',
        'taux_dimanche_ferie', 'montant_dimanche_ferie',
    )


@admin.register(PresenceJournaliere)
class PresenceJournaliereAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = ('employe', 'date', 'present', 'statut')
    list_filter = ('present', 'statut')
    search_fields = ('employe__matricule', 'employe__prenom', 'employe__nom')
    date_hierarchy = 'date'


@admin.register(SalaireMensuel)
class SalaireMensuelAdmin(UserOwnedAdminMixin, admin.ModelAdmin):
    list_display = ('employe', 'mois', 'annee', 'net_a_payer', 'brut')
    list_filter = ('annee', 'mois')
    search_fields = ('employe__matricule', 'employe__prenom', 'employe__nom')
