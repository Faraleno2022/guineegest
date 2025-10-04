from django.shortcuts import render, redirect, get_object_or_404
from datetime import timedelta
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, Avg, Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from decimal import Decimal, InvalidOperation
from datetime import datetime, timedelta, date
import json
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from .security import require_user_ownership, get_user_object_or_404
from .views_accounts import check_profile_completion

# Import des modèles
from .models import Vehicule, DistanceParcourue, ConsommationCarburant, DisponibiliteVehicule, CoutFonctionnement, CoutFinancier, IncidentSecurite, UtilisationActif, UtilisationVehicule, Chauffeur, FeuilleDeRoute, GalleryImage, DocumentAdministratif
from .models_alertes import Alerte

# Import des formulaires
from .forms import VehiculeForm, DistanceForm, ConsommationCarburantForm, DisponibiliteForm, CoutFonctionnementForm, CoutFinancierForm, IncidentSecuriteForm, UtilisationActifForm, UtilisationVehiculeForm, AlerteForm
from .forms_document import DocumentAdministratifForm

# Import des utilitaires
from .utils import convertir_en_gnf, formater_montant_gnf, formater_cout_par_km_gnf, TAUX_CONVERSION_EUR_GNF
from .utils.decorators import queryset_filter_by_tenant

# Vue de la page d'accueil
def home(request):
    """
    Vue de la page d'accueil qui affiche une présentation de l'entreprise
    Accessible à tous, même sans authentification
    """
    # Vérifier si l'utilisateur a complété son profil (seulement si connecté)
    if request.user.is_authenticated:
        profile_check = check_profile_completion(request)
        if profile_check:
            return profile_check
    
    from django.conf import settings
    
    # Dernières images de la galerie (upload via admin)
    try:
        latest_gallery = list(GalleryImage.objects.all().order_by('-created_at')[:12])
    except Exception:
        latest_gallery = []

    context = {
        'titre': 'Accueil',
        'description': 'Bienvenue dans le système de gestion du parc automobile',
        'MEDIA_URL': settings.MEDIA_URL,
        'gallery_images': latest_gallery,
    }
    return render(request, 'fleet_app/home.html', context)

# Galerie d'images simple
def gallery(request):
    """Page galerie publique: affiche les images uploadées via l'admin."""
    images = GalleryImage.objects.all().order_by('-created_at')
    context = {
        'titre': 'Galerie',
        'images': images,
    }
    return render(request, 'fleet_app/gallery.html', context)

# Fonction utilitaire pour la pagination et la recherche
def paginate_and_search(request, queryset, search_fields=None, per_page=10):
    """
    Fonction utilitaire pour gérer la pagination et la recherche
    
    Args:
        request: La requête HTTP
        queryset: Le queryset à paginer et filtrer
        search_fields: Liste des champs sur lesquels effectuer la recherche (format: model__field)
        per_page: Nombre d'éléments par page
        
    Returns:
        tuple: (queryset paginé, terme de recherche)
    """
    search_query = request.GET.get('search', '')
    
    # Appliquer le filtre de recherche si présent
    if search_query and search_fields:
        q_objects = Q()
        for field in search_fields:
            kwargs = {f"{field}__icontains": search_query}
            q_objects |= Q(**kwargs)
        queryset = queryset.filter(q_objects)
    
    # Pagination
    paginator = Paginator(queryset, per_page)
    page = request.GET.get('page', 1)
    
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)
        
    return paginated_queryset, search_query

from .models import *
from .forms import *
import json

# Helpers de filtrage de période pour les KPI
from datetime import date as _date, timedelta as _timedelta

def _period_dates(period: str):
    today = _date.today()
    if period == 'month':
        start = today.replace(day=1)
        end = today
    elif period == 'quarter':
        q = (today.month - 1) // 3
        start_month = q * 3 + 1
        start = _date(today.year, start_month, 1)
        end = today
    elif period == 'year':
        start = _date(today.year, 1, 1)
        end = today
    else:
        start = None
        end = None
    return start, end

def get_period_filter(request):
    """Retourne (start_date, end_date) à partir des paramètres GET period/start/end (YYYY-MM-DD)."""
    period = request.GET.get('period')
    start_param = request.GET.get('start')
    end_param = request.GET.get('end')
    start_date = end_date = None
    if period:
        start_date, end_date = _period_dates(period)
    # Priorité aux dates explicites si fournies
    from datetime import datetime as _dt
    fmt = '%Y-%m-%d'
    try:
        if start_param:
            start_date = _dt.strptime(start_param, fmt).date()
        if end_param:
            end_date = _dt.strptime(end_param, fmt).date()
    except Exception:
        pass
    return start_date, end_date

