from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
from .models_entreprise import Employe, PresenceJournaliere
import calendar
from datetime import date, datetime
import json
from .forms import PointageJournalierForm, PointageRapideForm
from decimal import Decimal


@login_required
def pointage_journalier(request):
    """Vue pour afficher le tableau de pointage journalier du mois"""
    today = timezone.now().date()
    mois = int(request.GET.get('mois', today.month))
    annee = int(request.GET.get('annee', today.year))
    
    # Générer tous les jours du mois
    _, nb_jours = calendar.monthrange(annee, mois)
    jours_mois = []
    
    for jour in range(1, nb_jours + 1):
        date_obj = date(annee, mois, jour)
        # Déterminer si on peut pointer pour ce jour (pas dans le futur)
        peut_pointer = date_obj <= today
        jours_mois.append({
            'jour': jour,
            'date': date_obj,
            'jour_semaine': date_obj.strftime('%a'),
            'peut_pointer': peut_pointer
        })
    
    # Récupérer tous les employés actifs de l'utilisateur
    employes = Employe.objects.filter(user=request.user, statut='Actif').order_by('nom', 'prenom')
    
    # Récupérer toutes les présences du mois
    presences = PresenceJournaliere.objects.filter(
        employe__user=request.user,
        date__year=annee,
        date__month=mois
    ).select_related('employe')
    
    # Organiser les présences par employé et date
    presences_dict = {}
    for presence in presences:
        employe_id = presence.employe.id
        jour = presence.date.day
        if employe_id not in presences_dict:
            presences_dict[employe_id] = {}
        presences_dict[employe_id][jour] = presence
    
    # Préparer les données pour le template
    employes_data = []
    for employe in employes:
        employe_presences = []
        for jour_info in jours_mois:
            jour = jour_info['jour']
            presence = presences_dict.get(employe.id, {}).get(jour)
            employe_presences.append({
                'jour': jour,
                'date': jour_info['date'],
                'presence': presence,
                'peut_pointer': jour_info['peut_pointer']
            })
        
        # Calculer les compteurs de statuts pour cet employé
        count_P_Am = 0
        count_P_Pm = 0
        count_P_Am_Pm = 0
        count_P_dim_Am = 0
        count_P_dim_Pm = 0
        count_P_dim_Am_Pm = 0
        count_A = 0
        count_M = 0
        count_M_Payer = 0
        count_OFF = 0
        count_total = 0
        
        # Compter les statuts pour cet employé
        for presence_info in employe_presences:
            if presence_info['presence']:
                statut = presence_info['presence'].statut
                count_total += 1
                if statut == 'P(Am)':
                    count_P_Am += 1
                elif statut == 'P(Pm)':
                    count_P_Pm += 1
                elif statut == 'P(Am_&_Pm)':
                    count_P_Am_Pm += 1
                elif statut == 'P(dim_Am)':
                    count_P_dim_Am += 1
                elif statut == 'P(dim_Pm)':
                    count_P_dim_Pm += 1
                elif statut == 'P(dim_Am_&_Pm)':
                    count_P_dim_Am_Pm += 1
                elif statut == 'A':
                    count_A += 1
                elif statut == 'M':
                    count_M += 1
                elif statut == 'M(Payer)':
                    count_M_Payer += 1
                elif statut == 'OFF':
                    count_OFF += 1
        
        employes_data.append({
            'employe': employe,
            'presences': employe_presences,
            'count_P_Am': count_P_Am,
            'count_P_Pm': count_P_Pm,
            'count_P_Am_Pm': count_P_Am_Pm,
            'count_P_dim_Am': count_P_dim_Am,
            'count_P_dim_Pm': count_P_dim_Pm,
            'count_P_dim_Am_Pm': count_P_dim_Am_Pm,
            'count_A': count_A,
            'count_M': count_M,
            'count_M_Payer': count_M_Payer,
            'count_OFF': count_OFF,
            'count_total': count_total
        })
    
    # Navigation mois précédent/suivant
    if mois == 1:
        mois_precedent = {'mois': 12, 'annee': annee - 1}
    else:
        mois_precedent = {'mois': mois - 1, 'annee': annee}
    
    if mois == 12:
        mois_suivant = {'mois': 1, 'annee': annee + 1}
    else:
        mois_suivant = {'mois': mois + 1, 'annee': annee}
    
    context = {
        'employes_data': employes_data,
        'jours_mois': jours_mois,
        'mois': mois,
        'annee': annee,
        'mois_nom': calendar.month_name[mois],
        'mois_precedent': mois_precedent,
        'mois_suivant': mois_suivant,
        'today': today,
        'statut_choices': PresenceJournaliere.STATUT_CHOICES,
    }
    
    return render(request, 'fleet_app/pointage/pointage_journalier.html', context)


