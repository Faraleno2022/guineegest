from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.db.models import Sum, Count, Q, Avg
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.http import JsonResponse
import calendar
from collections import defaultdict

from .models import Vehicule, FeuilleDeRoute, CoutFonctionnement, ConsommationCarburant
from .models_location import LocationVehicule, FeuillePontageLocation, FactureLocation
from .models_inventaire import EntreeStock, SortieStock


@login_required
def vehicule_stats_dashboard(request):
    """Dashboard principal des statistiques véhicules"""
    user = request.user
    
    # Période par défaut : mois en cours
    today = timezone.now().date()
    start_date = today.replace(day=1)
    end_date = today
    
    # Récupérer les paramètres de date si fournis
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    vehicules = Vehicule.objects.filter(user=user)
    
    # Statistiques globales
    stats_globales = {
        'total_vehicules': vehicules.count(),
        'vehicules_actifs': vehicules.filter(statut_actuel='Actif').count(),
        'vehicules_inactifs': vehicules.filter(statut_actuel='Inactif').count(),
        'vehicules_entretien': vehicules.filter(statut_actuel='En entretien').count(),
        'vehicules_hors_service': vehicules.filter(statut_actuel='Hors service').count(),
    }
    
    # Statistiques par véhicule pour la période
    vehicules_stats = []
    for vehicule in vehicules:
        stats = calculer_stats_vehicule(vehicule, start_date, end_date, user)
        vehicules_stats.append({
            'vehicule': vehicule,
            'stats': stats
        })
    
    # Statistiques d'entretien globales
    stats_entretien = calculer_stats_entretien_globales(user, start_date, end_date)
    
    # Statistiques de location globales
    stats_location = calculer_stats_location_globales(user, start_date, end_date)
    
    context = {
        'stats_globales': stats_globales,
        'vehicules_stats': vehicules_stats,
        'stats_entretien': stats_entretien,
        'stats_location': stats_location,
        'start_date': start_date,
        'end_date': end_date,
        'periode_jours': (end_date - start_date).days + 1,
    }
    
    return render(request, 'fleet_app/stats/vehicule_stats_dashboard.html', context)


@login_required
def vehicule_stats_detail(request, vehicule_id):
    """Statistiques détaillées d'un véhicule spécifique"""
    vehicule = get_object_or_404(Vehicule, pk=vehicule_id, user=request.user)
    
    # Période par défaut : 3 derniers mois
    today = timezone.now().date()
    start_date = today - timedelta(days=90)
    end_date = today
    
    # Récupérer les paramètres de date si fournis
    if request.GET.get('start_date'):
        start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Calculer les statistiques détaillées
    stats = calculer_stats_vehicule_detaillees(vehicule, start_date, end_date, request.user)
    
    # Données pour les graphiques
    stats_mensuelles = calculer_stats_mensuelles(vehicule, start_date, end_date, request.user)
    
    context = {
        'vehicule': vehicule,
        'stats': stats,
        'stats_mensuelles': stats_mensuelles,
        'start_date': start_date,
        'end_date': end_date,
    }
    
    return render(request, 'fleet_app/stats/vehicule_stats_detail.html', context)