# Vue de tableau de bord
@login_required
def dashboard(request):
    # Vérifier si l'utilisateur a complété son profil
    profile_check = check_profile_completion(request)
    if profile_check:
        return profile_check
        
    # Statistiques globales (filtrées par tenant)
    vehicules_qs = queryset_filter_by_tenant(Vehicule.objects.all(), request)
    total_vehicules = vehicules_qs.count()
    vehicules_actifs = vehicules_qs.filter(statut_actuel='Actif').count()
    vehicules_maintenance = vehicules_qs.filter(statut_actuel='Maintenance').count()
    vehicules_hors_service = vehicules_qs.filter(statut_actuel='Hors Service').count()
    
    # Calcul des 7 KPI
    
    # 1. Distance parcourue - Moyenne par véhicule
    distances = DistanceParcourue.objects.filter(vehicule__in=vehicules_qs).values('vehicule').annotate(
        distance_totale=Sum('distance_parcourue')
    ).order_by('-distance_totale')[:5]  # Top 5 des véhicules par distance
    
    # Enrichir avec les détails du véhicule
    for d in distances:
        vehicule = vehicules_qs.get(id_vehicule=d['vehicule'])
        d['immatriculation'] = vehicule.immatriculation
        d['marque'] = vehicule.marque
        d['modele'] = vehicule.modele
        d['type_moteur'] = vehicule.type_moteur
        # Définir des objectifs selon le type de moteur
        if vehicule.type_moteur == 'Diesel':
            d['objectif'] = 30000  # 30 000 km/an pour diesel
            d['pourcentage'] = min(100, (d['distance_totale'] / 30000) * 100)
        elif vehicule.type_moteur == 'Essence':
            d['objectif'] = 15000  # 15 000 km/an pour essence
            d['pourcentage'] = min(100, (d['distance_totale'] / 15000) * 100)
        else:
            d['objectif'] = 10000  # 10 000 km/an pour autres
            d['pourcentage'] = min(100, (d['distance_totale'] / 10000) * 100)
    
    # 2. Consommation de carburant - Moyenne par véhicule
    consommations = ConsommationCarburant.objects.filter(vehicule__in=vehicules_qs).values('vehicule').annotate(
        consommation_moyenne=Avg('consommation_100km')
    ).order_by('-consommation_moyenne')[:5]  # Top 5 des véhicules par consommation
    
    # Enrichir avec les détails du véhicule
    for c in consommations:
        vehicule = vehicules_qs.get(id_vehicule=c['vehicule'])
        c['immatriculation'] = vehicule.immatriculation
        c['marque'] = vehicule.marque
        c['modele'] = vehicule.modele
        c['type_moteur'] = vehicule.type_moteur
        # Valeur cible basée sur type de moteur (simplifié)
        if vehicule.type_moteur == 'Diesel':
            c['cible'] = 6.0  # L/100km
        elif vehicule.type_moteur == 'Essence':
            c['cible'] = 7.0  # L/100km
        else:
            c['cible'] = 5.0  # L/100km
        # Calcul du dépassement
        c['depassement'] = max(0, c['consommation_moyenne'] - c['cible'])
        c['alerte'] = c['consommation_moyenne'] > c['cible'] * 1.2  # Alerte si 20% au-dessus de la cible
    
    # 3. Disponibilité des véhicules
    disponibilites = DisponibiliteVehicule.objects.filter(vehicule__in=vehicules_qs).values('vehicule').annotate(
        disponibilite_moyenne=Avg('disponibilite_pourcentage')
    ).order_by('disponibilite_moyenne')[:5]  # 5 véhicules les moins disponibles
    
    # Enrichir avec les détails du véhicule
    for d in disponibilites:
        vehicule = vehicules_qs.get(id_vehicule=d['vehicule'])
        d['immatriculation'] = vehicule.immatriculation
        d['marque'] = vehicule.marque
        d['modele'] = vehicule.modele
        d['alerte'] = d['disponibilite_moyenne'] < 80  # Alerte si disponibilité < 80%
    
    # 4. Utilisation des actifs
    utilisations = UtilisationActif.objects.values('vehicule').annotate(
        jours_utilises_total=Sum('jours_utilises'),
        jours_disponibles_total=Sum('jours_disponibles')
    ).order_by('vehicule')[:5]  # 5 premiers véhicules
    
    # Enrichir avec les détails du véhicule et calculer le taux d'utilisation
    for u in utilisations:
        vehicule = vehicules_qs.get(id_vehicule=u['vehicule'])
        u['immatriculation'] = vehicule.immatriculation
        u['marque'] = vehicule.marque
        u['modele'] = vehicule.modele
        # Calculer le taux d'utilisation manuellement
        if u['jours_disponibles_total'] > 0:
            u['utilisation_moyenne'] = (u['jours_utilises_total'] / u['jours_disponibles_total']) * 100
        else:
            u['utilisation_moyenne'] = 0
        u['alerte'] = u['utilisation_moyenne'] < 70  # Alerte si utilisation < 70%
    
    # 5. Sécurité - Incidents par véhicule
    incidents = IncidentSecurite.objects.filter(vehicule__in=vehicules_qs).values('vehicule').annotate(
        total_incidents=Count('id')
    ).order_by('-total_incidents')[:5]  # Top 5 des véhicules avec le plus d'incidents
    
    # Enrichir avec les détails du véhicule
    for i in incidents:
        vehicule = vehicules_qs.get(id_vehicule=i['vehicule'])
        i['immatriculation'] = vehicule.immatriculation
        i['marque'] = vehicule.marque
        i['modele'] = vehicule.modele
        i['alerte'] = i['total_incidents'] > 0  # Alerte si au moins un incident
    
    # 6 & 7. Coûts de fonctionnement et financiers par km
    couts_fonctionnement = CoutFonctionnement.objects.filter(vehicule__in=vehicules_qs).values('vehicule').annotate(
        cout_moyen=Avg('cout_par_km')
    ).order_by('-cout_moyen')[:5]  # Top 5 des véhicules les plus coûteux
    
    # Enrichir avec les détails du véhicule
    for c in couts_fonctionnement:
        vehicule = vehicules_qs.get(id_vehicule=c['vehicule'])
        c['immatriculation'] = vehicule.immatriculation
        c['marque'] = vehicule.marque
        c['modele'] = vehicule.modele
        c['categorie'] = vehicule.categorie
        # Seuil d'alerte basé sur la catégorie (simplifié)
        if vehicule.categorie == 'Utilitaire':
            c['seuil'] = 0.15  # €/km
        elif vehicule.categorie == 'Berline':
            c['seuil'] = 0.12  # €/km
        else:
            c['seuil'] = 0.10  # €/km
        c['alerte'] = c['cout_moyen'] > c['seuil']  # Alerte si coût > seuil
    
    couts_financiers = CoutFinancier.objects.filter(vehicule__in=vehicules_qs).values('vehicule').annotate(
        cout_moyen=Avg('cout_par_km')
    ).order_by('-cout_moyen')[:5]  # Top 5 des véhicules les plus coûteux
    
    # Enrichir avec les détails du véhicule
    for c in couts_financiers:
        vehicule = vehicules_qs.get(id_vehicule=c['vehicule'])
        c['immatriculation'] = vehicule.immatriculation
        c['marque'] = vehicule.marque
        c['modele'] = vehicule.modele
        c['categorie'] = vehicule.categorie
        # Seuil d'alerte basé sur la catégorie (simplifié)
        if vehicule.categorie == 'Utilitaire':
            c['seuil'] = 0.20  # €/km
        elif vehicule.categorie == 'Berline':
            c['seuil'] = 0.15  # €/km
        else:
            c['seuil'] = 0.12  # €/km
        c['alerte'] = c['cout_moyen'] > c['seuil']  # Alerte si coût > seuil
    
    # Générer des alertes automatiques basées sur les KPI
    alertes_kpi = []
    
    # Alertes de consommation
    for c in consommations:
        if c['alerte']:
            alertes_kpi.append({
                'type': 'Consommation',
                'vehicule': f"{c['marque']} {c['modele']} ({c['immatriculation']})",
                'message': f"Consommation excessive: {c['consommation_moyenne']:.1f} L/100km (cible: {c['cible']} L/100km)",
                'niveau': 'warning'
            })
    
    # Alertes de disponibilité
    for d in disponibilites:
        if d['alerte']:
            alertes_kpi.append({
                'type': 'Disponibilité',
                'vehicule': f"{d['marque']} {d['modele']} ({d['immatriculation']})",
                'message': f"Faible disponibilité: {d['disponibilite_moyenne']:.1f}% (cible: >80%)",
                'niveau': 'danger'
            })
    
    # Alertes d'utilisation
    for u in utilisations:
        if u['alerte']:
            alertes_kpi.append({
                'type': 'Utilisation',
                'vehicule': f"{u['marque']} {u['modele']} ({u['immatriculation']})",
                'message': f"Sous-utilisation: {u['utilisation_moyenne']:.1f}% (cible: >70%)",
                'niveau': 'warning'
            })
    
    # Alertes d'incidents
    for i in incidents:
        if i['alerte']:
            alertes_kpi.append({
                'type': 'Sécurité',
                'vehicule': f"{i['marque']} {i['modele']} ({i['immatriculation']})",
                'message': f"{i['total_incidents']} incident(s) enregistré(s)",
                'niveau': 'danger'
            })
    
    # Alertes de coûts
    for c in couts_fonctionnement:
        if c['alerte']:
            # Convertir les coûts en GNF
            from .utils import convertir_en_gnf, formater_cout_par_km_gnf
            cout_gnf = convertir_en_gnf(c['cout_moyen'])
            seuil_gnf = convertir_en_gnf(c['seuil'])
            alertes_kpi.append({
                'type': 'Coût de fonctionnement',
                'vehicule': f"{c['marque']} {c['modele']} ({c['immatriculation']})",
                'message': f"Coût élevé: {cout_gnf:.0f} GNF/km (seuil: {seuil_gnf:.0f} GNF/km)",
                'niveau': 'warning'
            })
    
    for c in couts_financiers:
        if c['alerte']:
            # Convertir les coûts en GNF
            from .utils import convertir_en_gnf, formater_cout_par_km_gnf
            cout_gnf = convertir_en_gnf(c['cout_moyen'])
            seuil_gnf = convertir_en_gnf(c['seuil'])
            alertes_kpi.append({
                'type': 'Coût financier',
                'vehicule': f"{c['marque']} {c['modele']} ({c['immatriculation']})",
                'message': f"Coût élevé: {cout_gnf:.0f} GNF/km (seuil: {seuil_gnf:.0f} GNF/km)",
                'niveau': 'warning'
            })
    
    # Statistiques par catégorie
    stats_categories = Vehicule.objects.values('categorie').annotate(total=Count('id_vehicule'))
    
    # Données pour graphiques
    categories_labels = [item['categorie'] for item in stats_categories]
    categories_data = [item['total'] for item in stats_categories]
    
    # Coûts moyens par catégorie
    from .utils import convertir_en_gnf
    
    couts_moyens_fonctionnement = CoutFonctionnement.objects.values('vehicule__categorie').annotate(
        moyenne=Avg('cout_par_km')
    ).order_by('vehicule__categorie')
    
    couts_moyens_financiers = CoutFinancier.objects.values('vehicule__categorie').annotate(
        moyenne=Avg('cout_par_km')
    ).order_by('vehicule__categorie')
    
    # Préparer les données pour le tableau des coûts moyens par catégorie
    couts_moyens_par_categorie = []
    categories_uniques = set()
    
    # Collecter toutes les catégories uniques
    for cout in couts_moyens_fonctionnement:
        categories_uniques.add(cout['vehicule__categorie'])
    for cout in couts_moyens_financiers:
        categories_uniques.add(cout['vehicule__categorie'])
    
    # Créer une structure de données pour le tableau
    for categorie in sorted(categories_uniques):
        cout_item = {
            'categorie': categorie,
            'cout_fonctionnement': 0,
            'cout_financier': 0,
            'cout_total': 0
        }
        
        # Ajouter les coûts de fonctionnement
        for cf in couts_moyens_fonctionnement:
            if cf['vehicule__categorie'] == categorie:
                cout_item['cout_fonctionnement'] = convertir_en_gnf(cf['moyenne'])
                break
        
        # Ajouter les coûts financiers
        for cf in couts_moyens_financiers:
            if cf['vehicule__categorie'] == categorie:
                cout_item['cout_financier'] = convertir_en_gnf(cf['moyenne'])
                break
        
        # Calculer le coût total
        cout_item['cout_total'] = cout_item['cout_fonctionnement'] + cout_item['cout_financier']
        
        couts_moyens_par_categorie.append(cout_item)
    
    # Données pour le graphique de coûts
    categories_cout = []
    couts_fonctionnement_data = []
    couts_financiers_data = []
    
    # Créer une liste unique de catégories
    for item in couts_moyens_fonctionnement:
        if item['vehicule__categorie'] not in categories_cout:
            categories_cout.append(item['vehicule__categorie'])
    
    for item in couts_moyens_financiers:
        if item['vehicule__categorie'] not in categories_cout:
            categories_cout.append(item['vehicule__categorie'])
    
    # Remplir les données pour chaque catégorie
    for cat in categories_cout:
        # Coûts de fonctionnement
        found = False
        for item in couts_moyens_fonctionnement:
            if item['vehicule__categorie'] == cat:
                couts_fonctionnement_data.append(item['moyenne'])
                found = True
                break
        if not found:
            couts_fonctionnement_data.append(0)
        
        # Coûts financiers
        found = False
        for item in couts_moyens_financiers:
            if item['vehicule__categorie'] == cat:
                couts_financiers_data.append(item['moyenne'])
                found = True
                break
        if not found:
            couts_financiers_data.append(0)
    
    # Recommandations pour remplacement
    vehicules_a_remplacer = []
    
    # Identifier les véhicules à remplacer (coûts élevés + faible disponibilité + incidents)
    vehicules_problematiques = {}
    
    # Ajouter des points négatifs pour les véhicules avec coûts élevés
    for c in couts_fonctionnement:
        if c['alerte']:
            if c['vehicule'] not in vehicules_problematiques:
                vehicules_problematiques[c['vehicule']] = {'points': 0, 'details': {}}
            vehicules_problematiques[c['vehicule']]['points'] += 2
            vehicules_problematiques[c['vehicule']]['details']['cout_fonctionnement'] = c['cout_moyen']
    
    for c in couts_financiers:
        if c['alerte']:
            if c['vehicule'] not in vehicules_problematiques:
                vehicules_problematiques[c['vehicule']] = {'points': 0, 'details': {}}
            vehicules_problematiques[c['vehicule']]['points'] += 2
            vehicules_problematiques[c['vehicule']]['details']['cout_financier'] = c['cout_moyen']
    
    # Ajouter des points négatifs pour les véhicules avec faible disponibilité
    for d in disponibilites:
        if d['alerte']:
            if d['vehicule'] not in vehicules_problematiques:
                vehicules_problematiques[d['vehicule']] = {'points': 0, 'details': {}}
            vehicules_problematiques[d['vehicule']]['points'] += 3
            vehicules_problematiques[d['vehicule']]['details']['disponibilite'] = d['disponibilite_moyenne']
    
    # Ajouter des points négatifs pour les véhicules avec incidents
    for i in incidents:
        if i['alerte']:
            if i['vehicule'] not in vehicules_problematiques:
                vehicules_problematiques[i['vehicule']] = {'points': 0, 'details': {}}
            vehicules_problematiques[i['vehicule']]['points'] += i['total_incidents'] * 2
            vehicules_problematiques[i['vehicule']]['details']['incidents'] = i['total_incidents']
    
    # Identifier les véhicules à remplacer (points négatifs > 5)
    for vehicule_id, data in vehicules_problematiques.items():
        if data['points'] >= 5:
            vehicule = Vehicule.objects.get(id_vehicule=vehicule_id)
            raisons = []
            if 'cout_fonctionnement' in data['details']:
                raisons.append(f"Coût fonctionnement élevé: {data['details']['cout_fonctionnement']:.2f} €/km")
            if 'cout_financier' in data['details']:
                raisons.append(f"Coût financier élevé: {data['details']['cout_financier']:.2f} €/km")
            if 'disponibilite' in data['details']:
                raisons.append(f"Faible disponibilité: {data['details']['disponibilite']:.1f}%")
            if 'incidents' in data['details']:
                raisons.append(f"{data['details']['incidents']} incident(s)")
            
            vehicules_a_remplacer.append({
                'vehicule': vehicule,
                'raisons': raisons,
                'score': data['points']
            })
    
    # Trier par score décroissant
    vehicules_a_remplacer = sorted(vehicules_a_remplacer, key=lambda x: x['score'], reverse=True)[:3]
    
    # Définir les seuils pour les KPI
    kpi_seuils = {
        'distance': {'cible': 30000, 'acceptable': 25000, 'critique': 20000},  # km/an
        'consommation': {'cible': 8, 'acceptable': 10, 'critique': 12},  # L/100km
        'disponibilite': {'cible': 90, 'acceptable': 80, 'critique': 70},  # %
        'utilisation': {'cible': 85, 'acceptable': 70, 'critique': 60},  # %
        'incidents': {'cible': 0, 'acceptable': 2, 'critique': 5},  # nombre
        'cout_fonctionnement': {'cible': 0.15, 'acceptable': 0.20, 'critique': 0.25},  # €/km
        'cout_financier': {'cible': 0.25, 'acceptable': 0.30, 'critique': 0.35},  # €/km
    }
    
    # Calculer les valeurs moyennes actuelles pour chaque KPI pour le tableau récapitulatif
    kpi_resultats_actuels = {}
    
    # 1. Distance moyenne parcourue
    distance_moyenne = DistanceParcourue.objects.aggregate(moyenne=Avg('distance_parcourue'))['moyenne'] or 0
    kpi_resultats_actuels['distance'] = distance_moyenne
    
    # 2. Consommation moyenne de carburant
    consommation_moyenne = ConsommationCarburant.objects.aggregate(moyenne=Avg('consommation_100km'))['moyenne'] or 0
    kpi_resultats_actuels['consommation'] = consommation_moyenne
    
    # 3. Disponibilité moyenne
    disponibilite_moyenne = DisponibiliteVehicule.objects.aggregate(moyenne=Avg('disponibilite_pourcentage'))['moyenne'] or 0
    kpi_resultats_actuels['disponibilite'] = disponibilite_moyenne
    
    # 4. Utilisation moyenne des actifs
    utilisation_totale = UtilisationActif.objects.aggregate(
        jours_utilises=Sum('jours_utilises'),
        jours_disponibles=Sum('jours_disponibles')
    )
    if utilisation_totale['jours_disponibles'] and utilisation_totale['jours_disponibles'] > 0:
        utilisation_moyenne = (utilisation_totale['jours_utilises'] / utilisation_totale['jours_disponibles']) * 100
    else:
        utilisation_moyenne = 0
    kpi_resultats_actuels['utilisation'] = utilisation_moyenne
    
    # 5. Sécurité - Nombre total d'incidents
    incidents_total = IncidentSecurite.objects.count()
    kpi_resultats_actuels['incidents'] = incidents_total
    
    # Préparer la liste des incidents par véhicule pour le template
    incidents_par_vehicule = []
    for vehicule in Vehicule.objects.filter(statut_actuel='Actif')[:10]:  # Limiter à 10 véhicules pour la lisibilité
        total_incidents = IncidentSecurite.objects.filter(vehicule=vehicule).count()
        incidents_par_vehicule.append({
            'marque': vehicule.marque,
            'modele': vehicule.modele,
            'immatriculation': vehicule.immatriculation,
            'total_incidents': total_incidents,
            'alerte': total_incidents > kpi_seuils['incidents']['acceptable']
        })
    
    # 6. Coût de fonctionnement moyen par km
    cout_fonctionnement_moyen = CoutFonctionnement.objects.aggregate(moyenne=Avg('cout_par_km'))['moyenne'] or 0
    kpi_resultats_actuels['cout_fonctionnement'] = cout_fonctionnement_moyen
    
    # 7. Coût financier moyen par km
    cout_financier_moyen = CoutFinancier.objects.aggregate(moyenne=Avg('cout_par_km'))['moyenne'] or 0
    kpi_resultats_actuels['cout_financier'] = cout_financier_moyen

    # Préparer les données pour la comparaison des véhicules
    # 1. Comparaison de consommation
    comparaison_consommation = []
    top_vehicules = Vehicule.objects.filter(statut_actuel='Actif').order_by('id_vehicule')[:5]

    for vehicule in top_vehicules:
        # Récupérer la dernière consommation enregistrée pour ce véhicule
        derniere_consommation = ConsommationCarburant.objects.filter(vehicule=vehicule).order_by('-date_plein2').first()
        if derniere_consommation:
            comparaison_consommation.append({
                'vehicule': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'consommation': round(derniere_consommation.consommation_100km, 2)
            })

    # 2. Comparaison de disponibilité
    comparaison_disponibilite = []
    for vehicule in top_vehicules:
        # Récupérer la dernière disponibilité enregistrée pour ce véhicule
        derniere_disponibilite = DisponibiliteVehicule.objects.filter(vehicule=vehicule).order_by('-date_fin').first()
        if derniere_disponibilite:
            comparaison_disponibilite.append({
                'vehicule': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'disponibilite': round(derniere_disponibilite.disponibilite_pourcentage, 2)
            })

    # 3. Comparaison des coûts
    comparaison_couts = []
    for vehicule in top_vehicules:
        # Récupérer le dernier coût enregistré pour ce véhicule
        dernier_cout = CoutFonctionnement.objects.filter(vehicule=vehicule).order_by('-date').first()
        if dernier_cout:
            comparaison_couts.append({
                'vehicule': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'cout': round(dernier_cout.cout_par_km, 3)
            })

    # Générer les alertes KPI automatiques
    alertes_kpi = []

    # Récupérer les véhicules avec leurs dernières mesures de KPI
    vehicules = vehicules_qs.filter(statut_actuel='Actif')
    
    for vehicule in vehicules:
        # Vérifier la consommation
        derniere_consommation = ConsommationCarburant.objects.filter(vehicule=vehicule).order_by('-date_plein2').first()
        if derniere_consommation and derniere_consommation.consommation_100km > kpi_seuils['consommation']['acceptable']:
            severite = 'Critique' if derniere_consommation.consommation_100km > kpi_seuils['consommation']['critique'] else 'Élevé'
            alertes_kpi.append({
                'type_kpi': 'Consommation',
                'vehicule': vehicule,
                'valeur_actuelle': derniere_consommation.consommation_100km,
                'seuil': kpi_seuils['consommation']['acceptable'],
                'ecart': derniere_consommation.consommation_100km - kpi_seuils['consommation']['acceptable'],
                'severite': severite,
                'unite': 'L/100km'
            })
        
        # Vérifier la disponibilité
        derniere_disponibilite = DisponibiliteVehicule.objects.filter(vehicule=vehicule).order_by('-date_fin').first()
        if derniere_disponibilite and derniere_disponibilite.disponibilite_pourcentage < kpi_seuils['disponibilite']['acceptable']:
            severite = 'Critique' if derniere_disponibilite.disponibilite_pourcentage < kpi_seuils['disponibilite']['critique'] else 'Élevé'
            alertes_kpi.append({
                'type_kpi': 'Disponibilité',
                'vehicule': vehicule,
                'valeur_actuelle': derniere_disponibilite.disponibilite_pourcentage,
                'seuil': kpi_seuils['disponibilite']['acceptable'],
                'ecart': kpi_seuils['disponibilite']['acceptable'] - derniere_disponibilite.disponibilite_pourcentage,
                'severite': severite,
                'unite': '%'
            })
        
        # Vérifier l'utilisation
        derniere_utilisation = UtilisationActif.objects.filter(vehicule=vehicule).order_by('-date_fin').first()
        if derniere_utilisation and derniere_utilisation.jours_disponibles > 0:
            taux_utilisation = (derniere_utilisation.jours_utilises / derniere_utilisation.jours_disponibles) * 100
            if taux_utilisation < kpi_seuils['utilisation']['acceptable']:
                severite = 'Critique' if taux_utilisation < kpi_seuils['utilisation']['critique'] else 'Élevé'
                alertes_kpi.append({
                    'type_kpi': 'Utilisation',
                    'vehicule': vehicule,
                    'valeur_actuelle': taux_utilisation,
                    'seuil': kpi_seuils['utilisation']['acceptable'],
                    'ecart': kpi_seuils['utilisation']['acceptable'] - taux_utilisation,
                    'severite': severite,
                    'unite': '%'
                })
        
        # Vérifier les coûts de fonctionnement
        dernier_cout_fonct = CoutFonctionnement.objects.filter(vehicule=vehicule).order_by('-date').first()
        if dernier_cout_fonct and dernier_cout_fonct.cout_par_km > kpi_seuils['cout_fonctionnement']['acceptable']:
            severite = 'Critique' if dernier_cout_fonct.cout_par_km > kpi_seuils['cout_fonctionnement']['critique'] else 'Élevé'
            alertes_kpi.append({
                'type_kpi': 'Coût fonctionnement',
                'vehicule': vehicule,
                'valeur_actuelle': dernier_cout_fonct.cout_par_km,
                'seuil': kpi_seuils['cout_fonctionnement']['acceptable'],
                'ecart': dernier_cout_fonct.cout_par_km - kpi_seuils['cout_fonctionnement']['acceptable'],
                'severite': severite,
                'unite': '€/km'
            })
    
    # Trier les alertes par sévérité (Critique d'abord, puis Élevé)
    alertes_kpi = sorted(alertes_kpi, key=lambda x: 0 if x['severite'] == 'Critique' else 1)
    
    # Limiter à 10 alertes pour ne pas surcharger l'interface
    alertes_kpi = alertes_kpi[:10]
    
    # Préparer les données pour les graphiques de comparaison
    # 1. Comparaison de consommation par véhicule
    comparaison_consommation = []
    for vehicule in vehicules[:5]:  # Limiter à 5 véhicules pour la lisibilité
        consommation_moyenne = ConsommationCarburant.objects.filter(vehicule=vehicule).aggregate(moyenne=Avg('consommation_100km'))['moyenne'] or 0
        comparaison_consommation.append({
            'vehicule': f"{vehicule.marque} {vehicule.modele}",
            'consommation': round(consommation_moyenne, 1)
        })
    
    # 2. Comparaison de disponibilité par véhicule
    comparaison_disponibilite = []
    for vehicule in vehicules[:5]:  # Limiter à 5 véhicules pour la lisibilité
        disponibilite_moyenne = DisponibiliteVehicule.objects.filter(vehicule=vehicule).aggregate(moyenne=Avg('disponibilite_pourcentage'))['moyenne'] or 0
        comparaison_disponibilite.append({
            'vehicule': f"{vehicule.marque} {vehicule.modele}",
            'disponibilite': round(disponibilite_moyenne, 1)
        })
    
    # 3. Comparaison des coûts par véhicule
    comparaison_couts = []
    for vehicule in vehicules[:5]:  # Limiter à 5 véhicules pour la lisibilité
        cout_moyen = CoutFonctionnement.objects.filter(vehicule=vehicule).aggregate(moyenne=Avg('cout_par_km'))['moyenne'] or 0
        comparaison_couts.append({
            'vehicule': f"{vehicule.marque} {vehicule.modele}",
            'cout': round(cout_moyen, 2)
        })
    
    # Améliorer l'identification des véhicules à remplacer avec un score et des raisons détaillées
    for vehicule_id, data in vehicules_problematiques.items():
        if data['points'] >= 5:
            vehicule = vehicules_qs.get(id_vehicule=vehicule_id)
            raisons = []
            
            # Ajouter des raisons plus détaillées avec des recommandations
            if 'cout_fonctionnement' in data['details']:
                cout = data['details']['cout_fonctionnement']
                raisons.append(f"Coût fonctionnement élevé: {cout:.2f} €/km (dépasse de {(cout/kpi_seuils['cout_fonctionnement']['cible']-1)*100:.0f}% la cible)")
            
            if 'cout_financier' in data['details']:
                cout = data['details']['cout_financier']
                raisons.append(f"Coût financier élevé: {cout:.2f} €/km (dépasse de {(cout/kpi_seuils['cout_financier']['cible']-1)*100:.0f}% la cible)")
            
            if 'disponibilite' in data['details']:
                dispo = data['details']['disponibilite']
                raisons.append(f"Faible disponibilité: {dispo:.1f}% (en dessous de {kpi_seuils['disponibilite']['cible']}%)")
            
            if 'incidents' in data['details']:
                incidents = data['details']['incidents']
                raisons.append(f"{incidents} incident(s) de sécurité récent(s)")
            
            # Ajouter l'âge du véhicule comme facteur si disponible
            if vehicule.date_mise_service:
                age_annees = (timezone.now().date() - vehicule.date_mise_service).days / 365.25
                if age_annees > 5:  # Considérer les véhicules de plus de 5 ans comme vieillissants
                    raisons.append(f"Véhicule âgé de {age_annees:.1f} ans")
            
            vehicules_a_remplacer.append({
                'vehicule': vehicule,
                'raisons': raisons,
                'score': data['points'],
                'recommandation': "Remplacement recommandé" if data['points'] >= 8 else "Surveillance recommandée"
            })
    
    # Trier par score décroissant
    vehicules_a_remplacer = sorted(vehicules_a_remplacer, key=lambda x: x['score'], reverse=True)[:5]
    
    # Préparer les données pour les graphiques d'évolution
    # Récupérer les données des 12 derniers mois pour les KPI
    date_debut = timezone.now().date() - timedelta(days=365)
    
    # Évolution mensuelle de la consommation
    evolution_consommation = ConsommationCarburant.objects.filter(
        vehicule__in=vehicules_qs,
        date_plein2__gte=date_debut
    ).annotate(
        mois=TruncMonth('date_plein2')
    ).values('mois').annotate(
        moyenne=Avg('consommation_100km')
    ).order_by('mois')
    
    # Évolution mensuelle de la disponibilité
    evolution_disponibilite = DisponibiliteVehicule.objects.filter(
        vehicule__in=vehicules_qs,
        date_fin__gte=date_debut
    ).annotate(
        mois=TruncMonth('date_fin')
    ).values('mois').annotate(
        moyenne=Avg('disponibilite_pourcentage')
    ).order_by('mois')
    
    # Évolution mensuelle des coûts
    evolution_couts = CoutFonctionnement.objects.filter(
        vehicule__in=vehicules_qs,
        date__gte=date_debut
    ).annotate(
        mois=TruncMonth('date')
    ).values('mois').annotate(
        moyenne=Avg('cout_par_km')
    ).order_by('mois')
    
    # Récupérer les données des feuilles de route pour le tableau de bord
    # 1. Feuilles de route récentes (5 dernières)
    feuilles_route_recentes = FeuilleDeRoute.objects.filter(vehicule__in=vehicules_qs).order_by('-date_depart')[:5]
    
    # 2. Feuilles de route avec surconsommation (consommation > 8 L/100km)
    feuilles_route_surconsommation = FeuilleDeRoute.objects.filter(vehicule__in=vehicules_qs, consommation__gt=8).order_by('-consommation')[:5]
    
    # 3. Feuilles de route en attente (non complétées par les chauffeurs)
    feuilles_route_attente = FeuilleDeRoute.objects.filter(
        Q(km_retour__isnull=True) | 
        Q(carburant_utilise__isnull=True) | 
        Q(signature_chauffeur=False)
    ).filter(vehicule__in=vehicules_qs).order_by('-date_depart')[:5]
    
    # Préparer les données pour les graphiques
    labels_mois = []
    data_consommation = []
    data_disponibilite = []
    data_couts = []
    
    # Remplir avec des données pour chaque mois
    mois_actuel = timezone.now().date().replace(day=1)
    for i in range(12):
        mois = (mois_actuel - timedelta(days=30*i)).replace(day=1)
        labels_mois.append(mois.strftime('%b %Y'))
    
    # Inverser pour avoir l'ordre chronologique
    labels_mois.reverse()
    
    # Préparer les données pour JSON
    evolution_data = {
        'labels': labels_mois,
        'consommation': [round(item['moyenne'], 2) if item['moyenne'] else 0 for item in evolution_consommation],
        'disponibilite': [round(item['moyenne'], 2) if item['moyenne'] else 0 for item in evolution_disponibilite],
        'couts': [round(item['moyenne'], 3) if item['moyenne'] else 0 for item in evolution_couts]
    }
    
    # Calculer les coûts moyens par catégorie de véhicule (tenant)
    couts_moyens_fonctionnement = CoutFonctionnement.objects.filter(vehicule__in=vehicules_qs).values('vehicule__categorie').annotate(
        moyenne=Avg('cout_par_km')
    ).order_by('vehicule__categorie')
    
    couts_moyens_financiers = CoutFinancier.objects.filter(vehicule__in=vehicules_qs).values('vehicule__categorie').annotate(
        moyenne=Avg('cout_par_km')
    ).order_by('vehicule__categorie')
    
    # Statistiques sur les chauffeurs (tenant-aware)
    chauffeurs_qs = queryset_filter_by_tenant(Chauffeur.objects.all(), request)
    total_chauffeurs = chauffeurs_qs.count()
    chauffeurs_actifs = chauffeurs_qs.filter(statut='Actif').count()
    chauffeurs_inactifs = chauffeurs_qs.filter(statut='Inactif').count()
    
    # Liste de tous les chauffeurs (tenant-aware)
    tous_chauffeurs = chauffeurs_qs.order_by('nom', 'prenom')
    
    # Dates pour la gestion des expirations de permis
    today = timezone.now().date()
    today_plus_30 = today + timedelta(days=30)
    
    # Top 5 des chauffeurs par nombre de feuilles de route
    top_chauffeurs = Chauffeur.objects.annotate(
        nb_feuilles=Count('feuilles_route')
    ).order_by('-nb_feuilles')[:5]
    
    # Statistiques sur les feuilles de route
    total_feuilles_route = FeuilleDeRoute.objects.filter(vehicule__in=vehicules_qs).count()
    feuilles_route_completees = FeuilleDeRoute.objects.filter(vehicule__in=vehicules_qs, km_retour__isnull=False).count()
    feuilles_route_en_attente = FeuilleDeRoute.objects.filter(vehicule__in=vehicules_qs, km_retour__isnull=True).count()
    
    # Statistiques de consommation moyenne par chauffeur
    consommation_par_chauffeur = FeuilleDeRoute.objects.filter(
        vehicule__in=vehicules_qs,
        consommation__isnull=False
    ).values('chauffeur__nom', 'chauffeur__prenom').annotate(
        consommation_moyenne=Avg('consommation'),
        nb_feuilles=Count('id')
    ).order_by('-consommation_moyenne')[:5]
    context = {
        'total_vehicules': total_vehicules,
        'vehicules_actifs': vehicules_actifs,
        'vehicules_maintenance': vehicules_maintenance,
        'vehicules_hors_service': vehicules_hors_service,
        'distances': distances,
        'consommations': consommations,
        'disponibilites': disponibilites,
        'utilisations': utilisations,
        'incidents': incidents,
        'couts_fonctionnement': couts_fonctionnement,
        'couts_financiers': couts_financiers,
        'alertes_kpi': alertes_kpi,
        'stats_categories': stats_categories,
        'categories_labels': json.dumps(categories_labels),
        'categories_data': json.dumps(categories_data),
        'couts_moyens_par_categorie': couts_moyens_par_categorie,
        'vehicules_a_remplacer': vehicules_a_remplacer,
        'kpi_seuils': kpi_seuils,
        'kpi_resultats_actuels': kpi_resultats_actuels,
        'incidents_par_vehicule': incidents_par_vehicule,
        'comparaison_consommation': comparaison_consommation,
        'comparaison_disponibilite': comparaison_disponibilite,
        'comparaison_couts': comparaison_couts,
        'labels_mois': json.dumps(labels_mois),
        'data_consommation': json.dumps(data_consommation),
        'data_disponibilite': json.dumps(data_disponibilite),
        'data_couts': json.dumps(data_couts),
        # Données des feuilles de route pour le tableau de bord
        'feuilles_route_recentes': feuilles_route_recentes,
        'feuilles_route_surconsommation': feuilles_route_surconsommation,
        'feuilles_route_attente': feuilles_route_attente,
        'evolution_data': json.dumps(evolution_data),
        'couts_moyens_fonctionnement': couts_moyens_fonctionnement,
        'couts_moyens_financiers': couts_moyens_financiers,
        # Statistiques des chauffeurs
        'total_chauffeurs': total_chauffeurs,
        'chauffeurs_actifs': chauffeurs_actifs,
        'chauffeurs_inactifs': chauffeurs_inactifs,
        'top_chauffeurs': top_chauffeurs,
        'tous_chauffeurs': tous_chauffeurs,
        'today': today,
        'today_plus_30': today_plus_30,
        # Statistiques des feuilles de route
        'total_feuilles_route': total_feuilles_route,
        'feuilles_route_completees': feuilles_route_completees,
        'feuilles_route_en_attente': feuilles_route_en_attente,
        'consommation_par_chauffeur': consommation_par_chauffeur,
    }
    
    return render(request, 'fleet_app/dashboard.html', context)

# Vues pour les chauffeurs
class ChauffeurListView(LoginRequiredMixin, ListView):
    model = Chauffeur
    template_name = 'fleet_app/chauffeur_list.html'
    context_object_name = 'chauffeurs'
    ordering = ['nom', 'prenom']
    paginate_by = 10

    def get_queryset(self):
        qs = Chauffeur.objects.filter(user=self.request.user).order_by(*self.ordering)
        # Recherche
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(nom__icontains=search) |
                Q(prenom__icontains=search) |
                Q(numero_permis__icontains=search) |
                Q(telephone__icontains=search)
            )
        # Filtre de période sur la validité du permis (ou date_naissance si souhaité)
        start_date, end_date = get_period_filter(self.request)
        if start_date:
            qs = qs.filter(date_validite_permis__gte=start_date)
        if end_date:
            qs = qs.filter(date_validite_permis__lte=end_date)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = get_period_filter(self.request)
        context['period'] = self.request.GET.get('period', '')
        context['period_start'] = start_date
        context['period_end'] = end_date
        context['search_query'] = self.request.GET.get('search', '')
        return context

class ChauffeurDetailView(LoginRequiredMixin, DetailView):
    model = Chauffeur
    template_name = 'fleet_app/chauffeur_detail.html'
    context_object_name = 'chauffeur'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chauffeur = self.get_object()
        
        # Récupérer les feuilles de route récentes du chauffeur
        context['feuilles_route'] = FeuilleDeRoute.objects.filter(chauffeur=chauffeur).order_by('-date_depart')[:5]
        
        # Statistiques du chauffeur
        total_feuilles = FeuilleDeRoute.objects.filter(chauffeur=chauffeur).count()
        total_distance = FeuilleDeRoute.objects.filter(chauffeur=chauffeur).aggregate(Sum('distance_parcourue'))['distance_parcourue__sum'] or 0
        total_surconsommation = FeuilleDeRoute.objects.filter(chauffeur=chauffeur, consommation__gt=8).count()
        
        context['stats'] = {
            'total_feuilles': total_feuilles,
            'total_distance': total_distance,
            'total_surconsommation': total_surconsommation,
        }
        
        return context

class ChauffeurCreateView(LoginRequiredMixin, CreateView):
    model = Chauffeur
    template_name = 'fleet_app/chauffeur_form.html'
    fields = ['nom', 'prenom', 'date_naissance', 'numero_permis', 'date_validite_permis', 'telephone', 'email', 'adresse', 'photo']
    success_url = reverse_lazy('fleet_app:chauffeur_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Chauffeur ajouté avec succès.')
        return super().form_valid(form)

class ChauffeurUpdateView(LoginRequiredMixin, UpdateView):
    model = Chauffeur
    template_name = 'fleet_app/chauffeur_form.html'
    fields = ['nom', 'prenom', 'date_naissance', 'numero_permis', 'date_validite_permis', 'telephone', 'email', 'adresse', 'photo']
    success_url = reverse_lazy('fleet_app:chauffeur_list')
    pk_url_kwarg = 'id_chauffeur'
    
    def form_valid(self, form):
        messages.success(self.request, 'Chauffeur modifié avec succès.')
        return super().form_valid(form)

class ChauffeurDeleteView(LoginRequiredMixin, DeleteView):
    model = Chauffeur
    template_name = 'fleet_app/chauffeur_confirm_delete.html'
    success_url = reverse_lazy('fleet_app:chauffeur_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Chauffeur supprimé avec succès.')
        return super().delete(request, *args, **kwargs)