@login_required
def pointage_ajax(request):
    """Vue AJAX pour pointer un employé à une date donnée"""
    if request.method == 'POST':
        employe_id = request.POST.get('employe_id')
        date_str = request.POST.get('date')
        statut = request.POST.get('statut')
        
        try:
            # Vérifier que l'employé appartient à l'utilisateur
            employe = get_object_or_404(Employe, id=employe_id, user=request.user)
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # Vérifier qu'on ne pointe pas dans le futur
            if date_obj > timezone.now().date():
                return JsonResponse({
                    'success': False,
                    'message': 'Impossible de pointer dans le futur'
                })
            
            # Créer ou mettre à jour le pointage
            pointage, created = PresenceJournaliere.objects.update_or_create(
                employe=employe,
                date=date_obj,
                defaults={'statut': statut}
            )
            
            action = 'créé' if created else 'mis à jour'

            # Calculer les compteurs mis à jour pour l'employé sur le mois de la date pointée
            mois = date_obj.month
            annee = date_obj.year
            presences_mois = PresenceJournaliere.objects.filter(
                employe=employe,
                date__year=annee,
                date__month=mois
            )

            count_P_Am = 0
            count_P_Pm = 0
            count_P_Am_Pm = 0
            count_P_dim_Am = 0
            count_P_dim_Pm = 0
            count_P_dim_Am_Pm = 0
            count_A = 0
            count_M = 0
            count_M_Payer = 0
            count_OFF = 0
            count_total = 0

            for p in presences_mois:
                statut_val = p.statut
                count_total += 1
                if statut_val == 'P(Am)':
                    count_P_Am += 1
                elif statut_val == 'P(Pm)':
                    count_P_Pm += 1
                elif statut_val == 'P(Am_&_Pm)':
                    count_P_Am_Pm += 1
                elif statut_val == 'P(dim_Am)':
                    count_P_dim_Am += 1
                elif statut_val == 'P(dim_Pm)':
                    count_P_dim_Pm += 1
                elif statut_val == 'P(dim_Am_&_Pm)':
                    count_P_dim_Am_Pm += 1
                elif statut_val == 'A':
                    count_A += 1
                elif statut_val == 'M':
                    count_M += 1
                elif statut_val == 'M(Payer)':
                    count_M_Payer += 1
                elif statut_val == 'OFF':
                    count_OFF += 1

            return JsonResponse({
                'success': True,
                'message': f'Pointage {action} pour {employe.nom} {employe.prenom}',
                'statut': statut,
                'statut_display': dict(PresenceJournaliere.STATUT_CHOICES)[statut],
                'counts': {
                    'P_Am': count_P_Am,
                    'P_Pm': count_P_Pm,
                    'P_Am_Pm': count_P_Am_Pm,
                    'P_dim_Am': count_P_dim_Am,
                    'P_dim_Pm': count_P_dim_Pm,
                    'P_dim_Am_Pm': count_P_dim_Am_Pm,
                    'A': count_A,
                    'M': count_M,
                    'M_Payer': count_M_Payer,
                    'OFF': count_OFF,
                    'total': count_total,
                }
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'message': f'Erreur: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'message': 'Méthode non autorisée'})


@login_required
def pointage_formulaire(request):
    """Vue pour le formulaire de pointage individuel"""
    if request.method == 'POST':
        form = PointageJournalierForm(request.POST, user=request.user)
        if form.is_valid():
            pointage = form.save(commit=False)
            
            # Vérifier que l'employé appartient à l'utilisateur
            if pointage.employe.user != request.user:
                messages.error(request, 'Vous ne pouvez pas pointer pour cet employé.')
                return render(request, 'fleet_app/pointage/formulaire.html', {'form': form})
            
            # Vérifier si un pointage existe déjà
            existing = PresenceJournaliere.objects.filter(
                employe=pointage.employe,
                date=pointage.date
            ).first()
            
            if existing:
                existing.statut = pointage.statut
                existing.save()
                messages.success(
                    request,
                    f'Pointage mis à jour pour {pointage.employe.nom} {pointage.employe.prenom} '
                    f'le {pointage.date.strftime("%d/%m/%Y")}'
                )
            else:
                pointage.save()
                messages.success(
                    request,
                    f'Pointage enregistré pour {pointage.employe.nom} {pointage.employe.prenom} '
                    f'le {pointage.date.strftime("%d/%m/%Y")}'
                )
            
            return redirect('fleet_app:pointage_formulaire')
    else:
        form = PointageJournalierForm(user=request.user)
    
    # Récupérer les derniers pointages pour affichage
    derniers_pointages = PresenceJournaliere.objects.filter(
        employe__user=request.user
    ).select_related('employe').order_by('-date', '-id')[:10]
    
    context = {
        'form': form,
        'derniers_pointages': derniers_pointages
    }
    
    return render(request, 'fleet_app/pointage/formulaire.html', context)


@login_required
def pointage_rapide(request):
    """Vue pour le formulaire de pointage rapide (plusieurs employés)"""
    if request.method == 'POST':
        form = PointageRapideForm(request.POST, user=request.user)
        if form.is_valid():
            pointages_crees, pointages_mis_a_jour = form.save(request.user)
            
            total = pointages_crees + pointages_mis_a_jour
            if total > 0:
                messages.success(
                    request,
                    f'Pointage terminé : {pointages_crees} créés, {pointages_mis_a_jour} mis à jour'
                )
            else:
                messages.info(request, 'Aucun pointage n\'a été effectué.')
            
            return redirect('fleet_app:pointage_rapide')
    else:
        form = PointageRapideForm(user=request.user)
    
    # Récupérer les employés actifs pour affichage
    employes = Employe.objects.filter(user=request.user, statut='Actif').order_by('nom', 'prenom')
    
    context = {
        'form': form,
        'employes': employes
    }
    
    return render(request, 'fleet_app/pointage/rapide.html', context)


@login_required
def historique_pointage(request):
    """Vue pour consulter l'historique des pointages"""
    # Filtres
    employe_id = request.GET.get('employe')
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    statut = request.GET.get('statut')
    
    # Query de base
    pointages = PresenceJournaliere.objects.filter(
        employe__user=request.user
    ).select_related('employe')
    
    # Appliquer les filtres
    if employe_id:
        pointages = pointages.filter(employe_id=employe_id)
    
    if date_debut:
        pointages = pointages.filter(date__gte=date_debut)
    
    if date_fin:
        pointages = pointages.filter(date__lte=date_fin)
    
    if statut:
        pointages = pointages.filter(statut=statut)
    
    # Ordonner par date décroissante
    pointages = pointages.order_by('-date', 'employe__nom', 'employe__prenom')
    
    # Pagination (optionnelle)
    from django.core.paginator import Paginator
    paginator = Paginator(pointages, 50)  # 50 pointages par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Données pour les filtres
    employes = Employe.objects.filter(user=request.user, statut='Actif').order_by('nom', 'prenom')
    
    context = {
        'page_obj': page_obj,
        'employes': employes,
        'statut_choices': PresenceJournaliere.STATUT_CHOICES,
        'filters': {
            'employe': employe_id,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'statut': statut,
        }
    }
    
    return render(request, 'fleet_app/pointage/historique.html', context)


@login_required
def configuration_salaire(request):
    """
    Vue pour configurer les montants de salaire par statut de présence de manière dynamique
    """
    try:
        from .forms import ConfigurationSalaireForm
        from .models_entreprise import Employe, ConfigurationSalaire, PresenceJournaliere
        
        # Récupérer l'employé sélectionné depuis GET (navigation) ou POST (soumission)
        employe_id = request.GET.get('employe') or (request.POST.get('employe') if request.method == 'POST' else None)
        
        if request.method == 'POST':
            form = ConfigurationSalaireForm(request.POST, user=request.user, employe_id=employe_id)
            if form.is_valid():
                try:
                    configurations_mises_a_jour = form.save(request.user)
                    messages.success(
                        request, 
                        f'✅ {configurations_mises_a_jour} configurations de salaire mises à jour avec succès.'
                    )
                    return redirect('fleet_app:configuration_salaire')
                except Exception as e:
                    messages.error(request, f'❌ Erreur lors de la sauvegarde: {str(e)}')
        else:
            form = ConfigurationSalaireForm(user=request.user, employe_id=employe_id)
        
        # Récupérer tous les employés avec leurs configurations
        employes = Employe.objects.filter(user=request.user, statut='Actif').order_by('nom', 'prenom')
        configurations_resume = []
        
        for employe in employes:
            configs = ConfigurationSalaire.objects.filter(employe=employe, actif=True)
            total_configs = configs.count()
            total_montant = sum((config.montant_journalier for config in configs), Decimal('0'))
        
            configurations_resume.append({
                'employe': employe,
                'nb_configurations': total_configs,
                'montant_total': total_montant,
                'configurations': {config.statut_presence: config.montant_journalier for config in configs}
            })
        
        context = {
            'form': form,
            'configurations_resume': configurations_resume,
            'statut_choices': PresenceJournaliere.STATUT_CHOICES,
            'employe_selectionne_id': (int(employe_id) if (isinstance(employe_id, (int, str)) and str(employe_id).isdigit()) else None),
        }
        
        return render(request, 'fleet_app/pointage/configuration_salaire.html', context)
    
    except Exception as e:
        from django.http import HttpResponse
        import traceback
        # Retourner l'erreur complète pour debug
        error_details = f"Erreur 500 dans configuration_salaire:\n{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
        return HttpResponse(f"<pre>{error_details}</pre>", status=500)
