"""
Vue améliorée pour les paies avec intégration automatique des calculs de présence
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from datetime import datetime
from decimal import Decimal

from .models_entreprise import PaieEmploye, Employe, PresenceJournaliere, HeureSupplementaire
from .utils_presence_paie import (
    calculer_statistiques_presence,
    synchroniser_presence_vers_paie,
    synchroniser_tous_employes_mois
)


@login_required
def paie_employe_list_enhanced(request):
    """
    Vue améliorée pour afficher la liste des paies avec calculs automatiques de présence
    """
    # Récupérer les filtres
    employe_id = request.GET.get('employe_id')
    annee = int(request.GET.get('annee', datetime.now().year))
    mois = int(request.GET.get('mois', datetime.now().month))
    auto_sync = request.GET.get('auto_sync', 'false') == 'true'
    
    # Si auto_sync est activé, synchroniser automatiquement les données
    if auto_sync:
        try:
            rapport = synchroniser_tous_employes_mois(request.user, mois, annee)
            if rapport['employes_synchronises'] > 0:
                messages.success(
                    request, 
                    f"✅ {rapport['employes_synchronises']} paie(s) synchronisée(s) automatiquement pour {mois:02d}/{annee}"
                )
        except Exception as e:
            messages.warning(request, f"⚠️ Synchronisation automatique échouée: {str(e)}")
    
    # Récupérer les paies filtrées
    paies = PaieEmploye.objects.filter(
        employe__user=request.user,
        mois=mois,
        annee=annee
    ).select_related('employe').order_by('employe__matricule')
    
    if employe_id:
        paies = paies.filter(employe_id=employe_id)
    
    # Récupérer tous les employés pour les filtres
    employes = Employe.objects.filter(user=request.user, statut='Actif').order_by('matricule')
    
    # Calculer les statistiques enrichies pour chaque paie
    paies_enrichies = []
    total_global = {
        'jours_presence': 0,
        'sundays': 0,
        'absences': 0,
        'maladies': 0,
        'maladies_payees': 0,
        'jours_repos': 0,
        'salaire_brut': Decimal('0'),
        'salaire_net': Decimal('0')
    }
    
    for paie in paies:
        # Calculer les statistiques de présence en temps réel
        stats_presence = calculer_statistiques_presence(paie.employe, mois, annee)
        
        # Vérifier la cohérence avec les données stockées
        coherence = {
            'jours_presence': paie.jours_presence == stats_presence['jours_presence'],
            'dimanches': paie.dimanches == stats_presence['sundays'],
            'absences': paie.absences == stats_presence['absent'],
            'jours_repos': paie.jours_repos == stats_presence['j_repos']
        }
        
        # Calculer les heures supplémentaires
        heures_sup = HeureSupplementaire.objects.filter(
            employe=paie.employe,
            date__month=mois,
            date__year=annee
        )
        total_heures_sup = sum(hs.duree for hs in heures_sup)
        # Utiliser le champ existant total_a_payer (déjà utilisé ailleurs) au lieu d'une méthode inexistante
        total_montant_sup = sum(getattr(hs, 'total_a_payer', 0) for hs in heures_sup)
        
        paie_enrichie = {
            'paie': paie,
            'stats_presence_calculees': stats_presence,
            'coherence': coherence,
            'coherence_globale': all(coherence.values()),
            'heures_supplementaires': {
                'total_heures': float(total_heures_sup) if total_heures_sup else 0,
                'total_montant': float(total_montant_sup) if total_montant_sup else 0,
                'nombre_entrees': heures_sup.count()
            },
            'pourcentage_presence': round(
                (stats_presence['jours_presence'] / stats_presence['total_jours_mois']) * 100, 1
            ) if stats_presence['total_jours_mois'] > 0 else 0
        }
        
        paies_enrichies.append(paie_enrichie)
        
        # Mettre à jour les totaux globaux
        total_global['jours_presence'] += stats_presence['jours_presence']
        total_global['sundays'] += stats_presence['sundays']
        total_global['absences'] += stats_presence['absent']
        total_global['maladies'] += stats_presence['maladies']
        total_global['maladies_payees'] += stats_presence['m_payer']
        total_global['jours_repos'] += stats_presence['j_repos']
        total_global['salaire_brut'] += paie.salaire_brut
        total_global['salaire_net'] += paie.salaire_net
    
    # Détecter les employés sans paie pour cette période
    employes_avec_paie = set(paie.employe.id for paie in paies)
    employes_sans_paie = employes.exclude(id__in=employes_avec_paie)
    
    # Statistiques de cohérence
    paies_coherentes = sum(1 for p in paies_enrichies if p['coherence_globale'])
    paies_incoherentes = len(paies_enrichies) - paies_coherentes
    
    context = {
        'paies_enrichies': paies_enrichies,
        'employes': employes,
        'employes_sans_paie': employes_sans_paie,
        'employe_id': employe_id,
        'annee': annee,
        'mois': mois,
        'auto_sync': auto_sync,
        'total_global': total_global,
        'statistiques_periode': {
            'total_employes': employes.count(),
            'employes_avec_paie': len(paies_enrichies),
            'employes_sans_paie': employes_sans_paie.count(),
            'paies_coherentes': paies_coherentes,
            'paies_incoherentes': paies_incoherentes,
            'pourcentage_coherence': round(
                (paies_coherentes / len(paies_enrichies)) * 100, 1
            ) if paies_enrichies else 0
        },
        'mois_noms': {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
            5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
            9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        },
        'formules_calcul': {
            'jours_presence': 'P(Am_&_Pm) + P(Pm) + P(Am)',
            'sundays': 'P(dim_Am) + P(dim_Pm) + P(dim_Am_&_Pm)',
            'absent': 'nombre de A',
            'maladies': 'nombre de M',
            'm_payer': 'nombre de M(Payer)',
            'j_repos': 'nombre de OFF'
        }
    }
    
    return render(request, 'fleet_app/entreprise/paie_employe_list_enhanced.html', context)


@login_required
def paie_employe_detail_enhanced(request, paie_id):
    """
    Vue détaillée d'une paie avec calculs de présence en temps réel
    """
    paie = get_object_or_404(PaieEmploye, id=paie_id, employe__user=request.user)
    
    # Calculer les statistiques de présence
    stats_presence = calculer_statistiques_presence(paie.employe, paie.mois, paie.annee)
    
    # Récupérer les présences détaillées du mois
    presences = PresenceJournaliere.objects.filter(
        employe=paie.employe,
        date__month=paie.mois,
        date__year=paie.annee
    ).order_by('date')
    
    # Récupérer les heures supplémentaires du mois
    heures_sup = HeureSupplementaire.objects.filter(
        employe=paie.employe,
        date__month=paie.mois,
        date__year=paie.annee
    ).order_by('date')
    
    # Vérifier la cohérence
    coherence = {
        'jours_presence': {
            'stocke': paie.jours_presence,
            'calcule': stats_presence['jours_presence'],
            'coherent': paie.jours_presence == stats_presence['jours_presence']
        },
        'dimanches': {
            'stocke': paie.dimanches,
            'calcule': stats_presence['sundays'],
            'coherent': paie.dimanches == stats_presence['sundays']
        },
        'absences': {
            'stocke': paie.absences,
            'calcule': stats_presence['absent'],
            'coherent': paie.absences == stats_presence['absent']
        },
        'jours_repos': {
            'stocke': paie.jours_repos,
            'calcule': stats_presence['j_repos'],
            'coherent': paie.jours_repos == stats_presence['j_repos']
        }
    }
    
    context = {
        'paie': paie,
        'stats_presence': stats_presence,
        'presences': presences,
        'heures_sup': heures_sup,
        'coherence': coherence,
        'coherence_globale': all(c['coherent'] for c in coherence.values()),
        'mois_nom': {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
            5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
            9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }.get(paie.mois, f'Mois {paie.mois}')
    }
    
    return render(request, 'fleet_app/entreprise/paie_employe_detail_enhanced.html', context)


@login_required
def synchroniser_paie_individuelle(request, employe_id):
    """
    Synchroniser les données de présence pour un employé spécifique
    """
    if request.method == 'POST':
        try:
            employe = get_object_or_404(Employe, id=employe_id, user=request.user)
            mois = int(request.POST.get('mois', datetime.now().month))
            annee = int(request.POST.get('annee', datetime.now().year))
            
            paie_employe, created, stats = synchroniser_presence_vers_paie(employe, mois, annee)
            
            if created:
                messages.success(
                    request,
                    f"✅ Paie créée pour {employe.prenom} {employe.nom} - {mois:02d}/{annee}"
                )
            else:
                messages.success(
                    request,
                    f"🔄 Paie mise à jour pour {employe.prenom} {employe.nom} - {mois:02d}/{annee}"
                )
            
            # Afficher les statistiques
            messages.info(
                request,
                f"📊 Présence: {stats['jours_presence']} j. | "
                f"Sundays: {stats['sundays']} | "
                f"Absences: {stats['absent']} | "
                f"Repos: {stats['j_repos']}"
            )
            
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la synchronisation: {str(e)}")
    
    return redirect('fleet_app:paie_employe_list_enhanced')


@login_required
def creer_paies_manquantes(request):
    """
    Créer automatiquement les paies manquantes pour tous les employés
    """
    if request.method == 'POST':
        try:
            mois = int(request.POST.get('mois', datetime.now().month))
            annee = int(request.POST.get('annee', datetime.now().year))
            
            # Récupérer les employés sans paie pour cette période
            employes_avec_paie = PaieEmploye.objects.filter(
                employe__user=request.user,
                mois=mois,
                annee=annee
            ).values_list('employe_id', flat=True)
            
            employes_sans_paie = Employe.objects.filter(
                user=request.user,
                statut='Actif'
            ).exclude(id__in=employes_avec_paie)
            
            paies_creees = 0
            for employe in employes_sans_paie:
                try:
                    paie_employe, created, stats = synchroniser_presence_vers_paie(employe, mois, annee)
                    if created:
                        paies_creees += 1
                except Exception as e:
                    messages.warning(
                        request,
                        f"⚠️ Erreur pour {employe.prenom} {employe.nom}: {str(e)}"
                    )
            
            if paies_creees > 0:
                messages.success(
                    request,
                    f"✅ {paies_creees} paie(s) créée(s) pour {mois:02d}/{annee}"
                )
            else:
                messages.info(request, "ℹ️ Aucune paie manquante détectée")
                
        except Exception as e:
            messages.error(request, f"❌ Erreur lors de la création des paies: {str(e)}")
    
    return redirect('fleet_app:paie_employe_list_enhanced')


@login_required
def export_paies_csv(request):
    """
    Exporter les paies au format CSV avec les calculs de présence
    """
    import csv
    from django.http import HttpResponse
    
    mois = int(request.GET.get('mois', datetime.now().month))
    annee = int(request.GET.get('annee', datetime.now().year))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="paies_{mois:02d}_{annee}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Matricule', 'Nom', 'Prénom', 'Profession',
        'Jours Présence', 'Sundays', 'Absences', 'Maladies', 'M.Payer', 'J.Repos',
        'Salaire Base', 'Salaire Brut', 'CNSS', 'RTS', 'VF', 'Salaire Net'
    ])
    
    paies = PaieEmploye.objects.filter(
        employe__user=request.user,
        mois=mois,
        annee=annee
    ).select_related('employe')
    
    for paie in paies:
        stats = calculer_statistiques_presence(paie.employe, mois, annee)
        
        writer.writerow([
            paie.employe.matricule,
            paie.employe.nom,
            paie.employe.prenom,
            paie.employe.profession,
            stats['jours_presence'],
            stats['sundays'],
            stats['absent'],
            stats['maladies'],
            stats['m_payer'],
            stats['j_repos'],
            paie.salaire_base,
            paie.salaire_brut,
            paie.cnss,
            paie.rts,
            paie.vf,
            paie.salaire_net
        ])
    
    return response