# Vues pour les feuilles de route
class FeuilleRouteListView(LoginRequiredMixin, ListView):
    model = FeuilleDeRoute
    template_name = 'fleet_app/feuille_route_list.html'
    context_object_name = 'feuilles_route'
    ordering = ['-date_depart']
    paginate_by = 10

    def get_queryset(self):
        qs = FeuilleDeRoute.objects.filter(vehicule__user=self.request.user).order_by(*self.ordering)
        # Recherche
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(vehicule__immatriculation__icontains=search) |
                Q(chauffeur__nom__icontains=search) |
                Q(chauffeur__prenom__icontains=search) |
                Q(destination__icontains=search)
            )
        # Filtre de période sur date_depart/date_retour
        start_date, end_date = get_period_filter(self.request)
        if start_date:
            qs = qs.filter(date_depart__gte=start_date)
        if end_date:
            qs = qs.filter(date_depart__lte=end_date)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = get_period_filter(self.request)
        context['period'] = self.request.GET.get('period', '')
        context['period_start'] = start_date
        context['period_end'] = end_date
        context['search_query'] = self.request.GET.get('search', '')
        return context

# ---------- PDF UTIL ----------
def render_to_pdf(template_src, context_dict, filename):
    try:
        from xhtml2pdf import pisa
    except Exception:
        return HttpResponse('Génération PDF indisponible (xhtml2pdf/reportlab manquants).', status=503)

    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    return HttpResponse('Erreur lors de la génération du PDF', status=500)

# ---------- PDF EXPORT VIEWS ----------
@login_required
def export_vehicules_pdf(request):
    start_date, end_date = get_period_filter(request)
    qs = Vehicule.objects.filter(user=request.user).order_by('id_vehicule')
    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(Q(immatriculation__icontains=search) | Q(marque__icontains=search) | Q(modele__icontains=search))
    if start_date:
        qs = qs.filter(date_acquisition__gte=start_date)
    if end_date:
        qs = qs.filter(date_acquisition__lte=end_date)
    context = {
        'vehicules': qs,
        'generated_at': timezone.now(),
        'period': request.GET.get('period', ''),
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
    }
    return render_to_pdf('fleet_app/pdf/vehicules_list_pdf.html', context, 'vehicules.pdf')

@login_required
def export_feuilles_route_pdf(request):
    start_date, end_date = get_period_filter(request)
    qs = FeuilleDeRoute.objects.filter(vehicule__user=request.user).order_by('-date_depart')
    search = request.GET.get('search', '')
    if search:
        qs = qs.filter(
            Q(vehicule__immatriculation__icontains=search) |
            Q(chauffeur__nom__icontains=search) |
            Q(chauffeur__prenom__icontains=search) |
            Q(destination__icontains=search)
        )
    if start_date:
        qs = qs.filter(date_depart__gte=start_date)
    if end_date:
        qs = qs.filter(date_depart__lte=end_date)
    context = {
        'feuilles_route': qs,
        'generated_at': timezone.now(),
        'period': request.GET.get('period', ''),
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
    }
    return render_to_pdf('fleet_app/pdf/feuilles_route_list_pdf.html', context, 'feuilles_route.pdf')

class FeuilleRouteDetailView(LoginRequiredMixin, DetailView):
    model = FeuilleDeRoute
    template_name = 'fleet_app/feuille_route_detail.html'
    context_object_name = 'feuille_route'

@login_required
def feuille_route_add(request):
    if request.method == 'POST':
        form = FeuilleRouteForm(request.POST)
        if form.is_valid():
            feuille_route = form.save(commit=False)
            feuille_route.date_creation = timezone.now()
            feuille_route.save()
            messages.success(request, 'Feuille de route créée avec succès.')
            return redirect('fleet_app:feuille_route_detail', pk=feuille_route.pk)
    else:
        form = FeuilleRouteForm()
    
    return render(request, 'fleet_app/feuille_route_form.html', {'form': form})

@login_required
@require_user_ownership(FeuilleDeRoute)
def feuille_route_edit(request, pk):
    feuille_route = get_user_object_or_404(FeuilleDeRoute, request.user, pk=pk)
    if request.method == 'POST':
        form = FeuilleRouteUpdateForm(request.POST, instance=feuille_route)
        if form.is_valid():
            feuille = form.save(commit=False)

            # Marquer la feuille comme complétée par le chauffeur automatiquement
            feuille.signature_chauffeur = True

            # Calculer la distance parcourue si les kilomètres sont fournis
            if feuille.km_depart is not None and feuille.km_retour is not None:
                feuille.distance_parcourue = max(0, feuille.km_retour - feuille.km_depart)

            # Calculer le carburant utilisé si les données nécessaires sont fournies
            if feuille.carburant_depart is not None and feuille.carburant_retour is not None:
                feuille.carburant_utilise = feuille.carburant_depart - feuille.carburant_retour

            # Calculer la consommation si possible
            if feuille.distance_parcourue and feuille.distance_parcourue > 0 and feuille.carburant_utilise is not None:
                feuille.consommation = (feuille.carburant_utilise * 100) / feuille.distance_parcourue
                # Déterminer l'alerte de surconsommation (seuil 8 L/100km)
                feuille.alerte_surconsommation = feuille.consommation > 8
            else:
                feuille.alerte_surconsommation = False

            feuille.save()
            messages.success(request, 'Feuille de route mise à jour avec succès.')
            return redirect('fleet_app:feuille_route_detail', pk=feuille.pk)
    else:
        form = FeuilleRouteUpdateForm(instance=feuille_route)
    
    return render(request, 'fleet_app/feuille_route_update_form.html', {'form': form, 'feuille_route': feuille_route})

@login_required
@require_user_ownership(FeuilleDeRoute)
def feuille_route_delete(request, pk):
    feuille_route = get_user_object_or_404(FeuilleDeRoute, request.user, pk=pk)
    if request.method == 'POST':
        feuille_route.delete()
        messages.success(request, 'Feuille de route supprimée avec succès.')
        return redirect('fleet_app:feuille_route_list')
    
    return render(request, 'fleet_app/feuille_route_confirm_delete.html', {'feuille_route': feuille_route})

@login_required
@require_user_ownership(FeuilleDeRoute)
def feuille_route_print(request, pk):
    feuille_route = get_user_object_or_404(FeuilleDeRoute, request.user, pk=pk)
    return render(request, 'fleet_app/feuille_route_print.html', {'feuille_route': feuille_route})

# Vues pour les véhicules
class VehiculeListView(LoginRequiredMixin, ListView):
    model = Vehicule
    template_name = 'fleet_app/vehicule_list.html'
    context_object_name = 'vehicules'
    ordering = ['id_vehicule']
    paginate_by = 10
    
    def get_queryset(self):
        qs = Vehicule.objects.filter(user=self.request.user).order_by(*self.ordering)
        # Appliquer filtre de recherche s'il existe
        search = self.request.GET.get('search', '')
        if search:
            qs = qs.filter(
                Q(immatriculation__icontains=search) |
                Q(marque__icontains=search) |
                Q(modele__icontains=search)
            )
        # Filtre de période sur la date d'acquisition
        start_date, end_date = get_period_filter(self.request)
        if start_date:
            qs = qs.filter(date_acquisition__gte=start_date)
        if end_date:
            qs = qs.filter(date_acquisition__lte=end_date)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date, end_date = get_period_filter(self.request)
        context['period'] = self.request.GET.get('period', '')
        context['period_start'] = start_date
        context['period_end'] = end_date
        return context
from django.contrib import messages
from django.shortcuts import redirect

class VehiculeDetailView(LoginRequiredMixin, DetailView):
    model = Vehicule
    template_name = 'fleet_app/vehicule_detail.html'
    context_object_name = 'vehicule'
    pk_url_kwarg = 'id_vehicule'
    
    def get_queryset(self):
        return Vehicule.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        vehicule = self.get_object()
        # Filtres de période depuis la querystring
        start_date, end_date = get_period_filter(self.request)
        context['period_start'] = start_date
        context['period_end'] = end_date
        context['period'] = self.request.GET.get('period', '')

        # Documents administratifs
        try:
            documents_qs = DocumentAdministratif.objects.filter(vehicule=vehicule)
            if start_date:
                documents_qs = documents_qs.filter(date_emission__gte=start_date)
            if end_date:
                documents_qs = documents_qs.filter(date_emission__lte=end_date)
            context['documents'] = documents_qs.order_by('-date_emission')
            context['documents_error'] = False
        except Exception:
            context['documents'] = []
            context['documents_error'] = True

        # Formulaires d'ajout
        context['document_form'] = DocumentAdministratifForm(initial={'vehicule': vehicule})
        context['distance_form'] = DistanceForm(initial={'vehicule': vehicule})
        context['consommation_form'] = ConsommationCarburantForm(initial={'vehicule': vehicule})
        context['cout_form'] = CoutFonctionnementForm(initial={'vehicule': vehicule})
        context['alerte_form'] = AlerteForm(initial={'vehicule': vehicule})

        # Date du jour
        from datetime import date
        context['today'] = date.today()

        # Distances parcourues
        try:
            distances_qs = DistanceParcourue.objects.filter(vehicule=vehicule)
            if start_date:
                distances_qs = distances_qs.filter(date_debut__gte=start_date)
            if end_date:
                distances_qs = distances_qs.filter(date_fin__lte=end_date)
            context['distances'] = distances_qs.order_by('-date_debut')
            context['distances_error'] = False
        except Exception:
            context['distances'] = []
            context['distances_error'] = True

        # Consommation de carburant
        try:
            consommations_qs = ConsommationCarburant.objects.filter(vehicule=vehicule)
            if start_date:
                consommations_qs = consommations_qs.filter(date_plein1__gte=start_date)
            if end_date:
                consommations_qs = consommations_qs.filter(date_plein2__lte=end_date)
            context['consommations'] = consommations_qs.order_by('-date_plein1')
            context['consommations_error'] = False
        except Exception:
            context['consommations'] = []
            context['consommations_error'] = True

        # Coûts de fonctionnement
        try:
            couts_qs = CoutFonctionnement.objects.filter(vehicule=vehicule)
            if start_date:
                couts_qs = couts_qs.filter(date__gte=start_date)
            if end_date:
                couts_qs = couts_qs.filter(date__lte=end_date)
            context['couts_fonctionnement'] = couts_qs.order_by('-date')
            context['couts_fonctionnement_error'] = False
        except Exception:
            context['couts_fonctionnement'] = []
            context['couts_fonctionnement_error'] = True

        # Alertes
        try:
            # Statut choices in Alerte are 'Active', 'Résolue', 'Ignorée'
            alertes_qs = Alerte.objects.filter(vehicule=vehicule, statut='Active')
            if start_date:
                alertes_qs = alertes_qs.filter(date_creation__date__gte=start_date)
            if end_date:
                alertes_qs = alertes_qs.filter(date_creation__date__lte=end_date)
            context['alertes'] = alertes_qs.order_by('-date_creation')
            context['alertes_error'] = False
        except Exception:
            context['alertes'] = []
            context['alertes_error'] = True

        return context

    def post(self, request, *args, **kwargs):
        vehicule = self.get_object()
        # Important pour DetailView: assurer que self.object est défini pendant les requêtes POST
        # afin que super().get_context_data() puisse accéder à l'objet.
        self.object = vehicule
        
        # Déterminer quel formulaire a été soumis
        if 'add_document' in request.POST:
            form = DocumentAdministratifForm(request.POST, request.FILES)
            if form.is_valid():
                document = form.save(commit=False)
                document.vehicule = vehicule
                document.save()
                messages.success(request, 'Document administratif ajouté avec succès.')
                return redirect('fleet_app:vehicule_detail', id_vehicule=vehicule.id_vehicule)
            else:
                context = self.get_context_data()
                context['document_form'] = form
                messages.error(request, 'Erreur lors de l\'ajout du document administratif.')
                return self.render_to_response(context)
        
        elif 'add_distance' in request.POST:
            form = DistanceForm(request.POST)
            if form.is_valid():
                distance = form.save(commit=False)
                distance.vehicule = vehicule
                # Calculer automatiquement la distance parcourue
                if distance.km_fin and distance.km_debut:
                    distance.distance_parcourue = distance.km_fin - distance.km_debut
                distance.save()
                messages.success(request, 'Distance parcourue ajoutée avec succès.')
                return redirect('fleet_app:vehicule_detail', id_vehicule=vehicule.id_vehicule)
            else:
                context = self.get_context_data()
                context['distance_form'] = form
                messages.error(request, 'Erreur lors de l\'ajout de la distance parcourue.')
                return self.render_to_response(context)
        
        elif 'add_consommation' in request.POST:
            form = ConsommationCarburantForm(request.POST)
            if form.is_valid():
                consommation = form.save(commit=False)
                consommation.vehicule = vehicule
                # Calculer automatiquement la distance et la consommation
                if consommation.km_plein2 and consommation.km_plein1:
                    consommation.distance_parcourue = consommation.km_plein2 - consommation.km_plein1
                    if consommation.distance_parcourue > 0 and consommation.litres_ajoutes:
                        consommation.consommation_100km = (consommation.litres_ajoutes * 100) / consommation.distance_parcourue
                consommation.save()
                messages.success(request, 'Consommation de carburant ajoutée avec succès.')
                return redirect('fleet_app:vehicule_detail', id_vehicule=vehicule.id_vehicule)
            else:
                context = self.get_context_data()
                context['consommation_form'] = form
                messages.error(request, 'Erreur lors de l\'ajout de la consommation.')
                return self.render_to_response(context)
        
        elif 'add_cout' in request.POST:
            form = CoutFonctionnementForm(request.POST)
            if form.is_valid():
                cout = form.save(commit=False)
                cout.vehicule = vehicule
                # Calculer automatiquement le coût par km si possible
                if cout.montant and cout.kilometrage and cout.kilometrage > 0:
                    cout.cout_par_km = cout.montant / cout.kilometrage
                cout.save()
                messages.success(request, 'Coût de fonctionnement ajouté avec succès.')
                return redirect('fleet_app:vehicule_detail', id_vehicule=vehicule.id_vehicule)
            else:
                context = self.get_context_data()
                context['cout_form'] = form
                messages.error(request, 'Erreur lors de l\'ajout du coût.')
                return self.render_to_response(context)
        
        elif 'add_alerte' in request.POST:
            form = AlerteForm(request.POST)
            if form.is_valid():
                alerte = form.save(commit=False)
                alerte.vehicule = vehicule
                # Statut par défaut actif; le modèle a déjà default='Active'
                alerte.save()
                messages.success(request, 'Alerte créée avec succès.')
                return redirect('fleet_app:vehicule_detail', id_vehicule=vehicule.id_vehicule)
            else:
                context = self.get_context_data()
                context['alerte_form'] = form
                messages.error(request, 'Erreur lors de la création de l\'alerte.')
                return self.render_to_response(context)
        
        elif 'resolve_alerte' in request.POST:
            alerte_id = request.POST.get('alerte_id')
            try:
                alerte = Alerte.objects.get(pk=alerte_id, vehicule=vehicule)
                alerte.statut = 'Résolue'
                alerte.save()
                messages.success(request, 'Alerte marquée comme résolue.')
            except Alerte.DoesNotExist:
                messages.error(request, "Alerte introuvable pour ce véhicule.")
            return redirect('fleet_app:vehicule_detail', id_vehicule=vehicule.id_vehicule)

        elif 'ignore_alerte' in request.POST:
            alerte_id = request.POST.get('alerte_id')
            try:
                alerte = Alerte.objects.get(pk=alerte_id, vehicule=vehicule)
                alerte.statut = 'Ignorée'
                alerte.save()
                messages.success(request, 'Alerte ignorée.')
            except Alerte.DoesNotExist:
                messages.error(request, "Alerte introuvable pour ce véhicule.")
            return redirect('fleet_app:vehicule_detail', id_vehicule=vehicule.id_vehicule)
        
        # Si aucun formulaire reconnu, retourner une erreur
        messages.error(request, 'Action non reconnue.')
        return redirect('fleet_app:vehicule_detail', id_vehicule=vehicule.id_vehicule)

