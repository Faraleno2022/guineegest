from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from .security import user_owns_data, user_owns_related_data
from django.db.models import Count, Sum
from django.core.paginator import Paginator
import csv
from .models_entreprise import (
    Employe, PresenceJournaliere, PaieEmploye, HeureSupplementaire, ParametrePaie
)
from django.forms import modelform_factory
from .forms_entreprise import EmployeForm

@login_required
def employe_list(request):
    """
    Vue pour afficher la liste des employés
    """
    queryset = Employe.objects.filter(user=request.user).order_by('nom', 'prenom')
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employes': page_obj,
        'page_obj': page_obj,
        'total_employes': queryset.count(),
    }
    
    return render(request, 'fleet_app/entreprise/employe_list.html', context)

@login_required
@user_owns_data(Employe, relation_path=['user'])
def employe_detail(request, pk):
    """
    Vue pour afficher les détails d'un employé avec statistiques complètes
    Sécurisée pour garantir que l'utilisateur ne peut accéder qu'à ses propres données
    """
    employe = get_object_or_404(Employe, pk=pk)
    
    # Récupérer toutes les présences pour les statistiques d'abord
    all_presences = PresenceJournaliere.objects.filter(employe=employe).order_by('-date')
    
    # Calculer les statistiques de présence (30 derniers jours)
    presences_30_jours = all_presences[:30]
    total_presences = len(presences_30_jours)
    
    # Compter les différents types de statuts
    jours_presence = sum(1 for p in presences_30_jours if p.statut in ['P(Am)', 'P(Pm)', 'P(Am&Pm)', 'present_am', 'present_pm', 'present_journee'])
    jours_absence = sum(1 for p in presences_30_jours if p.statut in ['A', 'absent'])
    jours_maladie = sum(1 for p in presences_30_jours if p.statut in ['M', 'maladie'])
    jours_maladie_payee = sum(1 for p in presences_30_jours if p.statut in ['M(Payer)', 'maladie_payee'])
    jours_repos = sum(1 for p in presences_30_jours if p.statut in ['OFF', 'repos'])
    jours_dimanche = sum(1 for p in presences_30_jours if p.statut in ['D', 'dimanche'])
    jours_ferie = sum(1 for p in presences_30_jours if p.statut in ['Fér', 'ferie'])
    jours_conge = sum(1 for p in presences_30_jours if p.statut in ['C', 'conge'])
    jours_formation = sum(1 for p in presences_30_jours if p.statut in ['F', 'formation'])
    
    # Récupérer les 30 dernières présences pour l'affichage
    presences = presences_30_jours
    
    # Récupérer les 5 dernières paies
    paies = PaieEmploye.objects.filter(employe=employe).order_by('-annee', '-mois')[:5]
    
    # Récupérer les 10 dernières heures supplémentaires
    heures_sup = HeureSupplementaire.objects.filter(employe=employe).order_by('-date')[:10]
    
    # Calculer les statistiques d'heures supplémentaires
    total_heures_sup = sum(hs.duree for hs in heures_sup) if heures_sup else 0
    total_montant_sup = sum(hs.calculer_montant_supplementaire_simple() for hs in heures_sup) if heures_sup else 0
    
    # Calculer le montant total des paies
    total_salaire_brut = sum(paie.salaire_brut for paie in paies) if paies else 0
    total_salaire_net = sum(paie.salaire_net for paie in paies) if paies else 0
    
    context = {
        'employe': employe,
        'presences': presences,
        'paies': paies,
        'heures_sup': heures_sup,
        # Statistiques de présence
        'stats_presence': {
            'total_presences': total_presences,
            'jours_presence': jours_presence,
            'jours_absence': jours_absence,
            'jours_maladie': jours_maladie,
            'jours_maladie_payee': jours_maladie_payee,
            'jours_repos': jours_repos,
            'jours_dimanche': jours_dimanche,
            'jours_ferie': jours_ferie,
            'jours_conge': jours_conge,
            'jours_formation': jours_formation,
        },
        # Statistiques d'heures supplémentaires
        'stats_heures_sup': {
            'total_heures': float(total_heures_sup),
            'total_montant': float(total_montant_sup),
        },
        # Statistiques de paie
        'stats_paie': {
            'total_brut': float(total_salaire_brut),
            'total_net': float(total_salaire_net),
        },
    }
    
    return render(request, 'fleet_app/entreprise/employe_detail.html', context)
