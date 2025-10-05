#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fichier views_management.py minimal et fonctionnel
Remplace le fichier corrompu par les suppressions automatiques
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.utils import timezone
from datetime import datetime, date, timedelta
from calendar import monthrange
import json

from .models import ArchiveMensuelle
from .models_entreprise import (
    Employe, PaieEmploye, HeureSupplementaire, ConfigurationHeureSupplementaire
)
from .forms import EmployeForm
from .utils.decorators import queryset_filter_by_tenant

@login_required
def temp_redirect_view(request, *args, **kwargs):
    """
    Vue temporaire de redirection pour les URLs en transition
    """
    messages.info(request, "Cette fonctionnalité est en cours de développement.")
    return redirect('fleet_app:dashboard')

@login_required
def employe_list(request):
    """
    Liste des employés
    """
    employes = queryset_filter_by_tenant(Employe.objects.all(), request).order_by('matricule')
    
    context = {
        'employes': employes,
        'title': 'Liste des Employés'
    }
    
    return render(request, 'fleet_app/management/employe_list.html', context)

@login_required
def paie_employe_list(request):
    """
    Liste des paies des employés
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from django.utils import timezone
    
    # Récupérer les filtres de mois/année
    mois = request.GET.get('mois')
    annee = request.GET.get('annee')
    
    # Si pas de mois/année spécifié, utiliser le mois actuel
    if not mois or not annee:
        now = timezone.now()
        mois = str(now.month)
        annee = str(now.year)
    
    # Filtrer les paies
    paies = queryset_filter_by_tenant(PaieEmploye.objects.all(), request)
    
    try:
        mois_int = int(mois)
        annee_int = int(annee)
        paies = paies.filter(mois=mois_int, annee=annee_int)
        
        # Calculer le mois précédent et suivant
        date_actuelle = datetime(annee_int, mois_int, 1)
        mois_precedent = date_actuelle - relativedelta(months=1)
        mois_suivant = date_actuelle + relativedelta(months=1)
        
        # Nom du mois actuel
        mois_noms = ['', 'Janvier', 'Février', 'Mars', 'Avril', 'Mai', 'Juin',
                    'Juillet', 'Août', 'Septembre', 'Octobre', 'Novembre', 'Décembre']
        nom_mois_actuel = mois_noms[mois_int]
    except (ValueError, IndexError):
        mois_int = timezone.now().month
        annee_int = timezone.now().year
        mois_precedent = datetime(annee_int, mois_int, 1) - relativedelta(months=1)
        mois_suivant = datetime(annee_int, mois_int, 1) + relativedelta(months=1)
        nom_mois_actuel = 'Mois actuel'
    
    paies = paies.order_by('employe__matricule')
    
    # Pagination
    paginator = Paginator(paies, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'title': 'Paies des Employés',
        'mois_filtre': mois,
        'annee_filtre': annee,
        'mois_precedent': mois_precedent.month,
        'annee_precedent': mois_precedent.year,
        'mois_suivant': mois_suivant.month,
        'annee_suivant': mois_suivant.year,
        'nom_mois_actuel': nom_mois_actuel
    }
    
    return render(request, 'fleet_app/management/paie_employe_list.html', context)

@login_required
def heure_supplementaire_list(request):
    """
    Liste des heures supplémentaires
    """
    heures_sup = queryset_filter_by_tenant(HeureSupplementaire.objects.all(), request).order_by('-date')
    
    # Filtrage par employé si spécifié
    employe_id = request.GET.get('employe_id')
    if employe_id:
        heures_sup = heures_sup.filter(employe_id=employe_id)
    
    # Filtrage par date
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if date_debut:
        heures_sup = heures_sup.filter(date__gte=date_debut)
    if date_fin:
        heures_sup = heures_sup.filter(date__lte=date_fin)
    
    # Récupérer la liste des employés pour le formulaire de filtrage
    employes = Employe.objects.filter(user=request.user).order_by('matricule')
    
    context = {
        'heures_supplementaires': heures_sup,
        'employes': employes,
        'title': 'Heures Supplémentaires'
    }
    
    return render(request, 'fleet_app/management/heure_supplementaire_list.html', context)

@login_required
def parametre_paie_list(request):
    """
    Paramètres de paie des employés
    """
    if request.method == 'POST':
        # Traitement des formulaires de modification des paramètres
        
        # Si le formulaire concerne la suppression de l'avance d'un employé
        if 'supprimer_avance' in request.POST and 'employe_id' in request.POST:
            employe_id = request.POST.get('employe_id')
            try:
                employe = queryset_filter_by_tenant(Employe.objects.all(), request).get(id=employe_id)
                # Réinitialiser l'avance à 0
                employe.avances = 0
                employe.save()
                
                messages.success(request, f"Avance pour {employe.prenom} {employe.nom} supprimée avec succès.")
            except Employe.DoesNotExist:
                messages.error(request, "Employé introuvable.")
            
            return redirect('fleet_app:parametre_paie_list')
        
        # Si le formulaire concerne la modification d'un employé spécifique
        elif 'modifier_employe' in request.POST and 'employe_id' in request.POST:
            employe_id = request.POST.get('employe_id')
            try:
                employe = queryset_filter_by_tenant(Employe.objects.all(), request).get(id=employe_id)
                
                # Mise à jour des paramètres
                taux_jour_ouvrable = request.POST.get('taux_jour_ouvrable_employe')
                avances = request.POST.get('avances_employe')
                sanctions = request.POST.get('sanctions_employe')
                montant_jour_ouvrable = request.POST.get('montant_jour_ouvrable_employe')
                
                if taux_jour_ouvrable:
                    employe.taux_jour_ouvrable = float(taux_jour_ouvrable)
                if avances:
                    employe.avances = float(avances)
                if sanctions:
                    employe.sanctions = float(sanctions)
                if montant_jour_ouvrable:
                    employe.montant_jour_ouvrable = float(montant_jour_ouvrable)
                
                employe.save()
                messages.success(request, f"Paramètres de {employe.prenom} {employe.nom} mis à jour avec succès.")
                
            except Employe.DoesNotExist:
                messages.error(request, "Employé introuvable.")
            except ValueError:
                messages.error(request, "Valeurs numériques invalides.")
            
            return redirect('fleet_app:parametre_paie_list')
    
    # Récupération des employés pour l'affichage
    employes = Employe.objects.filter(user=request.user).order_by('matricule')
    
    context = {
        'employes': employes,
        'title': 'Paramètres de Paie'
    }
    
    return render(request, 'fleet_app/management/parametre_paie_list.html', context)

@login_required
def configuration_heure_supplementaire(request):
    """
    Configuration des heures supplémentaires
    """
    # Récupérer ou créer la configuration
    config, created = ConfigurationHeureSupplementaire.objects.get_or_create(
        user=request.user,
        defaults={
            'taux_majoration': 1.5,
            'seuil_declenchement': 8.0
        }
    )
    
    if request.method == 'POST':
        taux_majoration = request.POST.get('taux_majoration')
        seuil_declenchement = request.POST.get('seuil_declenchement')
        
        try:
            if taux_majoration:
                config.taux_majoration = float(taux_majoration)
            if seuil_declenchement:
                config.seuil_declenchement = float(seuil_declenchement)
            
            config.save()
            messages.success(request, "Configuration des heures supplémentaires mise à jour avec succès.")
            
        except ValueError:
            messages.error(request, "Valeurs numériques invalides.")
        
        return redirect('fleet_app:configuration_heure_supplementaire')
    
    # Récupérer les employés
    employes = Employe.objects.filter(user=request.user).order_by('matricule')
    
    # Données pour le contexte
    from datetime import datetime
    
    mois_actuel = datetime.now().month
    annee_actuelle = datetime.now().year
    
    context = {
        'config': config,
        'created': created,
        'employes': employes,
        'mois_actuel': mois_actuel,
        'annee_actuelle': annee_actuelle,
        'title': 'Configuration Heures Supplémentaires'
    }
    
    return render(request, 'fleet_app/management/configuration_heure_supplementaire.html', context)

# Fonctions utilitaires pour la compatibilité
def get_employe_data_for_context(user):
    """
    Récupère les données des employés pour le contexte des templates
    """
    employes = Employe.objects.filter(user=user).order_by('matricule')
    employes_data = []
    
    for employe in employes:
        employe_data = {
            'employe': employe,
            'total_heures_sup': 0,
            'total_montant': 0,
        }
        employes_data.append(employe_data)
    
    return employes_data
