from django.urls import path
from . import views
from . import views_entreprise
from . import views_inventaire
from . import views_facturation
from . import views_debug
from . import views_force_delete

app_name = 'fleet_app'

urlpatterns = [
    # Page d'accueil
    path('', views.home, name='home'),
    # Tableau de bord
    path('dashboard/', views.dashboard, name='dashboard'),
    
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
    path('alertes/', views.alerte_list, name='alerte_list'),
    path('alertes/nouvelle/', views.alerte_nouvelle, name='alerte_nouvelle'),
    path('alertes/resoudre/<int:pk>/', views.alerte_resoudre, name='alerte_resoudre'),
    path('alertes/ignorer/<int:pk>/', views.alerte_ignorer, name='alerte_ignorer'),
    path('alertes/supprimer/<int:pk>/', views.alerte_supprimer, name='alerte_supprimer'),
    path('api/alertes-kpi/', views.get_alertes_kpi, name='api_alertes_kpi'),
    
    # API pour la recherche dynamique
    path('api/vehicules/', views.get_vehicules_list, name='get_vehicules_list'),
    path('api/chauffeurs/', views.get_chauffeurs_list, name='get_chauffeurs_list'),
    
    # Debug
    path('debug/vehicule/<str:id_vehicule>/', views_debug.debug_vehicle_relations, name='debug_vehicle_relations'),
]
