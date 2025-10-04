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
from . import views_presence_sync
from . import views_paie_enhanced
from . import views_location
from . import views_vehicule_stats
from . import views_vehicule_simple
from . import views_fournisseur_simple

app_name = 'fleet_app'

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),
    # Galerie publique
    path('galerie/', views.gallery, name='gallery'),
    # Tableau de bord
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Création de compte après première connexion
    path('creation-compte/', views_accounts.creation_compte, name='creation_compte'),
    path('reinitialiser-creation-compte/', views_accounts.reinitialiser_creation_compte, name='reinitialiser_creation_compte'),
    path('creation-compte/retour/<int:etape>/', views_accounts.retour_etape, name='retour_etape'),
    
    # Véhicules
    path('vehicules/', views.VehiculeListView.as_view(), name='vehicule_list'),
    path('vehicules/export/pdf/', views.export_vehicules_pdf, name='export_vehicules_pdf'),
    path('vehicules/ajouter/', views.VehiculeCreateView.as_view(), name='vehicule_add'),
    path('vehicules/nouveau-simple/', views_vehicule_simple.vehicule_create_simple, name='vehicule_create_simple'),
    path('vehicules/<str:id_vehicule>/', views.VehiculeDetailView.as_view(), name='vehicule_detail'),
    path('vehicules/modifier/<str:id_vehicule>/', views.VehiculeUpdateView.as_view(), name='vehicule_edit'),
    path('vehicules/supprimer/<str:id_vehicule>/', views.VehiculeDeleteView.as_view(), name='vehicule_delete'),
    path('vehicules/force-delete/<str:id_vehicule>/', views_force_delete.force_delete_vehicule, name='force_delete_vehicule'),
    # Exports CSV spécifiques à un véhicule
    path('vehicules/<str:id_vehicule>/export/documents/', views.export_vehicule_documents_csv, name='export_vehicule_documents_csv'),
    path('vehicules/<str:id_vehicule>/export/distances/', views.export_vehicule_distances_csv, name='export_vehicule_distances_csv'),
    path('vehicules/<str:id_vehicule>/export/consommations/', views.export_vehicule_consommations_csv, name='export_vehicule_consommations_csv'),
    path('vehicules/<str:id_vehicule>/export/couts/', views.export_vehicule_couts_csv, name='export_vehicule_couts_csv'),
    path('vehicules/<str:id_vehicule>/export/alertes/', views.export_vehicule_alertes_csv, name='export_vehicule_alertes_csv'),
    
    # API pour récupérer le dernier kilométrage d'un véhicule
    path('api/vehicule/<str:id_vehicule>/last-km/', views.get_vehicule_last_km, name='get_vehicule_last_km'),
    
    # KPI
    path('kpi/distance/', views.kpi_distance, name='kpi_distance'),
    path('kpi/distance/export-csv/', views.export_kpi_distance_csv, name='export_kpi_distance_csv'),
    path('kpi/distance/export-pdf/', views.export_kpi_distance_pdf, name='export_kpi_distance_pdf'),
    path('kpi/consommation/', views.kpi_consommation, name='kpi_consommation'),
    path('kpi/consommation/export-csv/', views.export_kpi_consommation_csv, name='export_kpi_consommation_csv'),
    path('kpi/consommation/export-pdf/', views.export_kpi_consommation_pdf, name='export_kpi_consommation_pdf'),
    path('kpi/disponibilite/', views.kpi_disponibilite, name='kpi_disponibilite'),
    path('kpi/disponibilite/export-csv/', views.export_kpi_disponibilite_csv, name='export_kpi_disponibilite_csv'),
    path('kpi/disponibilite/export-pdf/', views.export_kpi_disponibilite_pdf, name='export_kpi_disponibilite_pdf'),
    path('kpi/couts-fonctionnement/', views.kpi_couts_fonctionnement, name='kpi_couts_fonctionnement'),
    path('kpi/couts-fonctionnement/export-pdf/', views.export_kpi_couts_fonctionnement_pdf, name='export_kpi_couts_fonctionnement_pdf'),
    path('feuilles-route/export/pdf/', views.export_feuilles_route_pdf, name='export_feuilles_route_pdf'),
    path('kpi/couts-financiers/', views.kpi_couts_financiers, name='kpi_couts_financiers'),
    path('kpi/couts-financiers/export-pdf/', views.export_kpi_couts_financiers_pdf, name='export_kpi_couts_financiers_pdf'),
    path('kpi/incidents/export-pdf/', views.export_kpi_incidents_pdf, name='export_kpi_incidents_pdf'),
    path('kpi/incidents/', views.kpi_incidents, name='kpi_incidents'),
    path('kpi/utilisation/', views.kpi_utilisation, name='kpi_utilisation'),
    path('kpi/utilisation/export-pdf/', views.export_kpi_utilisation_pdf, name='export_kpi_utilisation_pdf'),
    
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
    path('feuilles-route/imprimer/<int:pk>/', views.feuille_route_print, name='feuille_route_print'),
    
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
    path('paies-legacy/', views_management_complete.paie_employe_list, name='paie_employe_list'),
    path('paies-legacy/nouveau/<int:employe_id>/', views_management_complete.paie_employe_create, name='paie_employe_create'),
    path('paies-legacy/export/', views_management_complete.paie_employe_export, name='paie_employe_export'),
    path('paies-legacy/<int:pk>/edit/', views_management_complete.paie_employe_edit, name='paie_employe_edit'),
    path('paies-legacy/<int:pk>/delete/', views_management_complete.paie_employe_delete, name='paie_employe_delete'),
    
    # URLs pour les heures supplémentaires
    path('heures-supplementaires/', views_management_complete.heure_supplementaire_list, name='heure_supplementaire_list'),
    path('heures-supplementaires/ajouter/', views_management_complete.heure_supplementaire_add, name='heure_supplementaire_add'),
    path('heures-supplementaires/modifier/<int:pk>/', views_management_complete.heure_supplementaire_edit, name='heure_supplementaire_edit'),
    path('heures-supplementaires/export/', views_management_complete.heure_supplementaire_export, name='heure_supplementaire_export'),
    path('ajax/employe-info/', views_management_complete.get_employe_info_ajax, name='get_employe_info_ajax'),

    # URLs pour les bulletins de paie
    path('bulletins-paie/', views_management_complete.bulletin_paie_list, name='bulletin_paie_list'),
    path('bulletins-paie/imprimer/<int:employe_id>/', views_management_complete.bulletin_paie_print, name='bulletin_paie_print'),
    
    # URLs pour la configuration des charges sociales
    path('config-charges-sociales/', views_management_complete.config_charges_sociales, name='config_charges_sociales'),

    # URLs pour l'archivage mensuel
    path('archivage-mensuel/', views_management_complete.archive_mensuelle, name='archive_mensuelle_full'),
    path('archivage-mensuel/cloturer/', views_management_complete.cloturer_mois, name='cloturer_mois'),

    # URLs pour le pointage journalier
    path('pointage/', views_pointage.pointage_journalier, name='pointage_journalier'),
    path('pointage/ajax/', views_pointage.pointage_ajax, name='pointage_ajax'),
    path('pointage/formulaire/', views_pointage.pointage_formulaire, name='pointage_formulaire'),
    path('pointage/rapide/', views_pointage.pointage_rapide, name='pointage_rapide'),
    path('pointage/historique/', views_pointage.historique_pointage, name='historique_pointage'),
    
    # URLs pour les paramètres de paie
    path('parametres-paie/', views_management_complete.parametre_paie_list, name='parametre_paie_list'),
    path('parametres-paie/export/', views_management_complete.parametre_paie_export, name='parametre_paie_export'),
    
    # URLs pour les paies avec calculs automatiques de présence
    path('paies/', views_paie_enhanced.paie_employe_list_enhanced, name='paie_employe_list_enhanced'),
    # Alias pour l'ancienne URL de paie - redirige vers la nouvelle vue améliorée
    path('paies-list/', views_management_complete.paie_employe_list, name='paies_list'),
    path('paies/<int:paie_id>/', views_paie_enhanced.paie_employe_detail_enhanced, name='paie_employe_detail_enhanced'),
    path('paies/synchroniser/<int:employe_id>/', views_paie_enhanced.synchroniser_paie_individuelle, name='synchroniser_paie_individuelle'),
    path('paies/creer-manquantes/', views_paie_enhanced.creer_paies_manquantes, name='creer_paies_manquantes'),
    path('paies/export-csv/', views_paie_enhanced.export_paies_csv, name='export_paies_csv'),
    
    # URLs pour la synchronisation présence-paie
    path('synchroniser-presence-paie/', views_presence_sync.synchroniser_presence_paie_view, name='synchroniser_presence_paie'),
    path('rapport-presence-mois/', views_presence_sync.rapport_presence_mois_view, name='rapport_presence_mois'),
    path('verifier-coherence/', views_presence_sync.verifier_coherence_view, name='verifier_coherence'),
    path('dashboard-presence-paie/', views_presence_sync.dashboard_presence_paie, name='dashboard_presence_paie'),
    path('ajax/synchroniser-presence/', views_presence_sync.synchroniser_presence_ajax, name='synchroniser_presence_ajax'),
    path('ajax/statistiques-employe/', views_presence_sync.statistiques_employe_ajax, name='statistiques_employe_ajax'),
    
    # URLs pour le menu Minérai
    path('minerai/pesees-camions/', views_minerai.pesee_camion_list, name='pesee_camion_list'),
    path('minerai/pesees-camions/ajouter/', views_minerai.pesee_camion_add, name='pesee_camion_add'),
    path('minerai/pesees-camions/<int:pk>/', views_minerai.pesee_camion_detail, name='pesee_camion_detail'),
    path('minerai/pesees-camions/<int:pk>/modifier/', views_minerai.pesee_camion_update, name='pesee_camion_update'),
    path('minerai/pesees-camions/<int:pk>/supprimer/', views_minerai.pesee_camion_delete, name='pesee_camion_delete'),
    path('minerai/fiches-bord-machine/', views_minerai.fiche_bord_machine_list, name='fiche_bord_machine_list'),
    path('minerai/fiches-bord-machine/ajouter/', views_minerai.fiche_bord_machine_add, name='fiche_bord_machine_add'),
    path('minerai/fiches-bord-machine/export/', views_minerai.fiche_bord_machine_export, name='fiche_bord_machine_export'),
    path('minerai/fiches-or/', views_minerai.fiche_or_list, name='fiche_or_list'),
    path('minerai/fiches-or/ajouter/', views_minerai.fiche_or_add, name='fiche_or_add'),
    path('minerai/fiches-or/export/', views_minerai.fiche_or_export, name='fiche_or_export'),
    
    # URLs pour le menu Inventaire
    path('inventaire/produits/', views_inventaire.produit_list, name='produit_list'),
    path('inventaire/produits/creer/', views_inventaire.produit_create, name='produit_create'),
    path('inventaire/produits/<str:pk>/', views_inventaire.produit_detail, name='produit_detail'),
    path('inventaire/produits/<str:pk>/modifier/', views_inventaire.produit_update, name='produit_update'),
    path('inventaire/produits/<str:pk>/supprimer/', views_inventaire.produit_delete, name='produit_delete'),
    path('inventaire/entrees-stock/', views_inventaire.entree_stock_list, name='entree_stock_list'),
    path('inventaire/entrees-stock/creer/', views_inventaire.entree_stock_create, name='entree_stock_create'),
    path('inventaire/entrees-stock/<str:pk>/modifier/', views_inventaire.entree_stock_update, name='entree_stock_update'),
    path('inventaire/entrees-stock/<str:pk>/supprimer/', views_inventaire.entree_stock_delete, name='entree_stock_delete'),
    path('inventaire/sorties-stock/', views_inventaire.sortie_stock_list, name='sortie_stock_list'),
    path('inventaire/sorties-stock/creer/', views_inventaire.sortie_stock_create, name='sortie_stock_create'),
    path('inventaire/sorties-stock/<str:pk>/modifier/', views_inventaire.sortie_stock_update, name='sortie_stock_update'),
    path('inventaire/sorties-stock/<str:pk>/supprimer/', views_inventaire.sortie_stock_delete, name='sortie_stock_delete'),
    path('inventaire/dashboard/', views_inventaire.inventaire_dashboard, name='inventaire_dashboard'),
    path('inventaire/stock-actuel/', views_inventaire.stock_actuel, name='stock_actuel'),
    path('inventaire/mouvements-stock/', views_inventaire.mouvement_stock_list, name='mouvement_stock_list'),
    path('inventaire/commandes/', views_inventaire.commande_list, name='commande_list'),
    path('inventaire/commandes/creer/', views_inventaire.commande_create, name='commande_create'),
    path('inventaire/commandes/<str:pk>/', views_inventaire.commande_detail, name='commande_detail'),
    path('inventaire/commandes/<str:pk>/modifier/', views_inventaire.commande_update, name='commande_update'),
    path('inventaire/commandes/<str:pk>/supprimer/', views_inventaire.commande_delete, name='commande_delete'),
    path('inventaire/commandes/export/', views_inventaire.export_commandes_excel, name='export_commandes_excel'),
    path('inventaire/factures/', views_facturation.facture_list, name='facture_list'),
    path('inventaire/factures/creer/', views_facturation.facture_create, name='facture_create'),
    path('inventaire/factures/<str:pk>/', views_facturation.facture_detail, name='facture_detail'),
    path('inventaire/factures/<str:pk>/modifier/', views_facturation.facture_update, name='facture_update'),
    path('inventaire/factures/<str:pk>/supprimer/', views_facturation.facture_delete, name='facture_delete'),
    path('inventaire/factures/<str:pk>/pdf/', views_facturation.export_facture_pdf, name='export_facture_pdf'),
    path('inventaire/factures/export/', views_facturation.export_factures_excel, name='export_factures_excel'),
    
    # URLs pour le menu Locations (Locations de véhicules)
    path('locations/', views_location.locations_dashboard, name='locations_dashboard'),
    path('locations/list/', views_location.location_list, name='location_list'),
    path('locations/nouvelle/', views_location.location_create, name='location_create'),
    path('locations/<int:pk>/', views_location.location_detail, name='location_detail'),
    path('locations/<int:pk>/modifier/', views_location.location_update, name='location_update'),
    path('locations/<int:pk>/supprimer/', views_location.location_delete, name='location_delete'),
    
    # Feuilles de pontage
    path('locations/feuilles-pontage/', views_location.feuille_pontage_list, name='feuille_pontage_location_list'),
    path('locations/feuilles-pontage/nouvelle/', views_location.feuille_pontage_create, name='feuille_pontage_create'),
    path('locations/feuilles-pontage/<int:pk>/modifier/', views_location.feuille_pontage_update, name='feuille_pontage_update'),
    path('locations/feuilles-pontage/<int:pk>/supprimer/', views_location.feuille_pontage_delete, name='feuille_pontage_delete'),
    
    # Fournisseurs
    path('locations/fournisseurs/', views_location.fournisseur_list, name='fournisseur_location_list'),
    path('locations/fournisseurs/nouveau/', views_location.fournisseur_create, name='fournisseur_create'),
    path('locations/fournisseurs/nouveau-simple/', views_fournisseur_simple.fournisseur_create_simple, name='fournisseur_create_simple'),
    path('locations/fournisseurs/<int:pk>/modifier/', views_location.fournisseur_update, name='fournisseur_update'),
    path('locations/fournisseurs/<int:pk>/supprimer/', views_location.fournisseur_delete, name='fournisseur_delete'),
    
    # Factures
    path('locations/factures/', views_location.facture_list, name='facture_location_list'),
    path('locations/factures/nouvelle/', views_location.facture_create, name='facture_location_create'),
    path('locations/factures/<int:pk>/modifier/', views_location.facture_update, name='facture_location_update'),
    path('locations/factures/<int:pk>/supprimer/', views_location.facture_delete, name='facture_location_delete'),
    path('locations/factures/<int:pk>/', views_location.facture_detail, name='facture_location_detail'),
    path('locations/factures/<int:pk>/pdf/', views_location.facture_pdf, name='facture_location_pdf'),
    path('locations/factures/batch-pdf/', views_location.factures_batch_pdf, name='factures_batch_pdf'),
    path('locations/factures/generation-mensuelle/', views_location.generer_factures_mensuelles, name='generer_factures_mensuelles'),
    
    # AJAX
    path('locations/<int:location_pk>/generer-facture/', views_location.generer_facture_automatique, name='generer_facture_automatique'),
    path('locations/search-ajax/', views_location.location_search_ajax, name='location_search_ajax'),
    path('locations/dashboard-metrics/', views_location.locations_dashboard_metrics_ajax, name='locations_dashboard_metrics_ajax'),
    path('locations/feuilles/search-ajax/', views_location.feuille_pontage_search_ajax, name='feuille_pontage_search_ajax'),
    path('locations/fournisseurs/search-ajax/', views_location.fournisseur_search_ajax, name='fournisseur_search_ajax'),
    path('locations/factures/search-ajax/', views_location.facture_search_ajax, name='facture_search_ajax'),
    path('alertes/search-ajax/', views_alertes.alerte_search_ajax, name='alerte_search_ajax'),
    # AJAX for selects in location form
    path('ajax/search-vehicules/', views_location.search_vehicules_ajax, name='search_vehicules_ajax'),
    path('ajax/search-fournisseurs/', views_location.search_fournisseurs_ajax, name='search_fournisseurs_ajax'),
    path('ajax/fournisseur/quick-create/', views_location.fournisseur_quick_create_ajax, name='fournisseur_quick_create_ajax'),
    path('ajax/vehicule/quick-create/', views_location.vehicule_quick_create_ajax, name='vehicule_quick_create_ajax'),
    path('ajax/vehicule/get-fournisseur/', views_location.get_vehicule_fournisseur_ajax, name='get_vehicule_fournisseur_ajax'),
    
    # URLs pour les statistiques des véhicules
    path('stats/vehicules/', views_vehicule_stats.vehicule_stats_dashboard, name='vehicule_stats_dashboard'),
    path('stats/vehicules/comparaison/', views_vehicule_stats.vehicule_comparaison_stats, name='vehicule_comparaison_stats'),
    path('stats/vehicules/export/', views_vehicule_stats.vehicule_stats_export, name='vehicule_stats_export'),
    path('stats/vehicules/<str:vehicule_id>/', views_vehicule_stats.vehicule_stats_detail, name='vehicule_stats_detail'),
    
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
    
    # URLs pour les frais kilométriques (Bus/Km)
    path('frais-kilometriques/', views_entreprise.FraisKilometriqueListView.as_view(), name='frais_kilometrique_list'),
    path('frais-kilometriques/ajouter/', views_entreprise.frais_kilometrique_ajouter, name='frais_kilometrique_ajouter'),
    
    # Configuration des montants pour les présences (AJAX)
    path('configuration_montant_statut/', views_entreprise.configuration_montant_statut, name='configuration_montant_statut'),
    
    # Configuration des charges sociales (AJAX)
    path('config-charges-sociales/', views_entreprise.config_charges_sociales, name='config_charges_sociales'),
    
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
    
    # API de recherche dynamique
    path('api/recherche/', views.recherche_dynamique, name='api_recherche'),

]