def calculer_stats_vehicule(vehicule, start_date, end_date, user):
    """Calcule les statistiques d'un véhicule pour une période donnée"""
    
    # Jours d'activité via feuilles de route
    feuilles_route = FeuilleDeRoute.objects.filter(
        vehicule=vehicule,
        date_depart__range=[start_date, end_date]
    )
    
    # Calculer les jours d'activité basés sur les feuilles de route complétées
    jours_actifs = feuilles_route.filter(date_retour__isnull=False, signature_chauffeur=True).count()
    jours_inactifs = 0  # Pas de statut inactif dans le modèle
    jours_entretien = 0  # Pas de statut entretien dans le modèle
    jours_hors_service = 0  # Pas de statut hors service dans le modèle
    
    # Jours d'activité via locations
    locations = LocationVehicule.objects.filter(
        vehicule=vehicule,
        user=user,
        date_debut__lte=end_date,
        date_fin__gte=start_date
    )
    
    jours_location_travail = 0
    jours_location_entretien = 0
    jours_location_hs = 0
    
    for location in locations:
        pontages = FeuillePontageLocation.objects.filter(
            location=location,
            date__range=[start_date, end_date],
            user=user
        )
        jours_location_travail += pontages.filter(statut='Travail').count()
        jours_location_entretien += pontages.filter(statut='Entretien').count()
        jours_location_hs += pontages.filter(statut='Hors service').count()
    
    # Coûts d'entretien
    couts_entretien = CoutFonctionnement.objects.filter(
        vehicule=vehicule,
        date__range=[start_date, end_date],
        type_cout='Entretien',
        user=user
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Pièces utilisées (sorties de stock) - filtrage par destination contenant l'immatriculation
    pieces_utilisees = SortieStock.objects.filter(
        destination__icontains=vehicule.immatriculation,
        date__range=[start_date, end_date],
        entreprise__profil__user=user
    ).aggregate(
        total_pieces=Sum('quantite'),
        valeur_pieces=Sum('quantite')  # Pas de prix_unitaire dans SortieStock
    )
    
    # Consommation carburant
    consommation = ConsommationCarburant.objects.filter(
        vehicule=vehicule,
        date_plein2__range=[start_date, end_date],
        user=user
    ).aggregate(
        total_litres=Sum('litres_ajoutes'),
        total_cout=Sum('litres_ajoutes')  # ConsommationCarburant n'a pas de champ cout_total
    )
    
    # Frais de location
    frais_location = calculer_frais_location(vehicule, start_date, end_date, user)
    
    return {
        'jours_actifs': jours_actifs + jours_location_travail,
        'jours_inactifs': jours_inactifs,
        'jours_entretien': jours_entretien + jours_location_entretien,
        'jours_hors_service': jours_hors_service + jours_location_hs,
        'cout_entretien': couts_entretien,
        'pieces_utilisees': pieces_utilisees['total_pieces'] or 0,
        'valeur_pieces': pieces_utilisees['valeur_pieces'] or 0,
        'consommation_litres': consommation['total_litres'] or 0,
        'cout_carburant': consommation['total_cout'] or 0,
        'frais_location': frais_location,
    }


def calculer_stats_vehicule_detaillees(vehicule, start_date, end_date, user):
    """Calcule les statistiques détaillées d'un véhicule"""
    
    stats_base = calculer_stats_vehicule(vehicule, start_date, end_date, user)
    
    # Calculs additionnels
    total_jours = (end_date - start_date).days + 1
    
    # Pourcentages d'utilisation
    pourcentage_actif = (stats_base['jours_actifs'] / total_jours * 100) if total_jours > 0 else 0
    pourcentage_entretien = (stats_base['jours_entretien'] / total_jours * 100) if total_jours > 0 else 0
    pourcentage_hs = (stats_base['jours_hors_service'] / total_jours * 100) if total_jours > 0 else 0
    
    # Coût par jour d'utilisation
    jours_utilisation = stats_base['jours_actifs'] + stats_base['jours_entretien']
    cout_total = (stats_base['cout_entretien'] + stats_base['valeur_pieces'] + 
                  stats_base['cout_carburant'] + stats_base['frais_location']['total'])
    
    cout_par_jour = cout_total / jours_utilisation if jours_utilisation > 0 else 0
    
    # Consommation moyenne
    consommation_moyenne = (stats_base['consommation_litres'] / stats_base['jours_actifs'] 
                           if stats_base['jours_actifs'] > 0 else 0)
    
    # Calcul de rentabilité
    rentabilite = stats_base['frais_location']['total'] - cout_total
    
    stats_base.update({
        'total_jours': total_jours,
        'pourcentage_actif': round(pourcentage_actif, 1),
        'pourcentage_entretien': round(pourcentage_entretien, 1),
        'pourcentage_hs': round(pourcentage_hs, 1),
        'cout_total': cout_total,
        'cout_par_jour': cout_par_jour,
        'consommation_moyenne': round(consommation_moyenne, 2),
        'rentabilite': rentabilite,
    })
    
    return stats_base


def calculer_frais_location(vehicule, start_date, end_date, user):
    """Calcule les frais de location pour un véhicule"""
    
    locations = LocationVehicule.objects.filter(
        vehicule=vehicule,
        user=user,
        date_debut__lte=end_date,
        date_fin__gte=start_date
    )
    
    frais_journaliers = 0
    jours_factures = 0
    
    for location in locations:
        # Calculer les jours de travail facturables dans la période
        pontages = FeuillePontageLocation.objects.filter(
            location=location,
            date__range=[start_date, end_date],
            statut='Travail',
            user=user
        )
        
        jours_travail = pontages.count()
        frais_journaliers += jours_travail * location.tarif_journalier
        jours_factures += jours_travail
    
    # Calculs mensuels et annuels (estimations basées sur les données actuelles)
    frais_mensuels = (frais_journaliers / ((end_date - start_date).days + 1)) * 30 if frais_journaliers > 0 else 0
    frais_annuels = frais_mensuels * 12
    
    return {
        'journalier': frais_journaliers,
        'mensuel': frais_mensuels,
        'annuel': frais_annuels,
        'total': frais_journaliers,
        'jours_factures': jours_factures,
    }


def calculer_stats_entretien_globales(user, start_date, end_date):
    """Calcule les statistiques d'entretien globales"""
    
    # Coûts d'entretien par type
    couts_entretien = CoutFonctionnement.objects.filter(
        user=user,
        date__range=[start_date, end_date],
        type_cout='Entretien'
    ).aggregate(total=Sum('montant'))['total'] or 0
    
    # Nombre d'interventions d'entretien
    interventions = CoutFonctionnement.objects.filter(
        user=user,
        date__range=[start_date, end_date],
        type_cout='Entretien'
    ).count()
    
    # Pièces détachées utilisées
    pieces_stats = SortieStock.objects.filter(
        entreprise__profil__user=user,
        date__range=[start_date, end_date]
    ).aggregate(
        total_pieces=Sum('quantite'),
        valeur_totale=Sum('quantite')  # Pas de prix_unitaire dans SortieStock
    )
    
    return {
        'cout_total': couts_entretien,
        'nombre_interventions': interventions,
        'pieces_utilisees': pieces_stats['total_pieces'] or 0,
        'valeur_pieces': pieces_stats['valeur_totale'] or 0,
        'cout_moyen_intervention': couts_entretien / interventions if interventions > 0 else 0,
    }


def calculer_stats_location_globales(user, start_date, end_date):
    """Calcule les statistiques de location globales"""
    
    locations = LocationVehicule.objects.filter(
        user=user,
        date_debut__lte=end_date,
        date_fin__gte=start_date
    )
    
    revenus_totaux = 0
    jours_location_totaux = 0
    
    for location in locations:
        pontages = FeuillePontageLocation.objects.filter(
            location=location,
            date__range=[start_date, end_date],
            statut='Travail',
            user=user
        )
        
        jours_travail = pontages.count()
        revenus_totaux += jours_travail * location.tarif_journalier
        jours_location_totaux += jours_travail
    
    return {
        'revenus_totaux': revenus_totaux,
        'jours_location_totaux': jours_location_totaux,
        'nombre_locations': locations.count(),
        'revenu_moyen_jour': revenus_totaux / jours_location_totaux if jours_location_totaux > 0 else 0,
    }


def calculer_stats_mensuelles(vehicule, start_date, end_date, user):
    """Calcule les statistiques mensuelles pour les graphiques"""
    
    stats_par_mois = defaultdict(lambda: {
        'jours_actifs': 0,
        'jours_entretien': 0,
        'cout_entretien': 0,
        'cout_carburant': 0,
        'frais_location': 0,
    })
    
    # Parcourir chaque mois dans la période
    current_date = start_date.replace(day=1)
    while current_date <= end_date:
        # Dernier jour du mois
        last_day = calendar.monthrange(current_date.year, current_date.month)[1]
        month_end = current_date.replace(day=last_day)
        
        # Limiter à la période demandée
        period_start = max(current_date, start_date)
        period_end = min(month_end, end_date)
        
        # Calculer les stats pour ce mois
        stats_mois = calculer_stats_vehicule(vehicule, period_start, period_end, user)
        
        mois_key = current_date.strftime('%Y-%m')
        stats_par_mois[mois_key] = {
            'mois': current_date.strftime('%B %Y'),
            'jours_actifs': stats_mois['jours_actifs'],
            'jours_entretien': stats_mois['jours_entretien'],
            'cout_entretien': stats_mois['cout_entretien'],
            'cout_carburant': stats_mois['cout_carburant'],
            'frais_location': stats_mois['frais_location']['total'],
        }
        
        # Passer au mois suivant
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    return dict(stats_par_mois)


@login_required
def vehicule_stats_export(request):
    """Export des statistiques en JSON pour les graphiques"""
    
    vehicule_id = request.GET.get('vehicule_id')
    start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    if vehicule_id:
        vehicule = get_object_or_404(Vehicule, pk=vehicule_id, user=request.user)
        stats = calculer_stats_mensuelles(vehicule, start_date, end_date, request.user)
    else:
        # Statistiques globales
        vehicules = Vehicule.objects.filter(user=request.user)
        stats = {}
        for vehicule in vehicules:
            stats[str(vehicule.pk)] = calculer_stats_mensuelles(vehicule, start_date, end_date, request.user)
    
    return JsonResponse(stats)


@login_required
def vehicule_comparaison_stats(request):
    """Comparaison des statistiques entre plusieurs véhicules"""
    
    vehicule_ids = request.GET.getlist('vehicules')
    start_date = datetime.strptime(request.GET.get('start_date', '2024-01-01'), '%Y-%m-%d').date()
    end_date = datetime.strptime(request.GET.get('end_date', str(timezone.now().date())), '%Y-%m-%d').date()
    
    vehicules_stats = []
    
    if vehicule_ids:
        vehicules = Vehicule.objects.filter(pk__in=vehicule_ids, user=request.user)
        
        for vehicule in vehicules:
            stats = calculer_stats_vehicule_detaillees(vehicule, start_date, end_date, request.user)
            vehicules_stats.append({
                'vehicule': vehicule,
                'stats': stats
            })
    else:
        # Si aucun véhicule sélectionné, prendre tous les véhicules
        vehicules = Vehicule.objects.filter(user=request.user)[:5]  # Limiter à 5 pour la lisibilité
        
        for vehicule in vehicules:
            stats = calculer_stats_vehicule_detaillees(vehicule, start_date, end_date, request.user)
            vehicules_stats.append({
                'vehicule': vehicule,
                'stats': stats
            })
    
    context = {
        'vehicules_stats': vehicules_stats,
        'start_date': start_date,
        'end_date': end_date,
        'tous_vehicules': Vehicule.objects.filter(user=request.user),
        'vehicules_selectionnes': vehicule_ids,
    }
    
    return render(request, 'fleet_app/stats/vehicule_comparaison.html', context)