class VehiculeCreateView(LoginRequiredMixin, CreateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'fleet_app/vehicule_form.html'
    success_url = reverse_lazy('fleet_app:vehicule_list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Véhicule ajouté avec succès.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Debug: afficher les erreurs dans les messages pour diagnostic
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Erreur {field}: {error}")
        if form.non_field_errors():
            for error in form.non_field_errors():
                messages.error(self.request, f"Erreur générale: {error}")
        return super().form_invalid(form)

class VehiculeUpdateView(LoginRequiredMixin, UpdateView):
    model = Vehicule
    form_class = VehiculeForm
    template_name = 'fleet_app/vehicule_form.html'
    success_url = reverse_lazy('fleet_app:vehicule_list')
    pk_url_kwarg = 'id_vehicule'
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_queryset(self):
        return Vehicule.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Véhicule modifié avec succès.')
        return super().form_valid(form)

class VehiculeDeleteView(LoginRequiredMixin, DeleteView):
    model = Vehicule
    template_name = 'fleet_app/vehicule_confirm_delete.html'
    success_url = reverse_lazy('fleet_app:vehicule_list')
    pk_url_kwarg = 'id_vehicule'
    
    def get_queryset(self):
        return Vehicule.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        try:
            vehicule = self.get_object()
            
            # Utiliser une transaction pour garantir l'atomicité
            with transaction.atomic():
                from django.db import connection
                
                # 1. Désactiver temporairement les contraintes de clé étrangère (SQLite uniquement)
                from django.db import connection as _conn
                if _conn.vendor == 'sqlite':
                    with _conn.cursor() as cursor:
                        cursor.execute('PRAGMA foreign_keys = OFF;')
                        print("Contraintes de clé étrangère désactivées temporairement (SQLite)")
                
                # 2. Supprimer explicitement les enregistrements liés via l'API Django
                from fleet_app.models import (
                    DocumentAdministratif, DistanceParcourue, ConsommationCarburant,
                    DisponibiliteVehicule, UtilisationActif, CoutFonctionnement,
                    CoutFinancier, UtilisationVehicule, FeuilleDeRoute,
                    IncidentSecurite, Alerte
                )
                
                # Journaliser les suppressions pour débogage
                print(f"Suppression des enregistrements liés au véhicule {vehicule.pk}")
                
                # Supprimer les enregistrements liés dans chaque modèle
                DocumentAdministratif.objects.filter(vehicule=vehicule).delete()
                DistanceParcourue.objects.filter(vehicule=vehicule).delete()
                ConsommationCarburant.objects.filter(vehicule=vehicule).delete()
                DisponibiliteVehicule.objects.filter(vehicule=vehicule).delete()
                UtilisationActif.objects.filter(vehicule=vehicule).delete()
                CoutFonctionnement.objects.filter(vehicule=vehicule).delete()
                CoutFinancier.objects.filter(vehicule=vehicule).delete()
                UtilisationVehicule.objects.filter(vehicule=vehicule).delete()
                FeuilleDeRoute.objects.filter(vehicule=vehicule).delete()
                IncidentSecurite.objects.filter(vehicule=vehicule).delete()
                Alerte.objects.filter(vehicule=vehicule).delete()
                
                # 3. Supprimer le véhicule via l'ORM (compatible MySQL/PostgreSQL/SQLite)
                print(f"Suppression du véhicule {vehicule.pk} via l'ORM")
                vehicule.delete()
                
                # 4. Réactiver les contraintes de clé étrangère (SQLite uniquement)
                if _conn.vendor == 'sqlite':
                    with _conn.cursor() as cursor:
                        cursor.execute('PRAGMA foreign_keys = ON;')
                        print("Contraintes de clé étrangère réactivées (SQLite)")
                
                messages.success(self.request, 'Véhicule supprimé avec succès.')
                return redirect('fleet_app:vehicule_list')
                
        except Exception as e:
            messages.error(self.request, f'Erreur lors de la suppression du véhicule : {str(e)}')
            return redirect('fleet_app:vehicule_detail', id_vehicule=self.kwargs['id_vehicule'])

# Vues pour les KPI
@login_required
def kpi_distance(request):
    table_missing = False
    try:
        # Import ici pour capturer spécifiquement l'erreur de table manquante
        from django.db.utils import OperationalError
        
        try:
            # Filtres de période
            start_date, end_date = get_period_filter(request)

            # Récupérer toutes les distances et appliquer filtres, pagination et recherche
            distances_qs = DistanceParcourue.objects.filter(user=request.user)
            if start_date:
                distances_qs = distances_qs.filter(date_debut__gte=start_date)
            if end_date:
                distances_qs = distances_qs.filter(date_fin__lte=end_date)

            distances_list = distances_qs.order_by('-date_fin')
            
            # Champs sur lesquels effectuer la recherche
            search_fields = ['vehicule__marque', 'vehicule__modele', 'vehicule__immatriculation', 'conducteur', 'departement']
            
            # Appliquer pagination et recherche
            distances, search_query = paginate_and_search(request, distances_list, search_fields)
            
            # Données pour graphiques
            vehicules = Vehicule.objects.filter(user=request.user)
            labels = [f"{v.marque} {v.modele} ({v.immatriculation})" for v in vehicules]
            
            # Calcul des distances totales par véhicule
            data = []
            for v in vehicules:
                v_qs = DistanceParcourue.objects.filter(vehicule=v)
                if start_date:
                    v_qs = v_qs.filter(date_debut__gte=start_date)
                if end_date:
                    v_qs = v_qs.filter(date_fin__lte=end_date)
                total_distance = v_qs.aggregate(Sum('distance_parcourue'))
                data.append(total_distance['distance_parcourue__sum'] or 0)
            
        except OperationalError as e:
            if "no such table" in str(e).lower():
                table_missing = True
                messages.warning(request, "La table des distances parcourues n'existe pas encore. Veuillez exécuter les migrations pour créer cette table.")
                distances = []
                search_query = ""
                labels = []
                data = []
            else:
                raise
    except Exception as e:
        # Gérer l'erreur de table manquante ou autre erreur
        distances = []
        search_query = ""
        labels = []
        data = []
        messages.error(request, f"Erreur lors de l'accès aux données de distance: {str(e)}. La table n'existe peut-être pas encore.")
    
    form = None
    if request.method == 'POST':
        try:
            form = DistanceForm(request.POST)
            if form.is_valid():
                instance = form.save(commit=False)
                # Calculer automatiquement la distance parcourue si elle n'est pas fournie
                if not instance.distance_parcourue and instance.km_debut is not None and instance.km_fin is not None:
                    instance.distance_parcourue = max(0, instance.km_fin - instance.km_debut)
                
                # Définir la limite annuelle en fonction du type de moteur si elle n'est pas fournie
                if not instance.limite_annuelle and instance.vehicule:
                    if instance.vehicule.type_moteur == 'Diesel':
                        instance.limite_annuelle = 30000  # 30 000 km/an pour diesel
                    elif instance.vehicule.type_moteur == 'Essence':
                        instance.limite_annuelle = 15000  # 15 000 km/an pour essence
                    else:
                        instance.limite_annuelle = 10000  # 10 000 km/an pour autres
                
                instance.save()
                messages.success(request, 'Données de distance ajoutées avec succès.')
                return redirect('fleet_app:kpi_distance')
        except Exception as e:
            messages.error(request, f"Erreur lors de l'ajout des données de distance: {str(e)}. La table n'existe peut-être pas encore.")
            form = None
    else:
        try:
            form = DistanceForm()
        except Exception:
            form = None
            messages.warning(request, "Le formulaire de distance n'a pas pu être chargé. La table correspondante n'existe peut-être pas encore.")
    
    context = {
        'distances': distances if 'distances' in locals() else [],
        'labels': json.dumps(labels if 'labels' in locals() else []),
        'data': json.dumps(data if 'data' in locals() else []),
        'form': form,
        'search_query': search_query if 'search_query' in locals() else "",
        'table_missing': 'distances' not in locals() or not distances
    }
    
    return render(request, 'fleet_app/kpi_distance.html', context)

@login_required
def kpi_consommation(request):
    form = None
    consommations = []
    labels = []
    data = []
    table_missing = False
    
    try:
        # Filtres de période (appliqués au tableau et aux agrégats)
        start_date, end_date = get_period_filter(request)
        if request.method == 'POST':
            try:
                form = ConsommationCarburantForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'Données de consommation ajoutées avec succès.')
                    return redirect('fleet_app:kpi_consommation')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout des données de consommation: {str(e)}. La table n'existe peut-être pas encore.")
                form = None
        else:
            try:
                form = ConsommationCarburantForm()
            except Exception:
                form = None
                messages.warning(request, "Le formulaire de consommation n'a pas pu être chargé. La table correspondante n'existe peut-être pas encore.")
        
        conso_qs = ConsommationCarburant.objects.filter(user=request.user)
        if start_date:
            conso_qs = conso_qs.filter(date_plein1__gte=start_date)
        if end_date:
            conso_qs = conso_qs.filter(date_plein2__lte=end_date)
        consommations = conso_qs.order_by('-date_plein2')[:10]
        
        # Données pour graphiques
        vehicules = Vehicule.objects.filter(user=request.user)
        labels = [f"{v.marque} {v.modele} ({v.immatriculation})" for v in vehicules]
        
        # Calcul des consommations moyennes par véhicule (avec filtres)
        for v in vehicules:
            try:
                v_qs = ConsommationCarburant.objects.filter(vehicule=v)
                if start_date:
                    v_qs = v_qs.filter(date_plein1__gte=start_date)
                if end_date:
                    v_qs = v_qs.filter(date_plein2__lte=end_date)
                conso_avg = v_qs.aggregate(Avg('consommation_100km'))
                data.append(conso_avg['consommation_100km__avg'] or 0)
            except Exception:
                data.append(0)
    
    except Exception as e:
        # Gérer l'erreur de table manquante ou autre erreur
        messages.error(request, f"Erreur lors de l'accès aux données de consommation: {str(e)}. La table n'existe peut-être pas encore.")
        table_missing = True
    
    context = {
        'consommations': consommations,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'form': form,
        'table_missing': table_missing
    }
    
    return render(request, 'fleet_app/kpi_consommation.html', context)

@login_required
def kpi_disponibilite(request):
    form = None
    disponibilites = []
    labels = []
    data = []
    disponibilite_moyenne = 0
    vehicule_plus_disponible = None
    vehicule_moins_disponible = None
    table_missing = False
    
    try:
        # Gestion du formulaire d'ajout
        if request.method == 'POST':
            try:
                form = DisponibiliteForm(request.POST)
                if form.is_valid():
                    disponibilite = form.save(commit=False)
                    # Calcul automatique du pourcentage de disponibilité
                    if disponibilite.heures_totales > 0:
                        disponibilite.disponibilite_pourcentage = (disponibilite.heures_disponibles / disponibilite.heures_totales) * 100
                    else:
                        disponibilite.disponibilite_pourcentage = 0
                    disponibilite.save()
                    messages.success(request, 'Données de disponibilité ajoutées avec succès.')
                    return redirect('fleet_app:kpi_disponibilite')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout des données de disponibilité: {str(e)}. La table n'existe peut-être pas encore.")
                form = None
        else:
            try:
                form = DisponibiliteForm()
            except Exception:
                form = None
                messages.warning(request, "Le formulaire de disponibilité n'a pas pu être chargé. La table correspondante n'existe peut-être pas encore.")
        
        # Filtres de période
        start_date, end_date = get_period_filter(request)

        # Récupérer toutes les données de disponibilité pour le tableau
        dispo_qs = DisponibiliteVehicule.objects.filter(user=request.user)
        if start_date:
            dispo_qs = dispo_qs.filter(date_debut__gte=start_date)
        if end_date:
            dispo_qs = dispo_qs.filter(date_fin__lte=end_date)
        disponibilites_list = dispo_qs.order_by('-date_debut')
        
        # Pagination
        paginator = Paginator(disponibilites_list, 10)  # 10 éléments par page
        page = request.GET.get('page')
        try:
            disponibilites = paginator.page(page)
        except PageNotAnInteger:
            disponibilites = paginator.page(1)
        except EmptyPage:
            disponibilites = paginator.page(paginator.num_pages)
        
        # Données pour graphiques
        vehicules = Vehicule.objects.filter(user=request.user)
        
        # Calcul des disponibilités moyennes par véhicule (avec filtres)
        for v in vehicules:
            label = f"{v.marque} {v.modele} ({v.immatriculation})"
            labels.append(label)
            
            try:
                v_qs = DisponibiliteVehicule.objects.filter(vehicule=v)
                if start_date:
                    v_qs = v_qs.filter(date_debut__gte=start_date)
                if end_date:
                    v_qs = v_qs.filter(date_fin__lte=end_date)
                dispo_avg = v_qs.aggregate(Avg('disponibilite_pourcentage'))
                data.append(dispo_avg['disponibilite_pourcentage__avg'] or 0)
            except Exception:
                data.append(0)  # Valeur par défaut si la table n'existe pas
        
        # Calculer la disponibilité moyenne globale
        disponibilite_moyenne = sum(data) / len(data) if data else 0
        
        # Trouver le véhicule le plus et le moins disponible
        if data:
            max_index = data.index(max(data))
            min_index = data.index(min(data))
            vehicule_plus_disponible = labels[max_index]
            vehicule_moins_disponible = labels[min_index]
            
    except Exception as e:
        # Gérer l'erreur de table manquante ou autre erreur
        messages.error(request, f"Erreur lors de l'accès aux données de disponibilité: {str(e)}. La table n'existe peut-être pas encore.")
        table_missing = True
    
    return render(request, 'fleet_app/kpi_disponibilite.html', {
        'form': form,
        'disponibilites': disponibilites,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'disponibilite_moyenne': round(disponibilite_moyenne, 1),
        'vehicule_plus_disponible': vehicule_plus_disponible,
        'vehicule_moins_disponible': vehicule_moins_disponible,
        'edit_mode': False,
        'table_missing': table_missing
    })

@login_required
def disponibilite_edit(request, pk):
    try:
        disponibilite = get_object_or_404(DisponibiliteVehicule, pk=pk, vehicule__user=request.user)
        if request.method == 'POST':
            form = DisponibiliteForm(request.POST, instance=disponibilite)
            if form.is_valid():
                disponibilite = form.save(commit=False)
                # Calcul automatique du pourcentage de disponibilité
                if disponibilite.heures_totales > 0:
                    disponibilite.disponibilite_pourcentage = (disponibilite.heures_disponibles / disponibilite.heures_totales) * 100
                else:
                    disponibilite.disponibilite_pourcentage = 0
                disponibilite.save()
                messages.success(request, "La période de disponibilité a été modifiée avec succès.")
                return redirect('fleet_app:kpi_disponibilite')
        else:
            form = DisponibiliteForm(instance=disponibilite)
        
        context = {
            'form': form,
            'disponibilite': disponibilite,
            'title': 'Modifier une période de disponibilité',
        }
        return render(request, 'fleet_app/disponibilite_form.html', context)
    except:
        messages.error(request, f"La période de disponibilité avec l'ID {pk} n'existe pas ou a été supprimée.")
        return redirect('fleet_app:kpi_disponibilite')

@login_required
def disponibilite_delete(request, pk):
    try:
        disponibilite = get_object_or_404(DisponibiliteVehicule, pk=pk, vehicule__user=request.user)
        if request.method == 'POST':
            disponibilite.delete()
            messages.success(request, "La période de disponibilité a été supprimée avec succès.")
            return redirect('fleet_app:kpi_disponibilite')
        
        context = {
            'disponibilite': disponibilite,
        }
        return render(request, 'fleet_app/disponibilite_confirm_delete.html', context)
    except Exception as e:
        # Gérer l'erreur de table manquante ou autre erreur
        if isinstance(e, Http404):
            messages.error(request, f"La période de disponibilité avec l'ID {pk} n'existe pas ou a déjà été supprimée.")
        else:
            messages.error(request, f"Erreur lors de l'accès aux données de disponibilité: {str(e)}. La table n'existe peut-être pas encore.")
            table_missing = True
    
    context = {
        'vehicules_data': vehicules_data,
        'labels_mois': json.dumps(labels_mois),
        'datasets': json.dumps([{**ds, 'borderColor': f"#{hash(ds['label']) % 0xffffff:06x}"} for ds in datasets]),
        'derniers_releves': derniers_releves,
        'form': form,
        'table_missing': table_missing
    }
    
    return render(request, 'fleet_app/kpi_distance.html', context)
@login_required
@require_user_ownership(DistanceParcourue)
def distance_delete(request, pk):
    try:
        distance = get_user_object_or_404(DistanceParcourue, request.user, pk=pk)
        if request.method == 'POST':
            distance.delete()
            messages.success(request, "La distance parcourue a été supprimée avec succès.")
            return redirect('fleet_app:kpi_distance')
        
        context = {
            'distance': distance,
            'title': 'Supprimer une distance parcourue',
            'message': f"Voulez-vous vraiment supprimer cette distance parcourue pour le véhicule {distance.vehicule.marque} {distance.vehicule.modele} ({distance.vehicule.immatriculation}) ?",
            'cancel_url': 'fleet_app:kpi_distance',
        }
        return render(request, 'fleet_app/distance_confirm_delete.html', context)
    except Exception as e:
        messages.error(request, f"La distance parcourue avec l'ID {pk} n'existe pas ou a déjà été supprimée. Erreur: {str(e)}")
        return redirect('fleet_app:kpi_distance')

# Vues pour la gestion des consommations de carburant
@login_required
@require_user_ownership(ConsommationCarburant)
def consommation_edit(request, pk):
    try:
        consommation = get_user_object_or_404(ConsommationCarburant, request.user, pk=pk)
        if request.method == 'POST':
            form = ConsommationCarburantForm(request.POST, instance=consommation)
            if form.is_valid():
                form.save()
                messages.success(request, "La consommation de carburant a été modifiée avec succès.")
                return redirect('fleet_app:kpi_consommation')
        else:
            form = ConsommationCarburantForm(instance=consommation)
        
        # Récupérer toutes les données de consommation pour le tableau
        consommations_list = ConsommationCarburant.objects.filter(user=request.user).order_by('-date_plein2')
        
        # Pagination
        paginator = Paginator(consommations_list, 10)  # 10 éléments par page
        page = request.GET.get('page')
        try:
            consommations = paginator.page(page)
        except PageNotAnInteger:
            consommations = paginator.page(1)
        except EmptyPage:
            consommations = paginator.page(paginator.num_pages)
        
        # Récupérer les données agrégées pour le graphique
        consommations_graph = ConsommationCarburant.objects.values('vehicule').annotate(
            consommation_moyenne=Avg('consommation_100km')
        ).order_by('consommation_moyenne')
        
        # Enrichir les données avec les informations du véhicule
        for c in consommations_graph:
            vehicule = Vehicule.objects.get(id_vehicule=c['vehicule'])
            c['immatriculation'] = vehicule.immatriculation
            c['marque'] = vehicule.marque
            c['modele'] = vehicule.modele
            c['type_moteur'] = vehicule.type_moteur
            
            # Définir la cible selon le type de moteur
            if vehicule.type_moteur == 'Diesel':
                c['cible'] = 5.0  # 5 L/100km pour diesel
            elif vehicule.type_moteur == 'Essence':
                c['cible'] = 6.5  # 6.5 L/100km pour essence
            else:
                c['cible'] = 2.0  # 2 L/100km pour électrique/hybride
            
            # Calculer l'écart par rapport à la cible
            c['ecart'] = c['consommation_moyenne'] - c['cible']
            c['pourcentage_ecart'] = (c['ecart'] / c['cible']) * 100
        
        # Préparer les données pour le graphique
        labels = []
        data = []
        
        for c in consommations_graph:
            vehicule = Vehicule.objects.get(id_vehicule=c['vehicule'])
            label = f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})"
            labels.append(label)
            data.append(c['consommation_moyenne'])
        
        context = {
            'form': form,
            'consommation': consommation,
            'consommations': consommations,
            'consommations_graph': consommations_graph,
            'labels': json.dumps(labels),
            'data': json.dumps(data),
            'edit_mode': True,
            'title': 'Modifier une consommation de carburant',
        }
        return render(request, 'fleet_app/kpi_consommation.html', context)
    except Exception as e:
        messages.error(request, f"La consommation de carburant avec l'ID {pk} n'existe pas ou a été supprimée. Erreur: {str(e)}")
        return redirect('fleet_app:kpi_consommation')

@login_required
@require_user_ownership(ConsommationCarburant)
def consommation_delete(request, pk):
    try:
        consommation = get_user_object_or_404(ConsommationCarburant, request.user, pk=pk)
        if request.method == 'POST':
            consommation.delete()
            messages.success(request, "La consommation de carburant a été supprimée avec succès.")
            return redirect('fleet_app:kpi_consommation')
        
        context = {
            'consommation': consommation,
            'title': 'Supprimer une consommation de carburant',
            'message': f"Voulez-vous vraiment supprimer cette consommation de carburant pour le véhicule {consommation.vehicule.marque} {consommation.vehicule.modele} ({consommation.vehicule.immatriculation}) ?",
            'cancel_url': 'fleet_app:kpi_consommation',
        }
        return render(request, 'fleet_app/consommation_confirm_delete.html', context)
    except Exception as e:
        messages.error(request, f"La consommation de carburant avec l'ID {pk} n'existe pas ou a déjà été supprimée. Erreur: {str(e)}")
        return redirect('fleet_app:kpi_consommation')

# Vues pour la gestion des disponibilités de véhicules
@login_required
def disponibilite_edit(request, pk):
    try:
        disponibilite = get_object_or_404(DisponibiliteVehicule, pk=pk, vehicule__user=request.user)
        if request.method == 'POST':
            form = DisponibiliteForm(request.POST, instance=disponibilite)
            if form.is_valid():
                form.save()
                messages.success(request, "La période de disponibilité a été modifiée avec succès.")
                return redirect('fleet_app:kpi_disponibilite')
        else:
            form = DisponibiliteForm(instance=disponibilite)
        
        # Récupérer toutes les données de disponibilité pour le tableau
        disponibilites_list = DisponibiliteVehicule.objects.filter(user=request.user).order_by('-date_fin')
        
        # Pagination
        paginator = Paginator(disponibilites_list, 10)  # 10 éléments par page
        page = request.GET.get('page')
        try:
            disponibilites = paginator.page(page)
        except PageNotAnInteger:
            disponibilites = paginator.page(1)
        except EmptyPage:
            disponibilites = paginator.page(paginator.num_pages)
        
        # Récupérer les données agrégées pour le graphique
        disponibilites_graph = DisponibiliteVehicule.objects.values('vehicule').annotate(
            disponibilite_moyenne=Avg('disponibilite_pourcentage')
        ).order_by('-disponibilite_moyenne')
        
        # Enrichir les données avec les informations du véhicule
        for d in disponibilites_graph:
            vehicule = Vehicule.objects.get(id_vehicule=d['vehicule'])
            d['immatriculation'] = vehicule.immatriculation
            d['marque'] = vehicule.marque
            d['modele'] = vehicule.modele
        
        # Préparer les données pour le graphique
        labels = []
        data = []
        
        for d in disponibilites_graph:
            vehicule = Vehicule.objects.get(id_vehicule=d['vehicule'])
            label = f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})"
            labels.append(label)
            data.append(d['disponibilite_moyenne'])
        
        context = {
            'form': form,
            'disponibilite': disponibilite,
            'disponibilites': disponibilites,
            'disponibilites_graph': disponibilites_graph,
            'labels': json.dumps(labels),
            'data': json.dumps(data),
            'edit_mode': True,
            'title': 'Modifier une période de disponibilité',
        }
        return render(request, 'fleet_app/kpi_disponibilite.html', context)
    except Exception as e:
        messages.error(request, f"La période de disponibilité avec l'ID {pk} n'existe pas ou a été supprimée. Erreur: {str(e)}")
        return redirect('fleet_app:kpi_disponibilite')

@login_required
def disponibilite_delete(request, pk):
    try:
        disponibilite = get_object_or_404(DisponibiliteVehicule, pk=pk, vehicule__user=request.user)
        if request.method == 'POST':
            disponibilite.delete()
            messages.success(request, "La période de disponibilité a été supprimée avec succès.")
            return redirect('fleet_app:kpi_disponibilite')
        
        context = {
            'disponibilite': disponibilite,
            'title': 'Supprimer une période de disponibilité',
            'message': f"Voulez-vous vraiment supprimer cette période de disponibilité pour le véhicule {disponibilite.vehicule.marque} {disponibilite.vehicule.modele} ({disponibilite.vehicule.immatriculation}) ?",
            'cancel_url': 'fleet_app:kpi_disponibilite',
        }
        return render(request, 'fleet_app/disponibilite_confirm_delete.html', context)
    except Exception as e:
        messages.error(request, f"La période de disponibilité avec l'ID {pk} n'existe pas ou a déjà été supprimée. Erreur: {str(e)}")
        return redirect('fleet_app:kpi_disponibilite')

# Classes dupliquées supprimées - utiliser les versions sécurisées ci-dessus

@login_required
def feuille_route_create(request):
    if request.method == 'POST':
        form = FeuilleDeRouteForm(request.POST)
        if form.is_valid():
            feuille = form.save(commit=False)
            feuille.signature_gestionnaire = True  # Le gestionnaire signe en créant la feuille
            feuille.save()
            messages.success(request, "La feuille de route a été créée avec succès.")
            return redirect('fleet_app:feuille_route_list')
    else:
        form = FeuilleDeRouteForm()
        # Préremplir la date et l'heure actuelles
        from django.utils import timezone
        now = timezone.now()
        form.initial['date_depart'] = now.date()
        form.initial['heure_depart'] = now.time().strftime('%H:%M')
    
    context = {
        'form': form,
        'title': 'Nouvelle feuille de route'
    }
    return render(request, 'fleet_app/feuille_route_form.html', context)

@login_required
def feuille_route_update(request, pk):
    feuille = get_object_or_404(FeuilleDeRoute, pk=pk)
    if request.method == 'POST':
        form = FeuilleDeRouteUpdateForm(request.POST, instance=feuille)
        if form.is_valid():
            feuille = form.save(commit=False)
            feuille.signature_chauffeur = True  # Le chauffeur signe en mettant à jour les données de retour
            feuille.save()
            messages.success(request, "La feuille de route a été mise à jour avec succès.")
            return redirect('fleet_app:feuille_route_detail', pk=feuille.pk)
    else:
        form = FeuilleDeRouteUpdateForm(instance=feuille)
    
    context = {
        'form': form,
        'feuille_route': feuille,
        'title': 'Mettre à jour la feuille de route'
    }
    return render(request, 'fleet_app/feuille_route_update_form.html', context)

@login_required
def feuille_route_delete(request, pk):
    feuille = get_object_or_404(FeuilleDeRoute, pk=pk)
    if request.method == 'POST':
        feuille.delete()
        messages.success(request, "La feuille de route a été supprimée avec succès.")
        return redirect('fleet_app:feuille_route_list')
    
    context = {
        'feuille_route': feuille
    }
    return render(request, 'fleet_app/feuille_route_confirm_delete.html', context)

@login_required
def feuille_route_print(request, pk):
    feuille = get_object_or_404(FeuilleDeRoute, pk=pk)
    
    context = {
        'feuille_route': feuille,
        'print_mode': True
    }
    return render(request, 'fleet_app/feuille_route_print.html', context)

