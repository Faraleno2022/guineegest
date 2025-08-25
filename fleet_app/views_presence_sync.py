"""
Vues pour la synchronisation automatique des données de présence vers les paies
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime
import json

from .utils_presence_paie import (
    synchroniser_tous_employes_mois,
    generer_rapport_presence_mois,
    verifier_coherence_presence_paie,
    calculer_statistiques_presence
)
from .models_entreprise import Employe, PaieEmploye


@login_required
def synchroniser_presence_paie_view(request):
    """
    Vue pour synchroniser manuellement les données de présence vers les paies
    """
    if request.method == 'POST':
        mois = int(request.POST.get('mois', datetime.now().month))
        annee = int(request.POST.get('annee', datetime.now().year))
        
        try:
            # Synchroniser tous les employés pour le mois
            rapport = synchroniser_tous_employes_mois(request.user, mois, annee)
            
            # Messages de succès
            if rapport['employes_crees'] > 0:
                messages.success(
                    request, 
                    f"✅ {rapport['employes_crees']} nouvelles paies créées pour {mois:02d}/{annee}"
                )
            
            if rapport['employes_mis_a_jour'] > 0:
                messages.success(
                    request, 
                    f"🔄 {rapport['employes_mis_a_jour']} paies mises à jour pour {mois:02d}/{annee}"
                )
            
            # Messages d'erreur
            if rapport['erreurs']:
                for erreur in rapport['erreurs']:
                    messages.error(
                        request,
                        f"❌ Erreur pour {erreur['employe']['nom']}: {erreur['erreur']}"
                    )
            
            # Stocker le rapport en session pour affichage
            request.session['rapport_sync'] = rapport
            
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la synchronisation: {str(e)}")
    
    # Récupérer le rapport s'il existe
    rapport = request.session.pop('rapport_sync', None)
    
    context = {
        'rapport': rapport,
        'mois_actuel': datetime.now().month,
        'annee_actuelle': datetime.now().year,
        'mois_noms': [
            (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
            (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
            (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre')
        ]
    }
    
    return render(request, 'fleet_app/entreprise/synchroniser_presence_paie.html', context)


@login_required
def rapport_presence_mois_view(request):
    """
    Vue pour afficher le rapport détaillé des présences d'un mois
    """
    mois = int(request.GET.get('mois', datetime.now().month))
    annee = int(request.GET.get('annee', datetime.now().year))
    
    try:
        rapport = generer_rapport_presence_mois(request.user, mois, annee)
        
        context = {
            'rapport': rapport,
            'mois': mois,
            'annee': annee,
            'mois_noms': {
                1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
                5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
                9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
            }
        }
        
    except Exception as e:
        messages.error(request, f"❌ Erreur lors de la génération du rapport: {str(e)}")
        context = {'rapport': None, 'mois': mois, 'annee': annee}
    
    return render(request, 'fleet_app/entreprise/rapport_presence_mois.html', context)


@login_required
def verifier_coherence_view(request):
    """
    Vue pour vérifier la cohérence entre présences et paies
    """
    mois = int(request.GET.get('mois', datetime.now().month))
    annee = int(request.GET.get('annee', datetime.now().year))
    
    try:
        rapport = verifier_coherence_presence_paie(request.user, mois, annee)
        
        context = {
            'rapport': rapport,
            'mois': mois,
            'annee': annee,
            'mois_noms': {
                1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
                5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
                9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
            }
        }
        
        # Messages selon le résultat
        if rapport['employes_incoherents'] == 0:
            messages.success(request, f"✅ Toutes les données sont cohérentes pour {mois:02d}/{annee}")
        else:
            messages.warning(
                request, 
                f"⚠️ {rapport['employes_incoherents']} employé(s) ont des incohérences pour {mois:02d}/{annee}"
            )
        
    except Exception as e:
        messages.error(request, f"❌ Erreur lors de la vérification: {str(e)}")
        context = {'rapport': None, 'mois': mois, 'annee': annee}
    
    return render(request, 'fleet_app/entreprise/verifier_coherence.html', context)


@login_required
@require_http_methods(["POST"])
def synchroniser_presence_ajax(request):
    """
    API AJAX pour synchroniser les données de présence
    """
    try:
        data = json.loads(request.body)
        mois = int(data.get('mois', datetime.now().month))
        annee = int(data.get('annee', datetime.now().year))
        employe_id = data.get('employe_id')  # Optionnel pour un employé spécifique
        
        if employe_id:
            # Synchroniser un employé spécifique
            employe = Employe.objects.get(id=employe_id, user=request.user)
            from .utils_presence_paie import synchroniser_presence_vers_paie
            paie_employe, created, stats = synchroniser_presence_vers_paie(employe, mois, annee)
            
            return JsonResponse({
                'success': True,
                'message': f"Synchronisation réussie pour {employe.prenom} {employe.nom}",
                'created': created,
                'statistiques': stats
            })
        else:
            # Synchroniser tous les employés
            rapport = synchroniser_tous_employes_mois(request.user, mois, annee)
            
            return JsonResponse({
                'success': True,
                'message': f"Synchronisation réussie pour {rapport['employes_synchronises']} employé(s)",
                'rapport': rapport
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def statistiques_employe_ajax(request):
    """
    API AJAX pour récupérer les statistiques de présence d'un employé
    """
    try:
        employe_id = request.GET.get('employe_id')
        mois = int(request.GET.get('mois', datetime.now().month))
        annee = int(request.GET.get('annee', datetime.now().year))
        
        employe = Employe.objects.get(id=employe_id, user=request.user)
        stats = calculer_statistiques_presence(employe, mois, annee)
        
        return JsonResponse({
            'success': True,
            'employe': {
                'id': employe.id,
                'matricule': employe.matricule,
                'nom': f"{employe.prenom} {employe.nom}"
            },
            'statistiques': stats
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@login_required
def dashboard_presence_paie(request):
    """
    Dashboard pour la gestion de la synchronisation présence-paie
    """
    mois = int(request.GET.get('mois', datetime.now().month))
    annee = int(request.GET.get('annee', datetime.now().year))
    
    try:
        # Générer les rapports
        rapport_presence = generer_rapport_presence_mois(request.user, mois, annee)
        rapport_coherence = verifier_coherence_presence_paie(request.user, mois, annee)
        
        # Statistiques globales
        employes_total = Employe.objects.filter(user=request.user, statut='Actif').count()
        paies_existantes = PaieEmploye.objects.filter(
            employe__user=request.user,
            mois=mois,
            annee=annee
        ).count()
        
        context = {
            'mois': mois,
            'annee': annee,
            'rapport_presence': rapport_presence,
            'rapport_coherence': rapport_coherence,
            'statistiques_globales': {
                'employes_total': employes_total,
                'paies_existantes': paies_existantes,
                'paies_manquantes': employes_total - paies_existantes,
                'coherence_ok': rapport_coherence['employes_coherents'],
                'coherence_ko': rapport_coherence['employes_incoherents']
            },
            'mois_noms': {
                1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
                5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
                9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
            }
        }
        
    except Exception as e:
        messages.error(request, f"❌ Erreur lors du chargement du dashboard: {str(e)}")
        context = {
            'mois': mois,
            'annee': annee,
            'rapport_presence': None,
            'rapport_coherence': None
        }
    
    return render(request, 'fleet_app/entreprise/dashboard_presence_paie.html', context)
