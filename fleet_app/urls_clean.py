from django.urls import path
from . import views
from . import views_entreprise
from . import views_inventaire
from . import views_facturation
from . import views_debug
from . import views_force_delete
from . import views_integrity
from . import views_alertes
from . import views_management
from . import views_management_new
from . import views_management_complete
from . import views_minerai
from . import views_accounts
from . import views_entreprise_info
from . import views_synchronization
from . import views_pointage

app_name = 'fleet_app'

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),
    # Tableau de bord
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Création de compte après première connexion
    path('creation-compte/', views_accounts.creation_compte, name='creation_compte'),
    path('reinitialiser-creation-compte/', views_accounts.reinitialiser_creation_compte, name='reinitialiser_creation_compte'),
    path('creation-compte/retour/<int:etape>/', views_accounts.retour_etape, name='retour_etape'),
    
    # Véhicules
    path('vehicules/', views.VehiculeListView.as_view(), name='vehicule_list'),
    path('vehicules/ajouter/', views.VehiculeCreateView.as_view(), name='vehicule_add'),
    path('vehicules/<str:id_vehicule>/', views.VehiculeDetailView.as_view(), name='vehicule_detail'),
    path('vehicules/modifier/<str:id_vehicule>/', views.VehiculeUpdateView.as_view(), name='vehicule_edit'),
    path('vehicules/supprimer/<str:id_vehicule>/', views.VehiculeDeleteView.as_view(), name='vehicule_delete'),
    path('vehicules/force-delete/<str:id_vehicule>/', views_force_delete.force_delete_vehicule, name='force_delete_vehicule'),
    
    # KPI
    path('kpi/distance/', views.kpi_distance, name='kpi_distance'),
    path('kpi/consommation/', views.kpi_consommation, name='kpi_consommation'),
    path('kpi/disponibilite/', views.kpi_disponibilite, name='kpi_disponibilite'),
    path('kpi/couts-fonctionnement/', views.kpi_couts_fonctionnement, name='kpi_couts_fonctionnement'),
    path('kpi/couts-financiers/', views.kpi_couts_financiers, name='kpi_couts_financiers'),
    path('kpi/incidents/', views.kpi_incidents, name='kpi_incidents'),
    path('kpi/utilisation/', views.kpi_utilisation, name='kpi_utilisation'),
    
    # Gestion des utilisations
    path('utilisations/modifier/<int:pk>/', views.utilisation_edit, name='utilisation_edit'),
    path('utilisations/supprimer/<int:pk>/', views.utilisation_delete, name='utilisation_delete'),
    
    # Gestion des incidents
    path('incidents/modifier/<int:pk>/', views.incident_edit, name='incident_edit'),
    path('incidents/supprimer/<int:pk>/', views.incident_delete, name='incident_delete'),
    
    # Gestion des distances parcourues
    path('distances/modifier/<int:pk>/', views.distance_edit, name='distance_edit'),
    path('distances/supprimer/<int:pk>/', views.distance_delete, name='distance_delete'),
    
    # Gestion des consommations de carburant
    path('consommations/modifier/<int:pk>/', views.consommation_edit, name='consommation_edit'),
    path('consommations/supprimer/<int:pk>/', views.consommation_delete, name='consommation_delete'),
    
    # Gestion des disponibilités
    path('disponibilites/modifier/<int:pk>/', views.disponibilite_edit, name='disponibilite_edit'),
    path('disponibilites/supprimer/<int:pk>/', views.disponibilite_delete, name='disponibilite_delete'),
    
    # Gestion des coûts de fonctionnement
    path('couts-fonctionnement/modifier/<int:pk>/', views.cout_fonctionnement_edit, name='cout_fonctionnement_edit'),
    path('couts-fonctionnement/supprimer/<int:pk>/', views.cout_fonctionnement_delete, name='cout_fonctionnement_delete'),
    
    # Gestion des coûts financiers
    path('couts-financiers/modifier/<int:pk>/', views.cout_financier_edit, name='cout_financier_edit'),
    path('couts-financiers/supprimer/<int:pk>/', views.cout_financier_delete, name='cout_financier_delete'),
    
    # Chauffeurs
    path('chauffeurs/', views.ChauffeurListView.as_view(), name='chauffeur_list'),
    path('chauffeurs/ajouter/', views.ChauffeurCreateView.as_view(), name='chauffeur_add'),
    path('chauffeurs/<int:id_chauffeur>/', views.ChauffeurDetailView.as_view(), name='chauffeur_detail'),
    path('chauffeurs/modifier/<int:id_chauffeur>/', views.ChauffeurUpdateView.as_view(), name='chauffeur_edit'),
    path('chauffeurs/supprimer/<int:id_chauffeur>/', views.ChauffeurDeleteView.as_view(), name='chauffeur_delete'),
    
    # Feuilles de route
    path('feuilles-route/', views.FeuilleRouteListView.as_view(), name='feuille_route_list'),
    path('feuilles-route/ajouter/', views.feuille_route_add, name='feuille_route_add'),
    path('feuilles-route/<int:pk>/', views.FeuilleRouteDetailView.as_view(), name='feuille_route_detail'),
    path('feuilles-route/modifier/<int:pk>/', views.feuille_route_edit, name='feuille_route_edit'),
    path('feuilles-route/supprimer/<int:pk>/', views.feuille_route_delete, name='feuille_route_delete'),
    
    # Alertes
    path('alertes/', views_alertes.alerte_list, name='alerte_list'),
    path('alertes/nouvelle/', views_alertes.alerte_nouvelle, name='alerte_nouvelle'),
    path('alertes/<int:pk>/resoudre/', views_alertes.alerte_resoudre, name='alerte_resoudre'),
    path('alertes/<int:pk>/ignorer/', views_alertes.alerte_ignorer, name='alerte_ignorer'),
    path('alertes/<int:pk>/supprimer/', views_alertes.alerte_supprimer, name='alerte_supprimer'),
    path('api/alertes/kpi/', views_alertes.get_alertes_kpi, name='api_alertes_kpi'),
    
    # URLs pour les employés
    path('employes/', views_management_new.employe_list, name='employe_list'),
    path('employes/<int:pk>/', views_management_new.employe_detail, name='employe_detail'),
    path('employes/nouveau/', views_management_complete.employe_create, name='employe_create'),
    path('employes/<int:pk>/modifier/', views_management_complete.employe_edit, name='employe_edit'),
    path('employes/<int:pk>/supprimer/', views_management_complete.employe_delete, name='employe_delete'),
    
    # URLs pour la configuration des montants individuels par employé
    path('configuration-montants-employes/', views_entreprise.configuration_montant_employe_list, name='configuration_montant_employe_list'),
    path('configuration-montants-employes/formulaire/', views_entreprise.configuration_montant_employe_form, name='configuration_montant_employe_form'),
    path('configuration-montants-employes/formulaire/<int:employe_id>/', views_entreprise.configuration_montant_employe_form, name='configuration_montant_employe_form'),
    path('configuration-montants-employes/ajax/', views_entreprise.configuration_montant_employe_ajax, name='configuration_montant_employe_ajax'),
    
    # URLs pour les paies des employés
    path('paies/', views_management_complete.paie_employe_list, name='paie_employe_list'),
    path('paies/nouveau/<int:employe_id>/', views_management_complete.paie_employe_create, name='paie_employe_create'),
    path('paies/export/', views_management_complete.paie_employe_export, name='paie_employe_export'),
    path('paies/<int:pk>/edit/', views_management_complete.paie_employe_edit, name='paie_employe_edit'),
    path('paies/<int:pk>/delete/', views_management_complete.paie_employe_delete, name='paie_employe_delete'),
    
    # URLs pour les heures supplémentaires
    path('management/heures-supplementaires/', views_management_complete.heure_supplementaire_list, name='heure_supplementaire_list'),
    path('management/heures-supplementaires/export/', views_entreprise.heure_supplementaire_export, name='heure_supplementaire_export'),
    
    # URLs pour les paramètres de paie
    path('parametres-paie/', views_management_complete.parametre_paie_list, name='parametre_paie_list'),
    path('parametres-paie/export/', views_management_complete.parametre_paie_export, name='parametre_paie_export'),
    
    # Debug
    path('debug/vehicule/<str:id_vehicule>/', views_debug.debug_vehicle_relations, name='debug_vehicle_relations'),
    
    # Diagnostic d'intégrité
    path('integrity/check/<str:model_name>/<str:object_id>/', views_integrity.check_model_relations, name='check_model_relations'),
    path('integrity/dependencies/', views_integrity.list_model_dependencies, name='list_model_dependencies'),
    
    # URLs pour le sous-menu Management
    path('management/employes/', views_management_new.employe_list, name='management_employe_list'),
    path('management/employes/<int:pk>/', views_management_new.employe_detail, name='management_employe_detail'),
    path('management/employes/ajouter/', views_management.temp_redirect_view, name='management_employe_add'),
    path('management/employes/<int:pk>/modifier/', views_management.temp_redirect_view, name='management_employe_edit'),
    path('management/employes/<int:pk>/supprimer/', views_management.temp_redirect_view, name='management_employe_delete'),
    path('management/configuration-montant-statut/', views_entreprise.configuration_montant_statut, name='configuration_montant_statut'),
    path('management/paies/', views_management.temp_redirect_view, name='management_paie_list'),
    path('management/heures-supplementaires/', views_management.heure_supplementaire_list, name='management_heure_supplementaire_list'),
    path('management/parametres-paie/', views_management.parametre_paie_list, name='management_parametre_paie_list'),
    
    # Configuration des montants pour les présences (AJAX)
    path('configuration_montant_statut/', views_entreprise.configuration_montant_statut, name='configuration_montant_statut'),
    
    # Gestion des informations de l'entreprise
    path('entreprise/informations/', views_entreprise_info.entreprise_info_view, name='entreprise_info'),
    path('api/entreprise/informations/', views_entreprise_info.entreprise_info_api, name='entreprise_info_api'),
    
    # URLs pour la synchronisation des données
    path('synchronization/', views_synchronization.synchronization_dashboard, name='synchronization_dashboard'),
    path('synchronization/ajax/sync/', views_synchronization.synchroniser_donnees_ajax, name='synchroniser_donnees_ajax'),
    path('synchronization/ajax/coherence/', views_synchronization.verifier_coherence_ajax, name='verifier_coherence_ajax'),
    path('synchronization/corriger/', views_synchronization.corriger_incoherences, name='corriger_incoherences'),
    path('synchronization/export/', views_synchronization.export_rapport_coherence, name='export_rapport_coherence'),
    path('synchronization/status/', views_synchronization.status_synchronization_api, name='status_synchronization_api'),
    path('synchronization/relations/', views_synchronization.relations_modules_info, name='relations_modules_info'),
    
    # URLs pour le système de pointage journalier dynamique
    path('pointage/', views_pointage.pointage_journalier, name='pointage_journalier'),
    path('pointage/pointer/', views_pointage.pointer_employe_ajax, name='pointer_employe_ajax'),
    path('pointage/supprimer/', views_pointage.supprimer_pointage_ajax, name='supprimer_pointage_ajax'),
    path('pointage/navigation/', views_pointage.navigation_mois, name='navigation_mois'),
    path('pointage/statistiques/', views_pointage.statistiques_pointage, name='statistiques_pointage'),
    path('pointage/formulaire/', views_pointage.pointage_formulaire, name='pointage_formulaire'),
    path('pointage/rapide/', views_pointage.pointage_rapide, name='pointage_rapide'),
]
