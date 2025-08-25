from django.contrib import admin
from .models import *
from .models_alertes import Alerte
from .models_accounts import Profil, Entreprise, PersonnePhysique

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