@login_required
def kpi_consommation(request):
    # Gestion du formulaire d'ajout
    if request.method == 'POST':
        form = ConsommationCarburantForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'La consommation de carburant a été ajoutée avec succès.')
            return redirect('fleet_app:kpi_consommation')
    else:
        form = ConsommationCarburantForm()
    
    # Récupérer toutes les données de consommation pour le tableau
    consommations_list = ConsommationCarburant.objects.filter(user=request.user).order_by('-date_plein2')
    
    # Pagination
    paginator = Paginator(consommations_list, 10)  # 10 éléments par page
    page = request.GET.get('page')
    try:
        consommations = paginator.page(page)
    except PageNotAnInteger:
        consommations = paginator.page(1)
    except EmptyPage:
        consommations = paginator.page(paginator.num_pages)
    
    # Récupérer les données agrégées pour le graphique
    consommations_graph = ConsommationCarburant.objects.values('vehicule').annotate(
        litres_total=Sum('litres_ajoutes'),
    ).order_by('vehicule')
    
    # Enrichir les données avec les informations du véhicule et calculer la consommation moyenne
    for c in consommations_graph:
        vehicule = Vehicule.objects.get(id_vehicule=c['vehicule'])
        c['immatriculation'] = vehicule.immatriculation
        c['marque'] = vehicule.marque
        c['modele'] = vehicule.modele
        c['categorie'] = vehicule.categorie
        c['type_moteur'] = vehicule.type_moteur
        
        # Récupérer la distance parcourue pour ce véhicule
        distance_totale = DistanceParcourue.objects.filter(vehicule=vehicule).aggregate(Sum('distance_parcourue'))['distance_parcourue__sum'] or 0
        
        # Éviter division par zéro
        if distance_totale > 0:
            # Calculer la consommation moyenne en L/100km
            c['consommation_moyenne'] = (c['litres_total'] * 100) / distance_totale
            
            # Définir la cible selon le type de moteur (valeurs fictives à adapter)
            if vehicule.type_moteur == 'Diesel':
                c['cible'] = 6.5  # L/100km pour diesel
            elif vehicule.type_moteur == 'Essence':
                c['cible'] = 7.5  # L/100km pour essence
            else:
                c['cible'] = 2.0  # L/100km pour hybride/électrique
            
            # Ajouter une marge de tolérance pour les terrains difficiles
            c['cible'] += 3.0  # +3 L/100km en terrain difficile
            
            # Calculer le dépassement par rapport à la cible
            c['depassement'] = c['consommation_moyenne'] - c['cible']
            
            # Définir si une alerte doit être déclenchée
            c['alerte'] = c['depassement'] > 2.0  # Alerte si dépassement > 2 L/100km
            
            # Créer ou mettre à jour une alerte automatique si nécessaire
            if c['alerte']:
                # Vérifier si une alerte active existe déjà pour ce véhicule et ce titre
                alerte_existante = Alerte.objects.filter(
                    vehicule=vehicule,
                    titre__startswith='Consommation excessive',
                    statut='Active'
                ).first()
                
                # Description de l'alerte
                description = (
                    f"La consommation du véhicule {vehicule.marque} {vehicule.modele} ({vehicule.immatriculation}) "
                    f"est de {c['consommation_moyenne']:.1f} L/100km, "
                    f"ce qui dépasse la cible recommandée de {c['cible']:.1f} L/100km de {c['depassement']:.1f} L/100km."
                )
                
                if alerte_existante:
                    # Mettre à jour l'alerte existante
                    alerte_existante.description = description
                    alerte_existante.save()
                else:
                    # Créer une nouvelle alerte
                    niveau = 'Critique' if c['depassement'] > 5.0 else 'Élevé' if c['depassement'] > 3.5 else 'Moyen'
                    Alerte.objects.create(
                        vehicule=vehicule,
                        titre="Consommation excessive de carburant",
                        description=description,
                        niveau=niveau,
                        statut='Active'
                    )
        else:
            c['consommation_moyenne'] = 0
            c['cible'] = 0
            c['depassement'] = 0
            c['alerte'] = False
    
    # Préparer les données pour le graphique
    labels = []
    data = []
    
    for c in consommations_graph:
        vehicule = Vehicule.objects.get(id_vehicule=c['vehicule'])
        label = f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})"
        labels.append(label)
        
        if 'consommation_moyenne' in c and c['consommation_moyenne'] > 0:
            data.append(round(c['consommation_moyenne'], 1))
        else:
            data.append(0)
    
    # Calculer les statistiques pour le template
    consommation_moyenne_globale = 0
    if sum(data) > 0 and len([d for d in data if d > 0]) > 0:
        consommation_moyenne_globale = sum(data) / len([d for d in data if d > 0])
    
    return render(request, 'fleet_app/kpi_consommation.html', {
        'form': form,
        'consommations': consommations,
        'consommations_graph': consommations_graph,
        'labels': labels,
        'data': data,
        'consommation_moyenne_globale': round(consommation_moyenne_globale, 1),
        'edit_mode': False
    })

@login_required
def consommation_edit(request, pk):
    """Vue pour modifier une consommation de carburant existante"""
    consommation = get_object_or_404(ConsommationCarburant, pk=pk)
    
    if request.method == 'POST':
        form = ConsommationCarburantForm(request.POST, instance=consommation)
        if form.is_valid():
            form.save()
            messages.success(request, 'La consommation de carburant a été modifiée avec succès.')
            return redirect('fleet_app:kpi_consommation')
    else:
        form = ConsommationCarburantForm(instance=consommation)
    
    return render(request, 'fleet_app/kpi_consommation.html', {
        'form': form,
        'consommations': ConsommationCarburant.objects.filter(user=request.user).order_by('-date_plein2'),
        'edit_mode': True,
        'consommation': consommation
    })

@login_required
def consommation_delete(request, pk):
    """Vue pour supprimer une consommation de carburant"""
    consommation = get_object_or_404(ConsommationCarburant, pk=pk)
    
    if request.method == 'POST':
        consommation.delete()
        messages.success(request, 'La consommation de carburant a été supprimée avec succès.')
        return redirect('fleet_app:kpi_consommation')
    
    return render(request, 'fleet_app/confirm_delete.html', {
        'object': consommation,
        'object_name': f'Consommation du {consommation.date_plein2} pour {consommation.vehicule}',
        'cancel_url': 'fleet_app:kpi_consommation'
    })

@login_required
def kpi_disponibilite(request):
    # Initialiser les variables
    disponibilites = []
    disponibilites_graph = []
    labels = []
    data = []
    disponibilite_moyenne = 0
    vehicule_plus_disponible = None
    vehicule_moins_disponible = None
    form = None
    table_missing = False
    
    try:
        # Gestion du formulaire d'ajout
        if request.method == 'POST':
            try:
                form = DisponibiliteForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, 'La période de disponibilité a été ajoutée avec succès.')
                    return redirect('fleet_app:kpi_disponibilite')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout des données de disponibilité: {str(e)}. La table n'existe peut-être pas encore.")
                form = None
        else:
            try:
                form = DisponibiliteForm()
            except Exception:
                form = None
                messages.warning(request, "Le formulaire de disponibilité n'a pas pu être chargé. La table correspondante n'existe peut-être pas encore.")
        
        # Récupérer toutes les données de disponibilité pour le tableau
        disponibilites_list = DisponibiliteVehicule.objects.filter(user=request.user).order_by('-date_fin')
        
        # Pagination
        paginator = Paginator(disponibilites_list, 10)  # 10 éléments par page
        page = request.GET.get('page')
        try:
            disponibilites = paginator.page(page)
        except PageNotAnInteger:
            disponibilites = paginator.page(1)
        except EmptyPage:
            disponibilites = paginator.page(paginator.num_pages)
        
        # Récupérer les données agrégées pour le graphique
        disponibilites_graph = DisponibiliteVehicule.objects.values('vehicule').annotate(
            disponibilite_moyenne=Avg('disponibilite_pourcentage')
        ).order_by('-disponibilite_moyenne')
        
        # Enrichir les données avec les informations du véhicule
        for d in disponibilites_graph:
            try:
                vehicule = Vehicule.objects.get(id_vehicule=d['vehicule'])
                d['immatriculation'] = vehicule.immatriculation
                d['marque'] = vehicule.marque
                d['modele'] = vehicule.modele
            except Exception:
                # Erreur lors de la récupération du véhicule
                pass
        
        # Préparer les données pour le graphique
        labels = []
        data = []
        
        for d in disponibilites_graph:
            if 'marque' in d and 'modele' in d and 'immatriculation' in d:
                label = f"{d['marque']} {d['modele']} ({d['immatriculation']})"
                labels.append(label)
                data.append(float(d['disponibilite_moyenne']))
            
        # Ajouter des données factices si aucune donnée n'est disponible
        if not labels:
            # Récupérer tous les véhicules pour créer des données factices
            vehicules = Vehicule.objects.filter(user=request.user)[:5]  # Limiter à 5 véhicules
            for v in vehicules:
                labels.append(f"{v.marque} {v.modele} ({v.immatriculation})")
                # Générer une valeur aléatoire entre 50 et 100
                import random
                data.append(random.uniform(50, 100))
        
        # Calculer la disponibilité moyenne globale
        if disponibilites_list.exists():
            disponibilite_moyenne = disponibilites_list.aggregate(Avg('disponibilite_pourcentage'))['disponibilite_pourcentage__avg'] or 0
        
        # Trouver les véhicules les plus et moins disponibles
        if disponibilites_graph:
            filtered_graph = [d for d in disponibilites_graph if 'marque' in d and 'modele' in d and 'immatriculation' in d]
            if filtered_graph:
                max_dispo = max(filtered_graph, key=lambda x: x['disponibilite_moyenne'])
                min_dispo = min(filtered_graph, key=lambda x: x['disponibilite_moyenne'])
                vehicule_plus_disponible = f"{max_dispo['marque']} {max_dispo['modele']} ({max_dispo['immatriculation']})"
                vehicule_moins_disponible = f"{min_dispo['marque']} {min_dispo['modele']} ({min_dispo['immatriculation']})"
    
    except Exception as e:
        # Gérer l'erreur de table manquante ou autre erreur
        messages.error(request, f"Erreur lors de l'accès aux données de disponibilité: {str(e)}. La table n'existe peut-être pas encore.")
        table_missing = True
    
    return render(request, 'fleet_app/kpi_disponibilite.html', {
        'form': form,
        'disponibilites': disponibilites,
        'disponibilites_graph': disponibilites_graph,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'edit_mode': False,
        'disponibilite_moyenne': disponibilite_moyenne,
        'vehicule_plus_disponible': vehicule_plus_disponible,
        'vehicule_moins_disponible': vehicule_moins_disponible,
        'table_missing': table_missing
    })

@login_required
def kpi_incidents(request):
    # Récupérer tous les incidents groupés par véhicule
    incidents_par_vehicule = Incident.objects.values('vehicule').annotate(total_incidents=Count('id')).order_by('-total_incidents')
    
    # Enrichir les données avec les informations du véhicule
    for incident in incidents_par_vehicule:
        vehicule = Vehicule.objects.get(id_vehicule=incident['vehicule'])
        incident['immatriculation'] = vehicule.immatriculation
        incident['marque'] = vehicule.marque
        incident['modele'] = vehicule.modele
        incident['categorie'] = vehicule.categorie
        incident['type_moteur'] = vehicule.type_moteur
        
        # Définir si une alerte doit être déclenchée
        incident['alerte'] = incident['total_incidents'] > 1  # Alerte si plus d'un incident
        
        # Récupérer les détails des incidents pour ce véhicule
        incident['details'] = list(Incident.objects.filter(vehicule=vehicule).values('date_incident', 'description', 'gravite'))
    
    # Ajouter les véhicules sans incident
    vehicules_avec_incidents = [i['vehicule'] for i in incidents_par_vehicule]
    vehicules_sans_incident = Vehicule.objects.exclude(id_vehicule__in=vehicules_avec_incidents)
    
    for vehicule in vehicules_sans_incident:
        incident_info = {
            'vehicule': vehicule.id_vehicule,
            'immatriculation': vehicule.immatriculation,
            'marque': vehicule.marque,
            'modele': vehicule.modele,
            'categorie': vehicule.categorie,
            'type_moteur': vehicule.type_moteur,
            'total_incidents': 0,
            'alerte': False,
            'details': []
        }
        incidents_par_vehicule = list(incidents_par_vehicule)
        incidents_par_vehicule.append(incident_info)
    
    context = {
        'incidents': incidents_par_vehicule,
        'titre': 'KPI - Sécurité',
        'description': 'Analyse détaillée des incidents et accidents par véhicule'
    }
    
    return render(request, 'fleet_app/kpi_detail.html', context)

# --- Exports CSV pour KPI ---
@login_required
def export_kpi_distance_csv(request):
    """Export CSV des distances par véhicule."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="kpi_distances.csv"'

    writer = csv.writer(response)
    writer.writerow(['Véhicule', 'Date début', 'Date fin', 'Km début', 'Km fin', 'Distance parcourue (km)'])

    # Filtres de période
    start_date, end_date = get_period_filter(request)
    qs = DistanceParcourue.objects.select_related('vehicule')
    if start_date:
        qs = qs.filter(date_debut__gte=start_date)
    if end_date:
        qs = qs.filter(date_fin__lte=end_date)
    for d in qs.order_by('-date_fin'):
        v = d.vehicule
        writer.writerow([
            f"{v.marque} {v.modele} ({v.immatriculation})",
            d.date_debut, d.date_fin,
            d.km_debut, d.km_fin, d.distance_parcourue
        ])

    return response

@login_required
def export_kpi_consommation_csv(request):
    """Export CSV des consommations de carburant."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="kpi_consommation.csv"'

    writer = csv.writer(response)
    writer.writerow(['Véhicule', 'Date plein 1', 'Km plein 1', 'Date plein 2', 'Km plein 2', 'Litres ajoutés', 'Distance (km)', 'Conso (L/100km)'])

    # Filtres de période
    start_date, end_date = get_period_filter(request)
    qs = ConsommationCarburant.objects.select_related('vehicule')
    if start_date:
        qs = qs.filter(date_plein1__gte=start_date)
    if end_date:
        qs = qs.filter(date_plein2__lte=end_date)
    qs = qs.order_by('-date_plein2')
    for c in qs:
        v = c.vehicule
        writer.writerow([
            f"{v.marque} {v.modele} ({v.immatriculation})",
            c.date_plein1, c.km_plein1,
            c.date_plein2, c.km_plein2,
            c.litres_ajoutes,
            c.distance_parcourue,
            c.consommation_100km
        ])

    return response

@login_required
def export_kpi_disponibilite_csv(request):
    """Export CSV des disponibilités."""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="kpi_disponibilite.csv"'

    writer = csv.writer(response)
    writer.writerow(['Véhicule', 'Date début', 'Date fin', 'Heures disponibles', 'Heures totales', 'Disponibilité (%)', "Raison d'indisponibilité"]) 

    # Filtres de période
    start_date, end_date = get_period_filter(request)
    qs = DisponibiliteVehicule.objects.select_related('vehicule')
    if start_date:
        qs = qs.filter(date_debut__gte=start_date)
    if end_date:
        qs = qs.filter(date_fin__lte=end_date)
    qs = qs.order_by('-date_fin')
    for d in qs:
        v = d.vehicule
        writer.writerow([
            f"{v.marque} {v.modele} ({v.immatriculation})",
            d.date_debut, d.date_fin,
            d.heures_disponibles, d.heures_totales, d.disponibilite_pourcentage,
            d.raison_indisponibilite
        ])

    return response

# --- Exports PDF pour KPI ---
def _calendar_ranges(now=None):
    """Retourne les bornes calendaires (début du mois, trimestre, année) jusqu'à maintenant.
    Format: {'month': (start, end), 'quarter': (start, end), 'year': (start, end)}
    """
    if now is None:
        now = timezone.now()
    # Début du mois
    month_start = now.replace(day=1).date()
    # Début du trimestre calendaire
    q_month = ((now.month - 1) // 3) * 3 + 1
    quarter_start = date(year=now.year, month=q_month, day=1)
    # Début de l'année
    year_start = date(year=now.year, month=1, day=1)
    end = now.date()
    return {
        'month': (month_start, end),
        'quarter': (quarter_start, end),
        'year': (year_start, end),
    }
@login_required
def export_kpi_distance_pdf(request):
    start_date, end_date = get_period_filter(request)
    qs = DistanceParcourue.objects.select_related('vehicule')
    if start_date:
        qs = qs.filter(date_debut__gte=start_date)
    if end_date:
        qs = qs.filter(date_fin__lte=end_date)
    qs = qs.order_by('-date_fin')
    total_distance = qs.aggregate(Sum('distance_parcourue'))['distance_parcourue__sum'] or 0
    count = qs.count()
    # Résumé global calendaire (M/T/A)
    cal = _calendar_ranges()
    global_summary = {}
    for key, (s, e) in cal.items():
        qf = DistanceParcourue.objects.select_related('vehicule').filter(date_debut__gte=s, date_fin__lte=e)
        global_summary[key] = {
            'total_distance': qf.aggregate(Sum('distance_parcourue'))['distance_parcourue__sum'] or 0,
            'rows_count': qf.count(),
        }
    context = {
        'rows': qs,
        'generated_at': timezone.now(),
        'period': request.GET.get('period', ''),
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
        'summary': {
            'total_distance': total_distance,
            'rows_count': count,
        },
        'global_summary': global_summary,
    }
    return render_to_pdf('fleet_app/pdf/kpi_distance_pdf.html', context, 'kpi_distance.pdf')

@login_required
def export_kpi_consommation_pdf(request):
    start_date, end_date = get_period_filter(request)
    qs = ConsommationCarburant.objects.select_related('vehicule')
    if start_date:
        qs = qs.filter(date_plein1__gte=start_date)
    if end_date:
        qs = qs.filter(date_plein2__lte=end_date)
    qs = qs.order_by('-date_plein2')
    sums = qs.aggregate(
        total_litres=Sum('litres_ajoutes'),
        total_distance=Sum('distance_parcourue'),
        avg_conso=Avg('consommation_100km'),
    )
    cal = _calendar_ranges()
    global_summary = {}
    for key, (s, e) in cal.items():
        qf = ConsommationCarburant.objects.select_related('vehicule').filter(date_plein1__gte=s, date_plein2__lte=e)
        ag = qf.aggregate(total_litres=Sum('litres_ajoutes'), total_distance=Sum('distance_parcourue'), avg_conso=Avg('consommation_100km'))
        global_summary[key] = {
            'total_litres': ag.get('total_litres') or 0,
            'total_distance': ag.get('total_distance') or 0,
            'avg_conso': ag.get('avg_conso') or 0,
            'rows_count': qf.count(),
        }
    context = {
        'rows': qs,
        'generated_at': timezone.now(),
        'period': request.GET.get('period', ''),
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
        'summary': {
            'total_litres': sums.get('total_litres') or 0,
            'total_distance': sums.get('total_distance') or 0,
            'avg_conso': sums.get('avg_conso') or 0,
            'rows_count': qs.count(),
        },
        'global_summary': global_summary,
    }
    return render_to_pdf('fleet_app/pdf/kpi_consommation_pdf.html', context, 'kpi_consommation.pdf')

@login_required
def export_kpi_disponibilite_pdf(request):
    start_date, end_date = get_period_filter(request)
    qs = DisponibiliteVehicule.objects.select_related('vehicule')
    if start_date:
        qs = qs.filter(date_debut__gte=start_date)
    if end_date:
        qs = qs.filter(date_fin__lte=end_date)
    qs = qs.order_by('-date_fin')
    sums = qs.aggregate(
        total_heures_disponibles=Sum('heures_disponibles'),
        total_heures_totales=Sum('heures_totales'),
        avg_disponibilite=Avg('disponibilite_pourcentage'),
    )
    cal = _calendar_ranges()
    global_summary = {}
    for key, (s, e) in cal.items():
        qf = DisponibiliteVehicule.objects.select_related('vehicule').filter(date_debut__gte=s, date_fin__lte=e)
        ag = qf.aggregate(total_heures_disponibles=Sum('heures_disponibles'), total_heures_totales=Sum('heures_totales'), avg_disponibilite=Avg('disponibilite_pourcentage'))
        global_summary[key] = {
            'total_heures_disponibles': ag.get('total_heures_disponibles') or 0,
            'total_heures_totales': ag.get('total_heures_totales') or 0,
            'avg_disponibilite': ag.get('avg_disponibilite') or 0,
            'rows_count': qf.count(),
        }
    context = {
        'rows': qs,
        'generated_at': timezone.now(),
        'period': request.GET.get('period', ''),
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
        'summary': {
            'total_heures_disponibles': sums.get('total_heures_disponibles') or 0,
            'total_heures_totales': sums.get('total_heures_totales') or 0,
            'avg_disponibilite': sums.get('avg_disponibilite') or 0,
            'rows_count': qs.count(),
        },
        'global_summary': global_summary,
    }
    return render_to_pdf('fleet_app/pdf/kpi_disponibilite_pdf.html', context, 'kpi_disponibilite.pdf')

@login_required
def export_kpi_couts_fonctionnement_pdf(request):
    # Calcul simple par véhicule: coût total et coût moyen/km
    start_date, end_date = get_period_filter(request)
    couts = CoutFonctionnement.objects.filter(user=request.user)
    if start_date:
        couts = couts.filter(date__gte=start_date)
    if end_date:
        couts = couts.filter(date__lte=end_date)
    agg = couts.values('vehicule').annotate(cout_total=Sum('montant')).order_by('vehicule')
    rows = []
    for c in agg:
        try:
            v = Vehicule.objects.get(id_vehicule=c['vehicule'])
        except Vehicule.DoesNotExist:
            continue
        distance_totale = DistanceParcourue.objects.filter(vehicule=v)
        if start_date:
            distance_totale = distance_totale.filter(date_debut__gte=start_date)
        if end_date:
            distance_totale = distance_totale.filter(date_fin__lte=end_date)
        distance_totale = distance_totale.aggregate(Sum('distance_parcourue'))['distance_parcourue__sum'] or 0
        cout_total = c['cout_total'] or 0
        cout_moyen_par_km = cout_total / distance_totale if distance_totale else 0
        rows.append({
            'vehicule': v,
            'cout_total': cout_total,
            'distance_totale': distance_totale,
            'cout_moyen_par_km': cout_moyen_par_km,
        })
    total_cout = sum(r['cout_total'] for r in rows)
    total_km = sum(r['distance_totale'] for r in rows)
    avg_cout_km = (total_cout / total_km) if total_km else 0
    cal = _calendar_ranges()
    global_summary = {}
    for key, (s, e) in cal.items():
        qcf = CoutFonctionnement.objects.filter(date__gte=s, date__lte=e)
        ag_cout = qcf.aggregate(total_cout=Sum('montant'))
        # Distance globale sur la même fenêtre
        qd = DistanceParcourue.objects.filter(date_debut__gte=s, date_fin__lte=e)
        total_km_g = qd.aggregate(total_km=Sum('distance_parcourue'))['total_km'] or 0
        total_cout_g = ag_cout.get('total_cout') or 0
        global_summary[key] = {
            'total_cout': total_cout_g,
            'total_km': total_km_g,
            'avg_cout_km': (total_cout_g / total_km_g) if total_km_g else 0,
        }
    context = {
        'rows': rows,
        'generated_at': timezone.now(),
        'period': request.GET.get('period', ''),
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
        'summary': {
            'total_cout': total_cout,
            'total_km': total_km,
            'avg_cout_km': avg_cout_km,
            'rows_count': len(rows),
        },
        'global_summary': global_summary,
    }
    return render_to_pdf('fleet_app/pdf/kpi_couts_fonctionnement_pdf.html', context, 'kpi_couts_fonctionnement.pdf')

@login_required
def export_kpi_incidents_pdf(request):
    start_date, end_date = get_period_filter(request)
    qs = IncidentSecurite.objects.select_related('vehicule')
    if start_date:
        qs = qs.filter(date_incident__gte=start_date)
    if end_date:
        qs = qs.filter(date_incident__lte=end_date)
    qs = qs.order_by('-date_incident')
    # Aggregation par véhicule pour un tableau synthétique
    agg = qs.values('vehicule').annotate(total=Count('id')).order_by('-total')
    rows = []
    for a in agg:
        try:
            v = Vehicule.objects.get(id_vehicule=a['vehicule'])
        except Vehicule.DoesNotExist:
            continue
        rows.append({'vehicule': v, 'total_incidents': a['total']})
    total_incidents = sum(r['total_incidents'] for r in rows)
    cal = _calendar_ranges()
    global_summary = {}
    for key, (s, e) in cal.items():
        qf = IncidentSecurite.objects.select_related('vehicule').filter(date_incident__gte=s, date_incident__lte=e)
        global_summary[key] = {
            'total_incidents': qf.count(),
        }
    context = {
        'rows': rows,
        'generated_at': timezone.now(),
        'period': request.GET.get('period', ''),
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
        'summary': {
            'total_incidents': total_incidents,
            'vehicules_concernes': len(rows),
        },
        'global_summary': global_summary,
    }
    return render_to_pdf('fleet_app/pdf/kpi_incidents_pdf.html', context, 'kpi_incidents.pdf')

@login_required
def export_kpi_utilisation_pdf(request):
    start_date, end_date = get_period_filter(request)
    qs = UtilisationActif.objects.select_related('vehicule')
    if start_date:
        qs = qs.filter(date_debut__gte=start_date)
    if end_date:
        qs = qs.filter(date_fin__lte=end_date)
    qs = qs.order_by('-date_fin')
    # Calcul du taux d'utilisation par enregistrement
    rows = []
    for u in qs:
        taux = 0
        try:
            if u.jours_disponibles and u.jours_disponibles > 0:
                taux = (u.jours_utilises / u.jours_disponibles) * 100
        except Exception:
            taux = 0
        rows.append({'obj': u, 'taux': taux})
    total_jours_utilises = sum((r['obj'].jours_utilises or 0) for r in rows)
    total_jours_disponibles = sum((r['obj'].jours_disponibles or 0) for r in rows)
    avg_taux = (total_jours_utilises / total_jours_disponibles * 100) if total_jours_disponibles else 0
    cal = _calendar_ranges()
    global_summary = {}
    for key, (s, e) in cal.items():
        qf = UtilisationActif.objects.select_related('vehicule').filter(date_debut__gte=s, date_fin__lte=e)
        # Taux moyen global sur la fenêtre
        total_u = qf.aggregate(Sum('jours_utilises'))['jours_utilises__sum'] or 0
        total_d = qf.aggregate(Sum('jours_disponibles'))['jours_disponibles__sum'] or 0
        avg_taux_g = (total_u / total_d * 100) if total_d else 0
        global_summary[key] = {
            'total_jours_utilises': total_u,
            'total_jours_disponibles': total_d,
            'avg_taux': avg_taux_g,
        }
    context = {
        'rows': rows,
        'generated_at': timezone.now(),
        'period': request.GET.get('period', ''),
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
        'summary': {
            'total_jours_utilises': total_jours_utilises,
            'total_jours_disponibles': total_jours_disponibles,
            'avg_taux': avg_taux,
            'rows_count': len(rows),
        },
        'global_summary': global_summary,
    }
    return render_to_pdf('fleet_app/pdf/kpi_utilisation_pdf.html', context, 'kpi_utilisation.pdf')

@login_required
def export_kpi_couts_financiers_pdf(request):
    start_date, end_date = get_period_filter(request)
    qs = CoutFinancier.objects.select_related('vehicule')
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)
    qs = qs.order_by('-date')
    # Agrégation par véhicule (total GNF) pour un tableau synthétique
    agg = qs.values('vehicule').annotate(cout_total=Sum('montant')).order_by('-cout_total')
    rows = []
    for a in agg:
        try:
            v = Vehicule.objects.get(id_vehicule=a['vehicule'])
        except Vehicule.DoesNotExist:
            continue
        rows.append({'vehicule': v, 'cout_total': a['cout_total'] or 0})
    total_cout = sum(r['cout_total'] for r in rows)
    cal = _calendar_ranges()
    global_summary = {}
    for key, (s, e) in cal.items():
        qf = CoutFinancier.objects.select_related('vehicule').filter(date__gte=s, date__lte=e)
        total = qf.aggregate(Sum('montant'))['montant__sum'] or 0
        global_summary[key] = {
            'total_cout': total,
        }
    context = {
        'rows': rows,
        'generated_at': timezone.now(),
        'period': request.GET.get('period', ''),
        'start': request.GET.get('start', ''),
        'end': request.GET.get('end', ''),
        'summary': {
            'total_cout': total_cout,
            'rows_count': len(rows),
        },
        'global_summary': global_summary,
    }
    return render_to_pdf('fleet_app/pdf/kpi_couts_financiers_pdf.html', context, 'kpi_couts_financiers.pdf')

