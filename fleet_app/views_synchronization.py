"""
Vues pour la gestion de la synchronisation en temps réel
entre tous les modules du système de paie
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from datetime import datetime
import json

from .signals import synchroniser_module_complet, verifier_coherence_donnees
from .models_entreprise import (
    Employe, PaieEmploye, PresenceJournaliere, 
    HeureSupplementaire, ConfigurationMontantEmploye,
    ParametrePaie
)


@login_required
def synchronization_dashboard(request):
    """
    Tableau de bord de synchronisation des données
    """
    # Statistiques générales
    stats = {
        'nb_employes': Employe.objects.filter(user=request.user).count(),
        'nb_paies_mois_actuel': PaieEmploye.objects.filter(
            employe__user=request.user,
            mois=datetime.now().month,
            annee=datetime.now().year
        ).count(),
        'nb_presences_mois_actuel': PresenceJournaliere.objects.filter(
            employe__user=request.user,
            date__month=datetime.now().month,
            date__year=datetime.now().year
        ).count(),
        'nb_heures_supp_mois_actuel': HeureSupplementaire.objects.filter(
            employe__user=request.user,
            date__month=datetime.now().month,
            date__year=datetime.now().year
        ).count(),
    }
    
    # Vérification de cohérence
    rapport_coherence = verifier_coherence_donnees(request.user)
    
    context = {
        'stats': stats,
        'rapport_coherence': rapport_coherence,
        'mois_actuel': datetime.now().month,
        'annee_actuelle': datetime.now().year,
    }
    
    return render(request, 'fleet_app/synchronization/dashboard.html', context)


@login_required
@require_http_methods(["POST"])
def synchroniser_donnees_ajax(request):
    """
    Synchronisation AJAX des données pour un mois donné
    """
    try:
        data = json.loads(request.body)
        mois = int(data.get('mois', datetime.now().month))
        annee = int(data.get('annee', datetime.now().year))
        
        # Lancer la synchronisation complète
        success = synchroniser_module_complet(request.user, mois, annee)
        
        if success:
            # Récupérer les nouvelles statistiques
            stats_apres = {
                'nb_employes': Employe.objects.filter(user=request.user).count(),
                'nb_paies_synchronisees': PaieEmploye.objects.filter(
                    employe__user=request.user,
                    mois=mois,
                    annee=annee
                ).count(),
            }
            
            return JsonResponse({
                'success': True,
                'message': f'Synchronisation complète réussie pour {mois}/{annee}',
                'stats': stats_apres
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Erreur lors de la synchronisation'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@login_required
@require_http_methods(["POST"])
def verifier_coherence_ajax(request):
    """
    Vérification AJAX de la cohérence des données
    """
    try:
        data = json.loads(request.body)
        mois = int(data.get('mois', datetime.now().month))
        annee = int(data.get('annee', datetime.now().year))
        
        # Vérifier la cohérence
        rapport = verifier_coherence_donnees(request.user, mois, annee)
        
        return JsonResponse({
            'success': True,
            'rapport': rapport
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Erreur: {str(e)}'
        })


@login_required
def corriger_incoherences(request):
    """
    Correction automatique des incohérences détectées
    """
    if request.method == 'POST':
        try:
            mois = int(request.POST.get('mois', datetime.now().month))
            annee = int(request.POST.get('annee', datetime.now().year))
            
            # Vérifier d'abord les incohérences
            rapport = verifier_coherence_donnees(request.user, mois, annee)
            
            corrections_effectuees = 0
            
            # Corriger les employés sans configuration montants
            for matricule in rapport['employes_sans_config_montants']:
                try:
                    employe = Employe.objects.get(matricule=matricule, user=request.user)
                    ConfigurationMontantEmploye.get_or_create_for_employe(employe)
                    corrections_effectuees += 1
                except Employe.DoesNotExist:
                    continue
            
            # Synchroniser toutes les paies problématiques
            for matricule in rapport['paies_sans_presences']:
                try:
                    employe = Employe.objects.get(matricule=matricule, user=request.user)
                    from .signals import synchroniser_paie_employe, mettre_a_jour_colonnes_presence_paie
                    mettre_a_jour_colonnes_presence_paie(employe, mois, annee)
                    synchroniser_paie_employe(employe, mois, annee)
                    corrections_effectuees += 1
                except Employe.DoesNotExist:
                    continue
            
            messages.success(
                request, 
                f'✅ {corrections_effectuees} corrections effectuées avec succès pour {mois}/{annee}'
            )
            
        except Exception as e:
            messages.error(request, f'❌ Erreur lors des corrections: {str(e)}')
    
    return redirect('fleet_app:synchronization_dashboard')


@login_required
def export_rapport_coherence(request):
    """
    Export du rapport de cohérence en JSON
    """
    try:
        mois = int(request.GET.get('mois', datetime.now().month))
        annee = int(request.GET.get('annee', datetime.now().year))
        
        rapport = verifier_coherence_donnees(request.user, mois, annee)
        
        # Ajouter des métadonnées
        rapport['meta'] = {
            'utilisateur': request.user.username,
            'mois': mois,
            'annee': annee,
            'date_export': datetime.now().isoformat(),
        }
        
        response = JsonResponse(rapport, json_dumps_params={'indent': 2})
        response['Content-Disposition'] = f'attachment; filename="rapport_coherence_{mois}_{annee}.json"'
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'error': f'Erreur lors de l\'export: {str(e)}'
        })


@login_required
def status_synchronization_api(request):
    """
    API pour obtenir le statut de synchronisation en temps réel
    """
    try:
        mois = int(request.GET.get('mois', datetime.now().month))
        annee = int(request.GET.get('annee', datetime.now().year))
        
        # Statistiques détaillées
        employes = Employe.objects.filter(user=request.user)
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'mois': mois,
            'annee': annee,
            'employes': {
                'total': employes.count(),
                'actifs': employes.filter(statut='Actif').count(),
                'inactifs': employes.filter(statut='Inactif').count(),
            },
            'presences': {
                'total': PresenceJournaliere.objects.filter(
                    employe__user=request.user,
                    date__month=mois,
                    date__year=annee
                ).count(),
            },
            'heures_supplementaires': {
                'total': HeureSupplementaire.objects.filter(
                    employe__user=request.user,
                    date__month=mois,
                    date__year=annee
                ).count(),
            },
            'paies': {
                'total': PaieEmploye.objects.filter(
                    employe__user=request.user,
                    mois=mois,
                    annee=annee
                ).count(),
            },
            'configurations': {
                'montants_employes': ConfigurationMontantEmploye.objects.filter(
                    employe__user=request.user
                ).count(),
                'parametres_paie': ParametrePaie.objects.filter(
                    user=request.user
                ).count(),
            }
        }
        
        # Vérification rapide de cohérence
        rapport = verifier_coherence_donnees(request.user, mois, annee)
        status['coherence'] = {
            'statut': rapport['statut'],
            'nb_problemes': sum(len(rapport[key]) for key in rapport if key != 'statut')
        }
        
        return JsonResponse(status)
        
    except Exception as e:
        return JsonResponse({
            'error': f'Erreur: {str(e)}'
        })


@login_required
def relations_modules_info(request):
    """
    Informations sur les relations entre modules
    """
    relations_info = {
        'employes_to_presences': {
            'relation': 'OneToMany (ForeignKey)',
            'description': 'Un employé peut avoir plusieurs présences journalières',
            'synchronisation': 'Automatique via signaux Django'
        },
        'employes_to_paies': {
            'relation': 'OneToMany (ForeignKey)', 
            'description': 'Un employé peut avoir plusieurs paies mensuelles',
            'synchronisation': 'Automatique via signaux Django'
        },
        'employes_to_heures_supp': {
            'relation': 'OneToMany (ForeignKey)',
            'description': 'Un employé peut avoir plusieurs heures supplémentaires',
            'synchronisation': 'Automatique via signaux Django'
        },
        'employes_to_config_montants': {
            'relation': 'OneToOne (ForeignKey)',
            'description': 'Chaque employé a sa configuration de montants personnalisée',
            'synchronisation': 'Création automatique si manquante'
        },
        'presences_to_paies': {
            'relation': 'Calculée (via employé + mois/année)',
            'description': 'Les présences sont agrégées dans les paies mensuelles',
            'synchronisation': 'Temps réel via signaux post_save/post_delete'
        },
        'heures_supp_to_paies': {
            'relation': 'Calculée (via employé + mois/année)',
            'description': 'Les heures supp sont totalisées dans les paies mensuelles',
            'synchronisation': 'Temps réel via signaux post_save/post_delete'
        },
        'paies_to_bulletins': {
            'relation': 'OneToOne (même enregistrement)',
            'description': 'Chaque paie génère un bulletin imprimable',
            'synchronisation': 'Instantanée (même données)'
        },
        'paies_to_archives': {
            'relation': 'Sérialisée (JSON)',
            'description': 'Les paies sont archivées mensuellement en JSON',
            'synchronisation': 'Manuelle via interface archives'
        }
    }
    
    return JsonResponse(relations_info, json_dumps_params={'indent': 2})