from .utils import convertir_en_gnf, formater_montant_gnf, formater_cout_par_km_gnf
from django.http import JsonResponse

# --- API pour récupérer le dernier kilométrage d'un véhicule ---
@login_required
def get_vehicule_last_km(request, id_vehicule):
    """API pour récupérer le dernier kilométrage enregistré d'un véhicule"""
    try:
        vehicule = get_object_or_404(Vehicule, id_vehicule=id_vehicule, user=request.user)
        derniere_distance = DistanceParcourue.objects.filter(
            vehicule=vehicule
        ).order_by('-date_fin').first()
        
        if derniere_distance:
            return JsonResponse({
                'success': True,
                'last_km': derniere_distance.km_fin,
                'date': derniere_distance.date_fin.strftime('%Y-%m-%d')
            })
        else:
            return JsonResponse({
                'success': True,
                'last_km': 0,
                'date': None
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

# --- Exports CSV spécifiques à un véhicule ---
@login_required
def export_vehicule_documents_csv(request, id_vehicule):
    vehicule = get_object_or_404(Vehicule, id_vehicule=id_vehicule)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="documents_{vehicule.immatriculation}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Véhicule', 'Type', 'Numéro', "Date d'émission", "Date d'expiration", 'Statut'])
    start_date, end_date = get_period_filter(request)
    qs = DocumentAdministratif.objects.filter(vehicule=vehicule)
    if start_date:
        qs = qs.filter(date_emission__gte=start_date)
    if end_date:
        qs = qs.filter(date_emission__lte=end_date)
    qs = qs.order_by('-date_emission')
    for d in qs:
        statut = 'Valide'
        try:
            if d.date_expiration and d.date_expiration < timezone.now().date():
                statut = 'Expiré'
        except Exception:
            pass
        writer.writerow([f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})", d.type_document, d.numero, d.date_emission, d.date_expiration, statut])
    return response

@login_required
def export_vehicule_distances_csv(request, id_vehicule):
    vehicule = get_object_or_404(Vehicule, id_vehicule=id_vehicule)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="distances_{vehicule.immatriculation}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Véhicule', 'Date début', 'Date fin', 'Km début', 'Km fin', 'Distance (km)'])
    start_date, end_date = get_period_filter(request)
    qs = DistanceParcourue.objects.filter(vehicule=vehicule)
    if start_date:
        qs = qs.filter(date_debut__gte=start_date)
    if end_date:
        qs = qs.filter(date_fin__lte=end_date)
    qs = qs.order_by('-date_fin')
    for d in qs:
        writer.writerow([f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})", d.date_debut, d.date_fin, d.km_debut, d.km_fin, d.distance_parcourue])
    return response

@login_required
def export_vehicule_consommations_csv(request, id_vehicule):
    vehicule = get_object_or_404(Vehicule, id_vehicule=id_vehicule)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="consommations_{vehicule.immatriculation}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Véhicule', 'Date plein 1', 'Km plein 1', 'Date plein 2', 'Km plein 2', 'Litres ajoutés', 'Distance (km)', 'Conso (L/100km)'])
    start_date, end_date = get_period_filter(request)
    qs = ConsommationCarburant.objects.filter(vehicule=vehicule)
    if start_date:
        qs = qs.filter(date_plein1__gte=start_date)
    if end_date:
        qs = qs.filter(date_plein2__lte=end_date)
    qs = qs.order_by('-date_plein2')
    for c in qs:
        writer.writerow([f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})", c.date_plein1, c.km_plein1, c.date_plein2, c.km_plein2, c.litres_ajoutes, c.distance_parcourue, c.consommation_100km])
    return response

@login_required
def export_vehicule_couts_csv(request, id_vehicule):
    vehicule = get_object_or_404(Vehicule, id_vehicule=id_vehicule)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="couts_{vehicule.immatriculation}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Véhicule', 'Date', 'Type', 'Montant', 'Kilométrage', 'Coût/km'])
    start_date, end_date = get_period_filter(request)
    qs = CoutFonctionnement.objects.filter(vehicule=vehicule)
    if start_date:
        qs = qs.filter(date__gte=start_date)
    if end_date:
        qs = qs.filter(date__lte=end_date)
    qs = qs.order_by('-date')
    for c in qs:
        writer.writerow([f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})", c.date, c.type_cout, c.montant, getattr(c, 'kilometrage', ''), getattr(c, 'cout_par_km', '')])
    return response

@login_required
def export_vehicule_alertes_csv(request, id_vehicule):
    vehicule = get_object_or_404(Vehicule, id_vehicule=id_vehicule)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="alertes_{vehicule.immatriculation}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Véhicule', 'Date création', 'Type alerte', 'Description', 'Niveau', 'Statut'])
    start_date, end_date = get_period_filter(request)
    qs = Alerte.objects.filter(vehicule=vehicule)
    if start_date:
        qs = qs.filter(date_creation__date__gte=start_date)
    if end_date:
        qs = qs.filter(date_creation__date__lte=end_date)
    qs = qs.order_by('-date_creation')
    for a in qs:
        writer.writerow([f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})", a.date_creation, a.type_alerte, a.description, getattr(a, 'niveau_urgence', ''), a.statut])
    return response

@login_required
def kpi_couts_fonctionnement(request):
    try:
        # Récupérer tous les coûts de fonctionnement par véhicule
        couts = CoutFonctionnement.objects.values('vehicule').annotate(
            cout_total=Sum('montant')
        ).order_by('vehicule')
        
        # Enrichir les données avec les informations du véhicule et calculer le coût par km
        for c in couts:
            try:
                vehicule = Vehicule.objects.get(id_vehicule=c['vehicule'])
                c['immatriculation'] = vehicule.immatriculation
                c['marque'] = vehicule.marque
                c['modele'] = vehicule.modele
                c['categorie'] = vehicule.categorie
                c['type_moteur'] = vehicule.type_moteur
                
                # Convertir le coût total en GNF
                c['cout_total_eur'] = c['cout_total']
                c['cout_total'] = convertir_en_gnf(c['cout_total'])
                c['cout_total_formatte'] = formater_montant_gnf(c['cout_total'])
                
                try:
                    # Récupérer la distance parcourue pour ce véhicule
                    distance_totale = DistanceParcourue.objects.filter(vehicule=vehicule).aggregate(Sum('distance_parcourue'))['distance_parcourue__sum'] or 0
                except Exception:
                    # Table DistanceParcourue peut être manquante
                    distance_totale = 0
                
                # Éviter division par zéro
                if distance_totale > 0:
                    # Calculer le coût moyen par km (en EUR puis convertir en GNF)
                    c['cout_moyen_eur'] = c['cout_total_eur'] / distance_totale
                    c['cout_moyen'] = convertir_en_gnf(c['cout_moyen_eur'])
                    c['cout_moyen_formatte'] = formater_cout_par_km_gnf(c['cout_moyen_eur'])
                    c['distance_totale'] = distance_totale
                    
                    # Définir le seuil selon la catégorie du véhicule (valeurs en EUR/km)
                    if vehicule.categorie == 'Berline':
                        c['seuil_eur'] = 0.15
                    elif vehicule.categorie == 'SUV':
                        c['seuil_eur'] = 0.20
                    elif vehicule.categorie == 'Utilitaire':
                        c['seuil_eur'] = 0.25
                    else:
                        c['seuil_eur'] = 0.18
                    
                    # Convertir le seuil en GNF/km
                    c['seuil'] = convertir_en_gnf(c['seuil_eur'])
                    c['seuil_formatte'] = formater_cout_par_km_gnf(c['seuil_eur'])
                    
                    # Définir si une alerte doit être déclenchée
                    # On compare les valeurs en GNF pour plus de cohérence avec l'affichage
                    c['alerte'] = c['cout_moyen'] > c['seuil']  # Alerte si coût > seuil
                    
                    try:
                        # Créer ou mettre à jour une alerte automatique si nécessaire
                        if c['alerte']:
                            # Vérifier si une alerte active existe déjà pour ce véhicule et ce type
                            alerte_existante = Alerte.objects.filter(
                                vehicule=vehicule,
                                type_alerte__startswith='Coût de fonctionnement',
                                statut='Active'
                            ).first()
                            
                            # Description de l'alerte
                            description = f"Le coût de fonctionnement du véhicule {vehicule.marque} {vehicule.modele} ({vehicule.immatriculation}) "
                            description += f"est de {c['cout_moyen_formatte']} ({c['cout_moyen_eur']:.2f} €/km), "
                            description += f"ce qui dépasse le seuil recommandé de {c['seuil_formatte']} ({c['seuil_eur']:.2f} €/km)."
                            
                            if alerte_existante:
                                # Mettre à jour l'alerte existante
                                alerte_existante.description = description
                                alerte_existante.save()
                            else:
                                # Créer une nouvelle alerte
                                niveau_urgence = 'Critique' if c['cout_moyen'] > c['seuil'] * 1.5 else 'Élevé' if c['cout_moyen'] > c['seuil'] * 1.2 else 'Moyen'
                                Alerte.objects.create(
                                    vehicule=vehicule,
                                    type_alerte=f"Coût de fonctionnement élevé",
                                    description=description,
                                    niveau_urgence=niveau_urgence,
                                    statut='Active'
                                )
                    except Exception:
                        # La table Alerte peut être manquante
                        pass
                else:
                    c['cout_moyen_eur'] = 0
                    c['cout_moyen'] = 0
                    c['cout_moyen_formatte'] = formater_cout_par_km_gnf(0)
                    c['distance_totale'] = 0
                    c['seuil_eur'] = 0
                    c['seuil'] = 0
                    c['seuil_formatte'] = formater_cout_par_km_gnf(0)
                    c['alerte'] = False
            except Exception as e:
                # Erreur lors de la récupération des informations du véhicule
                pass
        
        # Trier par coût moyen décroissant
        couts = sorted(couts, key=lambda x: x.get('cout_moyen', 0), reverse=True)
        
    except Exception as e:
        # Gérer l'erreur de table manquante ou autre erreur
        couts = []
        messages.error(request, f"Erreur lors de l'accès aux données de coûts de fonctionnement: {str(e)}. La table n'existe peut-être pas encore.")
    
    context = {
        'couts': couts,
        'titre': 'KPI - Coûts de fonctionnement',
        'description': 'Analyse détaillée des coûts de fonctionnement par kilomètre',
        'devise': 'GNF',
        'table_missing': 'couts' not in locals() or not couts
    }
    
    return render(request, 'fleet_app/kpi_detail.html', context)

@login_required
def kpi_couts_financiers(request):
    # Récupérer tous les coûts financiers par véhicule
    couts = CoutFinancier.objects.values('vehicule').annotate(
        cout_total=Sum('montant')
    ).order_by('vehicule')
    
    # Enrichir les données avec les informations du véhicule et calculer le coût par km
    for c in couts:
        vehicule = Vehicule.objects.get(id_vehicule=c['vehicule'])
        c['immatriculation'] = vehicule.immatriculation
        c['marque'] = vehicule.marque
        c['modele'] = vehicule.modele
        c['categorie'] = vehicule.categorie
        c['type_moteur'] = vehicule.type_moteur
        
        # Convertir le coût total en GNF
        c['cout_total_eur'] = c['cout_total']
        c['cout_total'] = convertir_en_gnf(c['cout_total'])
        c['cout_total_formatte'] = formater_montant_gnf(c['cout_total'])
        
        # Récupérer la distance parcourue pour ce véhicule
        distance_totale = DistanceParcourue.objects.filter(vehicule=vehicule).aggregate(Sum('distance_parcourue'))['distance_parcourue__sum'] or 0
        
        # Éviter division par zéro
        if distance_totale > 0:
            # Calculer le coût moyen par km (en EUR puis convertir en GNF)
            c['cout_moyen_eur'] = c['cout_total_eur'] / distance_totale
            c['cout_moyen'] = convertir_en_gnf(c['cout_moyen_eur'])
            c['cout_moyen_formatte'] = formater_cout_par_km_gnf(c['cout_moyen_eur'])
            c['distance_totale'] = distance_totale
            
            # Définir le seuil selon la catégorie du véhicule (valeurs en EUR/km)
            if vehicule.categorie == 'Berline':
                c['seuil_eur'] = 0.12
            elif vehicule.categorie == 'SUV':
                c['seuil_eur'] = 0.15
            elif vehicule.categorie == 'Utilitaire':
                c['seuil_eur'] = 0.18
            else:
                c['seuil_eur'] = 0.14
            
            # Convertir le seuil en GNF/km
            c['seuil'] = convertir_en_gnf(c['seuil_eur'])
            c['seuil_formatte'] = formater_cout_par_km_gnf(c['seuil_eur'])
            
            # Définir si une alerte doit être déclenchée
            c['alerte'] = c['cout_moyen_eur'] > c['seuil_eur']  # Alerte si coût > seuil
            
            # Créer ou mettre à jour une alerte automatique si nécessaire
            if c['alerte']:
                # Vérifier si une alerte active existe déjà pour ce véhicule et ce type
                alerte_existante = Alerte.objects.filter(
                    vehicule=vehicule,
                    type_alerte__startswith='Coût financier',
                    statut='Active'
                ).first()
                
                # Description de l'alerte
                description = f"Le coût financier du véhicule {vehicule.marque} {vehicule.modele} ({vehicule.immatriculation}) "
                description += f"est de {c['cout_moyen_formatte']} ({c['cout_moyen_eur']:.2f} €/km), "
                description += f"ce qui dépasse le seuil recommandé de {c['seuil_formatte']} ({c['seuil_eur']:.2f} €/km)."
                
                if alerte_existante:
                    # Mettre à jour l'alerte existante
                    alerte_existante.description = description
                    alerte_existante.save()
                else:
                    # Créer une nouvelle alerte
                    niveau_urgence = 'Critique' if c['cout_moyen_eur'] > c['seuil_eur'] * 1.5 else 'Élevé' if c['cout_moyen_eur'] > c['seuil_eur'] * 1.2 else 'Moyen'
                    Alerte.objects.create(
                        vehicule=vehicule,
                        type_alerte=f"Coût financier élevé",
                        description=description,
                        niveau_urgence=niveau_urgence,
                        statut='Active'
                    )
        else:
            c['cout_moyen_eur'] = 0
            c['cout_moyen'] = 0
            c['cout_moyen_formatte'] = formater_cout_par_km_gnf(0)
            c['distance_totale'] = 0
            c['seuil_eur'] = 0
            c['seuil'] = 0
            c['seuil_formatte'] = formater_cout_par_km_gnf(0)
            c['alerte'] = False
    
    # Trier par coût moyen décroissant
    couts = sorted(couts, key=lambda x: x['cout_moyen'], reverse=True)
    
    context = {
        'couts': couts,
        'titre': 'KPI - Coûts financiers',
        'description': 'Analyse détaillée des coûts financiers par kilomètre',
        'devise': 'GNF'
    }
    
    return render(request, 'fleet_app/kpi_detail.html', context)

# Classes dupliquées supprimées - utiliser les versions sécurisées ci-dessous

# Vues pour les KPI additionnels
@login_required
def kpi_couts_fonctionnement(request):
    # Initialiser les variables
    form = None
    couts = []
    labels = []
    data = []
    data_gnf = []
    types_labels = []
    types_data = []
    types_data_gnf = []
    table_missing = False
    
    try:
        # Gestion du formulaire d'ajout
        if request.method == 'POST':
            try:
                form = CoutFonctionnementForm(request.POST)
                if form.is_valid():
                    cout = form.save(commit=False)
                    
                    # Calcul automatique du coût par km
                    if cout.montant and cout.km_actuel:
                        # Récupérer le kilométrage précédent du véhicule
                        try:
                            derniere_distance = DistanceParcourue.objects.filter(
                                vehicule=cout.vehicule
                            ).order_by('-date_fin').first()
                            
                            if derniere_distance:
                                km_precedent = derniere_distance.km_fin
                                distance_parcourue = cout.km_actuel - km_precedent
                                if distance_parcourue > 0:
                                    cout.cout_par_km = cout.montant / distance_parcourue
                                else:
                                    # Si pas de distance valide, utiliser une estimation
                                    cout.cout_par_km = cout.montant / 1000
                            else:
                                # Pas de données précédentes, estimation basée sur 1000km
                                cout.cout_par_km = cout.montant / 1000
                        except Exception:
                            # En cas d'erreur, estimation simple
                            cout.cout_par_km = cout.montant / 1000
                    
                    cout.save()
                    messages.success(request, 'Coût de fonctionnement ajouté avec succès.')
                    return redirect('fleet_app:kpi_couts_fonctionnement')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout du coût de fonctionnement: {str(e)}. La table n'existe peut-être pas encore.")
                form = None
        else:
            try:
                form = CoutFonctionnementForm()
            except Exception:
                form = None
                messages.warning(request, "Le formulaire de coûts de fonctionnement n'a pas pu être chargé. La table correspondante n'existe peut-être pas encore.")
        
        # Récupérer les données de coûts de fonctionnement
        couts = CoutFonctionnement.objects.filter(user=request.user).order_by('-date')[:10]
        
        # Données pour graphiques
        vehicules = Vehicule.objects.filter(user=request.user)
        labels = [f"{v.marque} {v.modele} ({v.immatriculation})" for v in vehicules]
        
        # Calcul des coûts moyens par véhicule
        data = []
        data_gnf = []
        for v in vehicules:
            cout_avg = CoutFonctionnement.objects.filter(vehicule=v).aggregate(Avg('cout_par_km'))
            cout_moyen = cout_avg['cout_par_km__avg'] or 0
            data.append(cout_moyen)
            # Conversion en GNF
            data_gnf.append(convertir_en_gnf(cout_moyen))
        
        # Calcul des coûts par type
        types_cout = CoutFonctionnement.objects.values('type_cout').annotate(total=Sum('montant'))
        types_labels = [item['type_cout'] for item in types_cout]
        types_data = [item['total'] for item in types_cout]
        # Conversion des totaux en GNF
        types_data_gnf = [convertir_en_gnf(item) for item in types_data]
        
        # Ajouter les montants en GNF pour chaque coût
        for cout in couts:
            cout.montant_gnf = convertir_en_gnf(cout.montant)
            cout.cout_par_km_gnf = convertir_en_gnf(cout.cout_par_km)
            cout.montant_gnf_formatte = formater_montant_gnf(cout.montant)
            cout.cout_par_km_gnf_formatte = formater_cout_par_km_gnf(cout.cout_par_km)
    
    except Exception as e:
        # Gérer l'erreur de table manquante ou autre erreur
        messages.error(request, f"Erreur lors de l'accès aux données de coûts de fonctionnement: {str(e)}. La table n'existe peut-être pas encore.")
        table_missing = True
    
    context = {
        'couts': couts,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'data_gnf': json.dumps(data_gnf),
        'types_labels': json.dumps(types_labels),
        'types_data': json.dumps(types_data),
        'types_data_gnf': json.dumps(types_data_gnf),
        'form': form,
        'taux_conversion': TAUX_CONVERSION_EUR_GNF,
        'devise': 'GNF',
        'table_missing': table_missing
    }
    
    return render(request, 'fleet_app/kpi_couts_fonctionnement.html', context)

@login_required
@require_user_ownership(CoutFonctionnement)
def cout_fonctionnement_edit(request, pk):
    try:
        cout = get_user_object_or_404(CoutFonctionnement, request.user, pk=pk)
        
        # Conversion des montants en GNF pour l'affichage
        cout.montant_gnf = convertir_en_gnf(cout.montant)
        cout.cout_par_km_gnf = convertir_en_gnf(cout.cout_par_km)
        
        if request.method == 'POST':
            form = CoutFonctionnementForm(request.POST, instance=cout)
            if form.is_valid():
                form.save()
                messages.success(request, "Le coût de fonctionnement a été modifié avec succès.")
                return redirect('fleet_app:kpi_couts_fonctionnement')
        else:
            form = CoutFonctionnementForm(instance=cout)
        
        context = {
            'form': form,
            'cout': cout,
            'title': 'Modifier un coût de fonctionnement',
            'taux_conversion': TAUX_CONVERSION_EUR_GNF,
        }
        return render(request, 'fleet_app/cout_fonctionnement_form.html', context)
    except:
        messages.error(request, f"Le coût de fonctionnement avec l'ID {pk} n'existe pas ou a été supprimé.")
        return redirect('fleet_app:kpi_couts_fonctionnement')

@login_required
@require_user_ownership(CoutFonctionnement)
def cout_fonctionnement_delete(request, pk):
    try:
        cout = get_user_object_or_404(CoutFonctionnement, request.user, pk=pk)
        if request.method == 'POST':
            cout.delete()
            messages.success(request, "Le coût de fonctionnement a été supprimé avec succès.")
            return redirect('fleet_app:kpi_couts_fonctionnement')
        
        context = {
            'cout': cout,
        }
        return render(request, 'fleet_app/cout_fonctionnement_confirm_delete.html', context)
    except:
        messages.error(request, f"Le coût de fonctionnement avec l'ID {pk} n'existe pas ou a déjà été supprimé.")
        return redirect('fleet_app:kpi_couts_fonctionnement')

@login_required
def kpi_couts_financiers(request):
    form = None
    if request.method == 'POST':
        form = CoutFinancierForm(request.POST)
        if form.is_valid():
            cout = form.save(commit=False)
            
            # Calcul automatique du coût par km
            if cout.montant and cout.kilometrage:
                # Récupérer le kilométrage précédent du véhicule
                try:
                    derniere_distance = DistanceParcourue.objects.filter(
                        vehicule=cout.vehicule
                    ).order_by('-date_fin').first()
                    
                    if derniere_distance:
                        km_precedent = derniere_distance.km_fin
                        distance_parcourue = cout.kilometrage - km_precedent
                        if distance_parcourue > 0:
                            cout.cout_par_km = cout.montant / distance_parcourue
                        else:
                            # Si pas de distance valide, utiliser une estimation
                            cout.cout_par_km = cout.montant / 1000
                    else:
                        # Pas de données précédentes, estimation basée sur 1000km
                        cout.cout_par_km = cout.montant / 1000
                except Exception:
                    # En cas d'erreur, estimation simple
                    cout.cout_par_km = cout.montant / 1000
            
            cout.save()
            messages.success(request, 'Coût financier ajouté avec succès.')
            return redirect('fleet_app:kpi_couts_financiers')
    else:
        form = CoutFinancierForm()
    
    couts = CoutFinancier.objects.filter(user=request.user).order_by('-date')[:10]
    
    # Conversion des montants en GNF pour l'affichage
    for cout in couts:
        cout.montant_gnf = convertir_en_gnf(cout.montant)
        cout.cout_par_km_gnf = convertir_en_gnf(cout.cout_par_km)
        cout.montant_gnf_formatte = formater_montant_gnf(cout.montant)
        cout.cout_par_km_gnf_formatte = formater_cout_par_km_gnf(cout.cout_par_km)
    
    # Données pour graphiques
    vehicules = Vehicule.objects.filter(user=request.user)
    labels = [f"{v.marque} {v.modele} ({v.immatriculation})" for v in vehicules]
    
    # Calcul des coûts totaux par véhicule (convertis en GNF)
    data = []
    for v in vehicules:
        cout_total = CoutFinancier.objects.filter(vehicule=v).aggregate(Sum('montant'))
        montant_eur = cout_total['montant__sum'] or 0
        montant_gnf = convertir_en_gnf(montant_eur)
        data.append(montant_gnf)
    
    # Calcul des coûts par type (convertis en GNF)
    types_cout = CoutFinancier.objects.values('type_cout').annotate(total=Sum('montant'))
    types_labels = [item['type_cout'] for item in types_cout]
    types_data = [convertir_en_gnf(item['total']) for item in types_cout]
    
    context = {
        'couts': couts,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'types_labels': json.dumps(types_labels),
        'types_data': json.dumps(types_data),
        'form': form,
        'taux_conversion': TAUX_CONVERSION_EUR_GNF
    }
    
    return render(request, 'fleet_app/kpi_couts_financiers.html', context)

@login_required
@require_user_ownership(CoutFinancier)
def cout_financier_edit(request, pk):
    try:
        cout = get_user_object_or_404(CoutFinancier, request.user, pk=pk)
        
        # Conversion des montants en GNF pour l'affichage
        cout.montant_gnf = convertir_en_gnf(cout.montant)
        cout.cout_par_km_gnf = convertir_en_gnf(cout.cout_par_km)
        
        if request.method == 'POST':
            form = CoutFinancierForm(request.POST, instance=cout)
            if form.is_valid():
                cout = form.save(commit=False)
                
                # Recalcul automatique du coût par km lors de la modification
                if cout.montant and cout.kilometrage:
                    try:
                        derniere_distance = DistanceParcourue.objects.filter(
                            vehicule=cout.vehicule
                        ).order_by('-date_fin').first()
                        
                        if derniere_distance:
                            km_precedent = derniere_distance.km_fin
                            distance_parcourue = cout.kilometrage - km_precedent
                            if distance_parcourue > 0:
                                cout.cout_par_km = cout.montant / distance_parcourue
                            else:
                                cout.cout_par_km = cout.montant / 1000
                        else:
                            cout.cout_par_km = cout.montant / 1000
                    except Exception:
                        cout.cout_par_km = cout.montant / 1000
                
                cout.save()
                messages.success(request, "Le coût financier a été modifié avec succès.")
                return redirect('fleet_app:kpi_couts_financiers')
        else:
            form = CoutFinancierForm(instance=cout)
        
        context = {
            'form': form,
            'cout': cout,
            'title': 'Modifier un coût financier',
            'taux_conversion': TAUX_CONVERSION_EUR_GNF,
        }
        return render(request, 'fleet_app/cout_financier_form.html', context)
    except:
        messages.error(request, f"Le coût financier avec l'ID {pk} n'existe pas ou a été supprimé.")
        return redirect('fleet_app:kpi_couts_financiers')

@login_required
@require_user_ownership(CoutFinancier)
def cout_financier_delete(request, pk):
    try:
        cout = get_user_object_or_404(CoutFinancier, request.user, pk=pk)
        if request.method == 'POST':
            cout.delete()
            messages.success(request, "Le coût financier a été supprimé avec succès.")
            return redirect('fleet_app:kpi_couts_financiers')
        
        context = {
            'cout': cout,
        }
        return render(request, 'fleet_app/cout_financier_confirm_delete.html', context)
    except:
        messages.error(request, f"Le coût financier avec l'ID {pk} n'existe pas ou a déjà été supprimé.")
        return redirect('fleet_app:kpi_couts_financiers')

@login_required
def kpi_incidents(request):
    form = None
    if request.method == 'POST':
        form = IncidentSecuriteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Incident de sécurité ajouté avec succès.')
            return redirect('fleet_app:kpi_incidents')
    else:
        form = IncidentSecuriteForm()
    
    # Récupérer tous les incidents et appliquer pagination et recherche
    incidents_list = IncidentSecurite.objects.filter(user=request.user).order_by('-date_incident')
    
    # Champs sur lesquels effectuer la recherche
    search_fields = ['vehicule__marque', 'vehicule__modele', 'vehicule__immatriculation', 'conducteur', 'description', 'gravite']
    
    # Appliquer pagination et recherche
    incidents, search_query = paginate_and_search(request, incidents_list, search_fields)
    
    # Données pour graphiques
    vehicules = Vehicule.objects.filter(user=request.user)
    labels = [f"{v.marque} {v.modele} ({v.immatriculation})" for v in vehicules]
    
    # Calcul du nombre d'incidents par véhicule
    data = []
    for v in vehicules:
        incident_count = IncidentSecurite.objects.filter(vehicule=v).count()
        data.append(incident_count)
    
    # Calcul des incidents par gravité
    gravites = IncidentSecurite.objects.values('gravite').annotate(total=Count('id'))
    gravites_labels = [item['gravite'] for item in gravites]
    gravites_data = [item['total'] for item in gravites]
    
    context = {
        'incidents': incidents,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'gravites_labels': json.dumps(gravites_labels),
        'gravites_data': json.dumps(gravites_data),
        'form': form,
        'search_query': search_query,
    }
    
    return render(request, 'fleet_app/kpi_incidents.html', context)

@login_required
def kpi_utilisation(request):
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.filter(user=request.user)
    labels = [f"{v.marque} {v.modele} ({v.immatriculation})" for v in vehicules]
    
    # Initialiser les variables
    utilisations = []
    departements_labels = []
    departements_data = []
    data = []
    search_query = request.GET.get('search', '')
    form = None
    table_missing = False
    
    try:
        # Formulaire d'ajout d'utilisation
        if request.method == 'POST':
            try:
                form = UtilisationVehiculeForm(request.POST)
                if form.is_valid():
                    form.save()
                    messages.success(request, "L'utilisation a été ajoutée avec succès.")
                    return redirect('fleet_app:kpi_utilisation')
            except Exception as e:
                messages.error(request, f"Erreur lors de l'ajout des données d'utilisation: {str(e)}. La table n'existe peut-être pas encore.")
                form = None
        else:
            try:
                form = UtilisationVehiculeForm()
            except Exception:
                form = None
                messages.warning(request, "Le formulaire d'utilisation n'a pas pu être chargé. La table correspondante n'existe peut-être pas encore.")
        
        # Récupérer toutes les utilisations avec filtre de recherche
        utilisations_list = UtilisationVehicule.objects.filter(user=request.user).order_by('-date_debut')
        
        # Appliquer le filtre de recherche si présent
        if search_query:
            utilisations_list = utilisations_list.filter(
                Q(vehicule__marque__icontains=search_query) |
                Q(vehicule__modele__icontains=search_query) |
                Q(vehicule__immatriculation__icontains=search_query) |
                Q(conducteur__icontains=search_query) |
                Q(departement__icontains=search_query) |
                Q(motif__icontains=search_query)
            )
        
        # Pagination avec 10 éléments par page
        paginator = Paginator(utilisations_list, 10)
        page = request.GET.get('page', 1)
        
        try:
            utilisations = paginator.page(page)
        except PageNotAnInteger:
            utilisations = paginator.page(1)
        except EmptyPage:
            utilisations = paginator.page(paginator.num_pages)
        
        # Ajouter la distance parcourue à chaque utilisation
        for utilisation in utilisations:
            if utilisation.km_retour and utilisation.km_depart:
                utilisation.distance_parcourue = utilisation.km_retour - utilisation.km_depart
            else:
                utilisation.distance_parcourue = 0
    
        # Passer le paramètre de recherche au contexte pour les liens de pagination
        departements = UtilisationVehicule.objects.values('departement').annotate(total=Count('id'))
        departements_labels = [item['departement'] for item in departements]
        departements_data = [item['total'] for item in departements]
        
        # Calcul du nombre d'utilisations par véhicule pour le graphique
        data = []
        for v in vehicules:
            utilisation_count = UtilisationVehicule.objects.filter(vehicule=v).count()
            data.append(utilisation_count)
            
    except Exception as e:
        # Gérer l'erreur de table manquante ou autre erreur
        utilisations = []
        messages.error(request, f"Erreur lors de l'accès aux données d'utilisation: {str(e)}. La table n'existe peut-être pas encore.")
        table_missing = True
    
    context = {
        'utilisations': utilisations,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'departements_labels': json.dumps(departements_labels),
        'departements_data': json.dumps(departements_data),
        'form': form,
        'search_query': search_query,
        'table_missing': table_missing
    }
    
    return render(request, 'fleet_app/kpi_utilisation.html', context)

@login_required
def kpi_distance(request):
    # Récupérer tous les véhicules
    vehicules = Vehicule.objects.filter(user=request.user)
    labels = [f"{v.marque} {v.modele} ({v.immatriculation})" for v in vehicules]
    
    # Formulaire d'ajout de distance parcourue
    if request.method == 'POST':
        form = DistanceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "La distance parcourue a été ajoutée avec succès.")
            return redirect('fleet_app:kpi_distance')
    else:
        form = DistanceForm()
    
    # Récupérer toutes les distances avec filtre de recherche
    search_query = request.GET.get('search', '')
    distances_list = DistanceParcourue.objects.filter(user=request.user).order_by('-date_debut')
    
    # Appliquer le filtre de recherche si présent
    if search_query:
        distances_list = distances_list.filter(
            Q(vehicule__marque__icontains=search_query) |
            Q(vehicule__modele__icontains=search_query) |
            Q(vehicule__immatriculation__icontains=search_query) |
            Q(type_moteur__icontains=search_query)
        )
    
    # Pagination avec 10 éléments par page
    paginator = Paginator(distances_list, 10)
    page = request.GET.get('page', 1)
    
    try:
        distances = paginator.page(page)
    except PageNotAnInteger:
        distances = paginator.page(1)
    except EmptyPage:
        distances = paginator.page(paginator.num_pages)
    
    # Calcul des statistiques de distance par véhicule pour le graphique
    data = []
    for v in vehicules:
        total_distance = DistanceParcourue.objects.filter(vehicule=v).aggregate(Sum('distance_parcourue'))
        distance_sum = total_distance['distance_parcourue__sum'] or 0
        data.append(distance_sum)
    
    context = {
        'distances': distances,
        'labels': json.dumps(labels),
        'data': json.dumps(data),
        'form': form,
        'search_query': search_query,
        'edit_mode': False
    }
    
    return render(request, 'fleet_app/kpi_distance.html', context)

# Vue pour les rapports
@login_required
def rapports(request):
    return render(request, 'fleet_app/rapports.html')


# API pour récupérer les alertes KPI au format JSON
from django.http import JsonResponse
from django.db.models import Q, Sum, Avg, Count
import json
from datetime import datetime, date

# Fonctions utilitaires pour le calcul des KPI
def calculer_distance_parcourue(vehicule):
    """Calcule la distance parcourue annuelle d'un véhicule et détermine si une alerte doit être déclenchée"""
    # Récupérer l'année en cours
    annee_courante = date.today().year
    
    # Calculer la distance parcourue cette année
    distances = DistanceParcourue.objects.filter(
        vehicule=vehicule,
        date_debut__year=annee_courante
    )
    
    distance_annuelle = distances.aggregate(Sum('distance_parcourue'))['distance_parcourue__sum'] or 0
    
    # Déterminer la cible en fonction du type de véhicule
    if vehicule.type_vehicule == 'Berline':
        cible = 15000  # 15 000 km par an
    elif vehicule.type_vehicule == 'SUV':
        cible = 20000  # 20 000 km par an
    elif vehicule.type_vehicule == 'Camionnette':
        cible = 25000  # 25 000 km par an
    else:
        cible = 18000  # Valeur par défaut
    
    # Calculer l'écart par rapport à la cible
    ecart = distance_annuelle - cible
    ecart_pourcentage = (ecart / cible * 100) if cible > 0 else 0
    
    # Déterminer si une alerte doit être déclenchée
    # Alerte si dépassement > 20% de la cible
    alerte = ecart_pourcentage > 20
    
    return {
        'distance_annuelle': distance_annuelle,
        'cible': cible,
        'ecart': ecart,
        'ecart_pourcentage': ecart_pourcentage,
        'alerte': alerte
    }

def calculer_consommation(vehicule):
    """Calcule la consommation moyenne de carburant d'un véhicule et détermine si une alerte doit être déclenchée"""
    # Récupérer les 5 dernières consommations
    consommations = ConsommationCarburant.objects.filter(vehicule=vehicule).order_by('-date_plein')[:5]
    
    if not consommations:
        return {
            'consommation': 0,
            'cible': 0,
            'ecart': 0,
            'ecart_pourcentage': 0,
            'alerte': False
        }
    
    # Calculer la consommation moyenne
    total_litres = sum(c.litres for c in consommations)
    total_km = sum(c.kilometres_parcourus for c in consommations)
    
    if total_km == 0:
        consommation = 0
    else:
        consommation = (total_litres / total_km) * 100  # L/100km
    
    # Déterminer la cible en fonction du type de véhicule et de carburant
    if vehicule.type_carburant == 'Diesel':
        if vehicule.type_vehicule == 'Berline':
            cible = 5.0  # 5 L/100km
        elif vehicule.type_vehicule == 'SUV':
            cible = 7.0  # 7 L/100km
        else:
            cible = 8.0  # 8 L/100km pour les autres types
    else:  # Essence
        if vehicule.type_vehicule == 'Berline':
            cible = 6.0  # 6 L/100km
        elif vehicule.type_vehicule == 'SUV':
            cible = 8.5  # 8.5 L/100km
        else:
            cible = 10.0  # 10 L/100km pour les autres types
    
    # Calculer l'écart par rapport à la cible
    ecart = consommation - cible
    ecart_pourcentage = (ecart / cible * 100) if cible > 0 else 0
    
    # Déterminer si une alerte doit être déclenchée
    # Alerte si dépassement > 15% de la cible
    alerte = ecart_pourcentage > 15
    
    return {
        'consommation': consommation,
        'cible': cible,
        'ecart': ecart,
        'ecart_pourcentage': ecart_pourcentage,
        'alerte': alerte
    }

def calculer_disponibilite(vehicule):
    """Calcule le taux de disponibilité d'un véhicule et détermine si une alerte doit être déclenchée"""
    # Récupérer les indisponibilités des 30 derniers jours
    date_debut = date.today() - timedelta(days=30)
    indisponibilites = Indisponibilite.objects.filter(
        vehicule=vehicule,
        date_debut__gte=date_debut
    )
    
    # Calculer le nombre total de jours d'indisponibilité
    jours_indisponibles = 0
    for indispo in indisponibilites:
        date_fin = indispo.date_fin or date.today()
        duree = (date_fin - indispo.date_debut).days + 1
        jours_indisponibles += duree
    
    # Limiter à 30 jours maximum
    jours_indisponibles = min(jours_indisponibles, 30)
    
    # Calculer le taux de disponibilité
    disponibilite = ((30 - jours_indisponibles) / 30) * 100
    
    # Déterminer si une alerte doit être déclenchée
    # Alerte si disponibilité < 80%
    alerte = disponibilite < 80
    
    return {
        'disponibilite': disponibilite,
        'jours_indisponibles': jours_indisponibles,
        'alerte': alerte
    }

def calculer_utilisation(vehicule):
    """Calcule le taux d'utilisation d'un véhicule et détermine si une alerte doit être déclenchée"""
    # Récupérer les utilisations des 30 derniers jours
    date_debut = date.today() - timedelta(days=30)
    utilisations = FeuilleDeRoute.objects.filter(
        vehicule=vehicule,
        date_depart__gte=date_debut
    )
    
    # Calculer le nombre de jours d'utilisation
    jours_utilises = utilisations.values('date_depart').distinct().count()
    
    # Calculer le taux d'utilisation
    taux_utilisation = (jours_utilises / 30) * 100
    
    # Déterminer la cible minimale en fonction du type de véhicule
    if vehicule.type_vehicule == 'Berline':
        cible_min = 70  # 70% d'utilisation minimale
    elif vehicule.type_vehicule == 'SUV':
        cible_min = 60  # 60% d'utilisation minimale
    else:
        cible_min = 50  # 50% pour les autres types
    
    # Déterminer si une alerte doit être déclenchée
    # Alerte si utilisation < cible_min ou > 95%
    alerte = taux_utilisation < cible_min or taux_utilisation > 95
    
    return {
        'taux': taux_utilisation,
        'jours_utilises': jours_utilises,
        'cible_min': cible_min,
        'alerte': alerte
    }

@login_required
def get_alertes_kpi(request):
    """API pour récupérer les alertes KPI en temps réel"""
    # Récupérer toutes les alertes KPI actives
    alertes_kpi = []
    
    # 1. Récupérer tous les véhicules
    vehicules = Vehicule.objects.filter(user=request.user)
    
    for vehicule in vehicules:
        # 2. Calculer les KPI pour chaque véhicule
        
        # 2.1 Distance parcourue
        distance_parcourue = calculer_distance_parcourue(vehicule)
        if distance_parcourue['alerte']:
            type_kpi = "Distance parcourue"
            severite = "Critique" if distance_parcourue['ecart_pourcentage'] > 30 else "Élevé"
            alertes_kpi.append({
                'vehicule_id': vehicule.id_vehicule,
                'vehicule_info': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'type_kpi': type_kpi,
                'valeur_actuelle': round(distance_parcourue['distance_annuelle'], 2),
                'seuil': round(distance_parcourue['cible'], 2),
                'ecart': round(distance_parcourue['ecart'], 2),
                'unite': 'km',
                'severite': severite
            })
        
        # 2.2 Consommation de carburant
        consommation = calculer_consommation(vehicule)
        if consommation['alerte']:
            type_kpi = "Consommation de carburant"
            severite = "Critique" if consommation['ecart_pourcentage'] > 20 else "Élevé"
            alertes_kpi.append({
                'vehicule_id': vehicule.id_vehicule,
                'vehicule_info': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'type_kpi': type_kpi,
                'valeur_actuelle': round(consommation['consommation'], 2),
                'seuil': round(consommation['cible'], 2),
                'ecart': round(consommation['ecart'], 2),
                'unite': 'L/100km',
                'severite': severite
            })
        
        # 2.3 Disponibilité
        disponibilite = calculer_disponibilite(vehicule)
        if disponibilite['alerte']:
            type_kpi = "Disponibilité"
            severite = "Critique" if disponibilite['disponibilite'] < 70 else "Élevé"
            alertes_kpi.append({
                'vehicule_id': vehicule.id_vehicule,
                'vehicule_info': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'type_kpi': type_kpi,
                'valeur_actuelle': round(disponibilite['disponibilite'], 2),
                'seuil': 80,
                'ecart': round(80 - disponibilite['disponibilite'], 2),
                'unite': '%',
                'severite': severite
            })
        
        # 2.4 Utilisation
        utilisation = calculer_utilisation(vehicule)
        if utilisation['alerte']:
            type_kpi = "Utilisation"
            if utilisation['taux'] < 70:
                severite = "Critique" if utilisation['taux'] < 50 else "Élevé"
                seuil = 70
                ecart = 70 - utilisation['taux']
            else:  # > 95%
                severite = "Critique" if utilisation['taux'] > 98 else "Élevé"
                seuil = 95
                ecart = utilisation['taux'] - 95
            
            alertes_kpi.append({
                'vehicule_id': vehicule.id_vehicule,
                'vehicule_info': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'type_kpi': type_kpi,
                'valeur_actuelle': round(utilisation['taux'], 2),
                'seuil': seuil,
                'ecart': round(ecart, 2),
                'unite': '%',
                'severite': severite
            })
    
    # Trier les alertes par sévérité (Critique d'abord, puis Élevé)
    alertes_kpi = sorted(alertes_kpi, key=lambda x: 0 if x['severite'] == 'Critique' else 1)
    
    return JsonResponse({
        'alertes_kpi': alertes_kpi,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

@login_required
def recherche_dynamique(request):
    """API pour la recherche dynamique dans les différentes tables de la base de données"""
    query = request.GET.get('q', '')
    table = request.GET.get('table', 'vehicules')
    limit = int(request.GET.get('limit', 10))
    
    # Filtres spécifiques
    statut = request.GET.get('statut', '')
    categorie = request.GET.get('categorie', '')
    niveau = request.GET.get('niveau', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    
    if not query or len(query) < 2:
        return JsonResponse({'results': []})
    
    results = []
    
    if table == 'vehicules':
        # Recherche dans les véhicules
        query_filter = Q(marque__icontains=query) | \
                      Q(modele__icontains=query) | \
                      Q(immatriculation__icontains=query) | \
                      Q(numero_chassis__icontains=query) | \
                      Q(categorie__icontains=query)
        
        # Appliquer les filtres supplémentaires
        if statut:
            query_filter &= Q(statut_actuel=statut)
        if categorie:
            query_filter &= Q(categorie=categorie)
            
        vehicules = Vehicule.objects.filter(query_filter)[:limit]
        
        for v in vehicules:
            results.append({
                'id': v.id_vehicule,
                'text': f"{v.marque} {v.modele} ({v.immatriculation})",
                'url': f"/vehicules/{v.id_vehicule}/",
                'type': 'Véhicule',
                'statut': v.statut_actuel,
                'categorie': v.categorie
            })
    
    elif table == 'chauffeurs':
        # Recherche dans les chauffeurs
        query_filter = Q(nom__icontains=query) | \
                      Q(prenom__icontains=query) | \
                      Q(numero_permis__icontains=query) | \
                      Q(telephone__icontains=query)
        
        # Appliquer les filtres supplémentaires
        if statut:
            query_filter &= Q(statut=statut)
            
        chauffeurs = Chauffeur.objects.filter(query_filter)[:limit]
        
        for c in chauffeurs:
            results.append({
                'id': c.id_chauffeur,
                'text': f"{c.nom} {c.prenom}",
                'url': f"/chauffeurs/{c.id_chauffeur}/",
                'type': 'Chauffeur',
                'telephone': c.telephone,
                'statut': c.statut
            })
    
    elif table == 'feuilles_route':
        # Recherche dans les feuilles de route
        query_filter = Q(destination__icontains=query) | \
                      Q(vehicule__marque__icontains=query) | \
                      Q(vehicule__modele__icontains=query) | \
                      Q(vehicule__immatriculation__icontains=query) | \
                      Q(chauffeur__nom__icontains=query) | \
                      Q(chauffeur__prenom__icontains=query)
        
        # Appliquer les filtres de date
        if date_debut:
            try:
                date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
                query_filter &= Q(date_depart__gte=date_debut_obj)
            except ValueError:
                pass
                
        if date_fin:
            try:
                date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
                query_filter &= Q(date_depart__lte=date_fin_obj)
            except ValueError:
                pass
                
        feuilles = FeuilleDeRoute.objects.filter(query_filter)[:limit]
        
        for f in feuilles:
            results.append({
                'id': f.id,
                'text': f"Feuille de route {f.id} - {f.destination}",
                'url': f"/feuilles-route/{f.id}/",
                'type': 'Feuille de route',
                'date': f.date_depart.strftime('%d/%m/%Y'),
                'vehicule': f"{f.vehicule.marque} {f.vehicule.modele} ({f.vehicule.immatriculation})",
                'chauffeur': f"{f.chauffeur.nom} {f.chauffeur.prenom}"
            })
    
    elif table == 'alertes':
        # Recherche dans les alertes
        query_filter = Q(type_alerte__icontains=query) | \
                      Q(description__icontains=query) | \
                      Q(vehicule__marque__icontains=query) | \
                      Q(vehicule__modele__icontains=query) | \
                      Q(vehicule__immatriculation__icontains=query)
        
        # Appliquer les filtres supplémentaires
        if statut:
            query_filter &= Q(statut=statut)
        if niveau:
            query_filter &= Q(niveau_urgence=niveau)
            
        # Filtres de date
        if date_debut:
            try:
                date_debut_obj = datetime.strptime(date_debut, '%Y-%m-%d').date()
                query_filter &= Q(date_creation__gte=date_debut_obj)
            except ValueError:
                pass
                
        if date_fin:
            try:
                date_fin_obj = datetime.strptime(date_fin, '%Y-%m-%d').date()
                query_filter &= Q(date_creation__lte=date_fin_obj)
            except ValueError:
                pass
                
        alertes = Alerte.objects.filter(query_filter)[:limit]
        
        for a in alertes:
            results.append({
                'id': a.id,
                'text': f"{a.type_alerte} - {a.vehicule.marque} {a.vehicule.modele}",
                'url': f"/alertes/",  # Redirection vers la liste des alertes avec un filtre
                'type': 'Alerte',
                'niveau': a.niveau_urgence,
                'statut': a.statut,
                'date': a.date_creation.strftime('%d/%m/%Y')
            })
    
    elif table == 'global':
        # Recherche globale dans toutes les tables principales
        # Véhicules
        vehicules = Vehicule.objects.filter(
            Q(marque__icontains=query) | 
            Q(modele__icontains=query) | 
            Q(immatriculation__icontains=query)
        )[:5]
        
        for v in vehicules:
            results.append({
                'id': v.id_vehicule,
                'text': f"{v.marque} {v.modele} ({v.immatriculation})",
                'url': f"/vehicules/{v.id_vehicule}/",
                'type': 'Véhicule'
            })
        
        # Chauffeurs
        chauffeurs = Chauffeur.objects.filter(
            Q(nom__icontains=query) | 
            Q(prenom__icontains=query)
        )[:5]
        
        for c in chauffeurs:
            results.append({
                'id': c.id_chauffeur,
                'text': f"{c.nom} {c.prenom}",
                'url': f"/chauffeurs/{c.id_chauffeur}/",
                'type': 'Chauffeur'
            })
        
        # Feuilles de route
        feuilles = FeuilleDeRoute.objects.filter(
            Q(destination__icontains=query)
        )[:5]
        
        for f in feuilles:
            results.append({
                'id': f.id,
                'text': f"Feuille de route - {f.destination}",
                'url': f"/feuilles-route/{f.id}/",
                'type': 'Feuille de route'
            })
    
    return JsonResponse({'results': results})

@login_required
def get_alertes_kpi(request):
    """API pour récupérer les alertes KPI au format JSON pour mise à jour automatique du tableau de bord"""
    # Définir les seuils pour les KPI
    kpi_seuils = {
        'consommation': {'cible': 8, 'acceptable': 10, 'critique': 12},  # L/100km
        'disponibilite': {'cible': 90, 'acceptable': 80, 'critique': 70},  # %
        'utilisation': {'cible': 85, 'acceptable': 70, 'critique': 60},  # %
        'cout_fonctionnement': {'cible': 0.15, 'acceptable': 0.20, 'critique': 0.25},  # €/km
        'cout_financier': {'cible': 0.25, 'acceptable': 0.30, 'critique': 0.35},  # €/km
    }
    
    # Récupérer les véhicules avec leurs dernières mesures de KPI
    vehicules = Vehicule.objects.filter(statut_actuel='Actif')
    
    # Générer les alertes KPI automatiques
    alertes_kpi = []
    
    for vehicule in vehicules:
        # Vérifier la consommation
        derniere_consommation = ConsommationCarburant.objects.filter(vehicule=vehicule).order_by('-date_plein2').first()
        if derniere_consommation and derniere_consommation.consommation_100km > kpi_seuils['consommation']['acceptable']:
            severite = 'Critique' if derniere_consommation.consommation_100km > kpi_seuils['consommation']['critique'] else 'Élevé'
            alertes_kpi.append({
                'type_kpi': 'Consommation',
                'vehicule_id': vehicule.id_vehicule,
                'vehicule_info': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'valeur_actuelle': round(derniere_consommation.consommation_100km, 1),
                'seuil': kpi_seuils['consommation']['acceptable'],
                'ecart': round(derniere_consommation.consommation_100km - kpi_seuils['consommation']['acceptable'], 1),
                'severite': severite,
                'unite': 'L/100km'
            })
        
        # Vérifier la disponibilité
        derniere_disponibilite = DisponibiliteVehicule.objects.filter(vehicule=vehicule).order_by('-date_fin').first()
        if derniere_disponibilite and derniere_disponibilite.disponibilite_pourcentage < kpi_seuils['disponibilite']['acceptable']:
            severite = 'Critique' if derniere_disponibilite.disponibilite_pourcentage < kpi_seuils['disponibilite']['critique'] else 'Élevé'
            alertes_kpi.append({
                'type_kpi': 'Disponibilité',
                'vehicule_id': vehicule.id_vehicule,
                'vehicule_info': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'valeur_actuelle': round(derniere_disponibilite.disponibilite_pourcentage, 1),
                'seuil': kpi_seuils['disponibilite']['acceptable'],
                'ecart': round(kpi_seuils['disponibilite']['acceptable'] - derniere_disponibilite.disponibilite_pourcentage, 1),
                'severite': severite,
                'unite': '%'
            })
        
        # Vérifier l'utilisation
        derniere_utilisation = UtilisationActif.objects.filter(vehicule=vehicule).order_by('-date_fin').first()
        if derniere_utilisation and derniere_utilisation.jours_disponibles > 0:
            taux_utilisation = (derniere_utilisation.jours_utilises / derniere_utilisation.jours_disponibles) * 100
            if taux_utilisation < kpi_seuils['utilisation']['acceptable']:
                severite = 'Critique' if taux_utilisation < kpi_seuils['utilisation']['critique'] else 'Élevé'
                alertes_kpi.append({
                    'type_kpi': 'Utilisation',
                    'vehicule_id': vehicule.id_vehicule,
                    'vehicule_info': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                    'valeur_actuelle': round(taux_utilisation, 1),
                    'seuil': kpi_seuils['utilisation']['acceptable'],
                    'ecart': round(kpi_seuils['utilisation']['acceptable'] - taux_utilisation, 1),
                    'severite': severite,
                    'unite': '%'
                })
        
        # Vérifier les coûts de fonctionnement
        dernier_cout_fonct = CoutFonctionnement.objects.filter(vehicule=vehicule).order_by('-date').first()
        if dernier_cout_fonct and dernier_cout_fonct.cout_par_km > kpi_seuils['cout_fonctionnement']['acceptable']:
            severite = 'Critique' if dernier_cout_fonct.cout_par_km > kpi_seuils['cout_fonctionnement']['critique'] else 'Élevé'
            alertes_kpi.append({
                'type_kpi': 'Coût fonctionnement',
                'vehicule_id': vehicule.id_vehicule,
                'vehicule_info': f"{vehicule.marque} {vehicule.modele} ({vehicule.immatriculation})",
                'valeur_actuelle': round(dernier_cout_fonct.cout_par_km, 3),
                'seuil': kpi_seuils['cout_fonctionnement']['acceptable'],
                'ecart': round(dernier_cout_fonct.cout_par_km - kpi_seuils['cout_fonctionnement']['acceptable'], 3),
                'severite': severite,
                'unite': '€/km'
            })
    
    # Trier les alertes par sévérité (Critique d'abord, puis Élevé)
    alertes_kpi = sorted(alertes_kpi, key=lambda x: 0 if x['severite'] == 'Critique' else 1)
    
    # Limiter à 10 alertes pour ne pas surcharger l'interface
    alertes_kpi = alertes_kpi[:10]
    
    return JsonResponse({'alertes_kpi': alertes_kpi})

# Classes dupliquées supprimées - utiliser les versions sécurisées ci-dessus

# Vues pour la gestion des utilisations de véhicules
@login_required
@require_user_ownership(UtilisationVehicule)
def utilisation_edit(request, pk):
    utilisation = get_user_object_or_404(UtilisationVehicule, request.user, pk=pk)
    if request.method == 'POST':
        form = UtilisationVehiculeForm(request.POST, instance=utilisation)
        if form.is_valid():
            form.save()
            messages.success(request, "L'utilisation a été modifiée avec succès.")
            return redirect('fleet_app:kpi_utilisation')
    else:
        form = UtilisationVehiculeForm(instance=utilisation)
    
    context = {
        'form': form,
        'utilisation': utilisation,
        'title': 'Modifier une utilisation',
    }
    return render(request, 'fleet_app/utilisation_form.html', context)

@login_required
@require_user_ownership(UtilisationVehicule)
def utilisation_delete(request, pk):
    utilisation = get_user_object_or_404(UtilisationVehicule, request.user, pk=pk)
    if request.method == 'POST':
        utilisation.delete()
        messages.success(request, "L'utilisation a été supprimée avec succès.")
        return redirect('fleet_app:kpi_utilisation')
    
    context = {
        'utilisation': utilisation,
        'title': 'Supprimer une utilisation',
    }
    return render(request, 'fleet_app/utilisation_confirm_delete.html', context)

# Vues pour la gestion des incidents de sécurité
@login_required
@require_user_ownership(IncidentSecurite)
def incident_edit(request, pk):
    incident = get_user_object_or_404(IncidentSecurite, request.user, pk=pk)
    if request.method == 'POST':
        form = IncidentSecuriteForm(request.POST, instance=incident)
        if form.is_valid():
            form.save()
            messages.success(request, "L'incident a été modifié avec succès.")
            return redirect('fleet_app:kpi_incidents')
    else:
        form = IncidentSecuriteForm(instance=incident)
    
    context = {
        'form': form,
        'incident': incident,
        'title': 'Modifier un incident',
    }
    return render(request, 'fleet_app/incident_form.html', context)

@login_required
@require_user_ownership(IncidentSecurite)
def incident_delete(request, pk):
    incident = get_user_object_or_404(IncidentSecurite, request.user, pk=pk)
    if request.method == 'POST':
        incident.delete()
        messages.success(request, "L'incident a été supprimé avec succès.")
        return redirect('fleet_app:kpi_incidents')
    
    context = {
        'incident': incident,
        'title': 'Supprimer un incident',
    }
    return render(request, 'fleet_app/incident_confirm_delete.html', context)

# Vues pour la gestion des distances parcourues
@login_required
@require_user_ownership(DistanceParcourue)
def distance_edit(request, pk):
    try:
        distance = get_user_object_or_404(DistanceParcourue, request.user, pk=pk)
        if request.method == 'POST':
            form = DistanceForm(request.POST, instance=distance)
            if form.is_valid():
                form.save()
                messages.success(request, "La distance parcourue a été modifiée avec succès.")
                return redirect('fleet_app:kpi_distance')
        else:
            form = DistanceForm(instance=distance)
        
        context = {
            'form': form,
            'distance': distance,
            'title': 'Modifier une distance parcourue',
        }
        return render(request, 'fleet_app/distance_form.html', context)
    except:
        messages.error(request, f"La distance parcourue avec l'ID {pk} n'existe pas ou a été supprimée.")
        return redirect('fleet_app:kpi_distance')

# Vues pour la gestion des consommations de carburant
# Vue dupliquée supprimée - utiliser la version sécurisée ci-dessus

# Vue dupliquée supprimée - utiliser la version sécurisée ci-dessus

# Vue dupliquée supprimée - utiliser la version sécurisée ci-dessus
    
    def get_queryset(self):
        return Alerte.objects.filter(user=self.request.user).order_by('-date_creation')



@login_required
def rapports(request):
    """Vue pour la page des rapports et analyses"""
    # Vérifier si l'utilisateur a complété son profil
    profile_check = check_profile_completion(request)
    if profile_check:
        return profile_check
        
    # Récupérer tous les véhicules pour le filtre
    vehicules = Vehicule.objects.filter(user=request.user).order_by('marque', 'modele')
    
    # Récupérer les rapports enregistrés (simulation)
    rapports_enregistres = [
        {
            'id': 1,
            'titre': 'Rapport mensuel - Juin 2025',
            'type': 'global',
            'date_creation': '2025-07-01',
            'auteur': 'Admin',
            'format': 'pdf'
        },
        {
            'id': 2,
            'titre': 'Analyse des coûts - T2 2025',
            'type': 'couts',
            'date_creation': '2025-06-30',
            'auteur': 'Admin',
            'format': 'excel'
        },
        {
            'id': 3,
            'titre': 'Consommation carburant - Mai 2025',
            'type': 'carburant',
            'date_creation': '2025-06-15',
            'auteur': 'Admin',
            'format': 'pdf'
        }
    ]
    
    # Statistiques globales pour le tableau de bord des rapports
    statistiques = {
        'cout_total': 456805000,  # Exemple de valeur en GNF
        'distance_totale': 28750,  # Exemple de valeur
        'consommation_moyenne': 7.8,  # Exemple de valeur
        'disponibilite_moyenne': 92.5,  # Exemple de valeur
        'incidents_total': 8,  # Exemple de valeur
        'utilisation_moyenne': 76.3  # Exemple de valeur
    }
    
    context = {
        'vehicules': vehicules,
        'rapports_enregistres': rapports_enregistres,
        'statistiques': statistiques,
        'titre': 'Rapports et Analyses',
        'description': 'Générez et consultez des rapports détaillés sur votre flotte de véhicules'
    }
    
    return render(request, 'fleet_app/rapports.html', context)

@login_required
def alertes(request):
    """Vue pour la page des alertes"""
    # Vérifier si l'utilisateur a complété son profil
    profile_check = check_profile_completion(request)
    if profile_check:
        return profile_check
    
    # Récupérer toutes les alertes actives
    alertes_actives = Alerte.objects.filter(statut='Active').order_by('-niveau_urgence', '-date_creation')
    
    # Pour chaque alerte concernant les coûts de fonctionnement, ajouter les montants en GNF
    for alerte in alertes_actives:
        if 'coût de fonctionnement' in alerte.type_alerte.lower():
            # Extraire les montants en euros de la description si possible
            # et les convertir en GNF pour l'affichage
            alerte.description_gnf = alerte.description
            
            # Remplacer les montants en euros par des montants en GNF dans la description
            # Format typique: "X.XX €/km" ou "X.XX euros/km"
            import re
            montants = re.findall(r'(\d+[.,]\d+)\s*[€€euros\/]*km', alerte.description, re.IGNORECASE)
            for montant_str in montants:
                try:
                    montant_eur = float(montant_str.replace(',', '.'))
                    montant_gnf = convertir_en_gnf(montant_eur)
                    montant_gnf_formatte = formater_cout_par_km_gnf(montant_eur)
                    # Ajouter l'équivalent en GNF à la description
                    nouvelle_mention = f"{montant_str} €/km ({montant_gnf_formatte})"
                    alerte.description_gnf = alerte.description_gnf.replace(f"{montant_str} €/km", nouvelle_mention)
                    alerte.description_gnf = alerte.description_gnf.replace(f"{montant_str} euros/km", nouvelle_mention)
                except ValueError:
                    pass
    
    # Récupérer l'historique des alertes résolues ou ignorées
    alertes_historique = Alerte.objects.exclude(statut='Active').order_by('-date_creation')
    
    context = {
        'alertes': alertes_actives,
        'alertes_historique': alertes_historique,
        'titre': 'Alertes',
        'description': 'Gestion des alertes du parc automobile',
        'taux_conversion': TAUX_CONVERSION_EUR_GNF,
        'devise': 'GNF'
    }
    
    return render(request, 'fleet_app/alerte_list.html', context)

@login_required
@require_user_ownership(Alerte)
def alerte_resoudre(request, pk):
    """Marquer une alerte comme résolue"""
    if request.method == 'POST':
        alerte = get_user_object_or_404(Alerte, request.user, pk=pk)
        alerte.statut = 'Résolue'
        alerte.save()
        messages.success(request, f"L'alerte '{alerte.type_alerte}' a été marquée comme résolue.")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
@require_user_ownership(Alerte)
def alerte_ignorer(request, pk):
    """Marquer une alerte comme ignorée"""
    if request.method == 'POST':
        alerte = get_user_object_or_404(Alerte, request.user, pk=pk)
        alerte.statut = 'Ignorée'
        alerte.save()
        messages.success(request, f"L'alerte '{alerte.type_alerte}' a été ignorée.")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
@login_required
@require_user_ownership(Alerte)
def alerte_supprimer(request, pk):
    """Supprimer une alerte"""
    if request.method == 'POST':
        alerte = get_user_object_or_404(Alerte, request.user, pk=pk)
        alerte.delete()
        messages.success(request, f"L'alerte '{alerte.type_alerte}' a été supprimée.")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

@login_required
def alerte_nouvelle(request):
    """Créer une nouvelle alerte"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        vehicule_id = request.POST.get('vehicule')
        type_alerte = request.POST.get('type_alerte')
        description = request.POST.get('description')
        niveau_urgence = request.POST.get('niveau_urgence')
        
        # Créer la nouvelle alerte
        try:
            vehicule = Vehicule.objects.filter(user=request.user, id_vehicule=vehicule_id).first() if vehicule_id else None
            
            alerte = Alerte(
                user=request.user,
                vehicule=vehicule,
                type_alerte=type_alerte,
                description=description,
                date_creation=timezone.now().date(),
                niveau_urgence=niveau_urgence,
                statut='Active'
            )
            alerte.save()
            messages.success(request, "Nouvelle alerte créée avec succès.")
            return redirect('fleet_app:alerte_list')
        except Exception as e:
            messages.error(request, f"Erreur lors de la création de l'alerte: {str(e)}")
            return redirect('fleet_app:alerte_list')
    
    # Afficher le formulaire de création d'alerte
    vehicules = Vehicule.objects.filter(user=request.user).order_by('marque', 'modele')
    context = {
        'vehicules': vehicules,
        'titre': 'Nouvelle alerte',
        'niveaux_urgence': Alerte.NIVEAU_CHOICES
    }
    return render(request, 'fleet_app/alerte_form.html', context)
