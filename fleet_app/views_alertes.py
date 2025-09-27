from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.template.loader import render_to_string
from django.views.decorators.http import require_http_methods
from .models_alertes import Alerte
from .models import Vehicule, DistanceParcourue, ConsommationCarburant, DisponibiliteVehicule, UtilisationVehicule, IncidentSecurite, CoutFonctionnement, CoutFinancier

@login_required
def alerte_list(request):
    """
    Vue pour afficher la liste des alertes actives et résolues avec recherche
    """
    user = request.user
    
    # Filtres de recherche
    search_text = request.GET.get('search_text', '').strip()
    search_niveau = request.GET.get('search_niveau', '').strip()
    search_statut = request.GET.get('search_statut', '').strip()
    search_vehicule = request.GET.get('search_vehicule', '').strip()
    date_creation_min = request.GET.get('date_creation_min', '').strip()
    date_creation_max = request.GET.get('date_creation_max', '').strip()
    
    # Requête de base avec filtrage par utilisateur
    qs_actives = Alerte.objects.filter(user=user, statut='Active').select_related('vehicule')
    qs_resolues = Alerte.objects.filter(user=user, statut__in=['Résolue', 'Ignorée']).select_related('vehicule')
    
    # Application des filtres pour les alertes actives
    if search_text:
        qs_actives = qs_actives.filter(
            Q(titre__icontains=search_text) |
            Q(description__icontains=search_text) |
            Q(type_alerte__icontains=search_text)
        )
    
    if search_niveau:
        qs_actives = qs_actives.filter(niveau_urgence=search_niveau)
    
    if search_vehicule:
        qs_actives = qs_actives.filter(
            Q(vehicule__immatriculation__icontains=search_vehicule) |
            Q(vehicule__marque__icontains=search_vehicule) |
            Q(vehicule__modele__icontains=search_vehicule)
        )
    
    if date_creation_min:
        qs_actives = qs_actives.filter(date_creation__gte=date_creation_min)
    
    if date_creation_max:
        qs_actives = qs_actives.filter(date_creation__lte=date_creation_max)
    
    # Application des mêmes filtres pour les alertes résolues
    if search_text:
        qs_resolues = qs_resolues.filter(
            Q(titre__icontains=search_text) |
            Q(description__icontains=search_text) |
            Q(type_alerte__icontains=search_text)
        )
    
    if search_niveau:
        qs_resolues = qs_resolues.filter(niveau_urgence=search_niveau)
    
    if search_vehicule:
        qs_resolues = qs_resolues.filter(
            Q(vehicule__immatriculation__icontains=search_vehicule) |
            Q(vehicule__marque__icontains=search_vehicule) |
            Q(vehicule__modele__icontains=search_vehicule)
        )
    
    if date_creation_min:
        qs_resolues = qs_resolues.filter(date_creation__gte=date_creation_min)
    
    if date_creation_max:
        qs_resolues = qs_resolues.filter(date_creation__lte=date_creation_max)
    
    # Tri
    alertes_actives = qs_actives.order_by('-date_creation')
    alertes_resolues = qs_resolues.order_by('-date_creation')
    
    # Pagination
    paginator_actives = Paginator(alertes_actives, 10)
    page_number_actives = request.GET.get('page_actives', 1)
    alertes_actives_page = paginator_actives.get_page(page_number_actives)
    
    paginator_resolues = Paginator(alertes_resolues, 10)
    page_number_resolues = request.GET.get('page_resolues', 1)
    alertes_resolues_page = paginator_resolues.get_page(page_number_resolues)
    
    # Données pour les filtres
    vehicules = Vehicule.objects.filter(user=user).values_list('immatriculation', flat=True).distinct()
    niveaux_urgence = Alerte.NIVEAU_CHOICES if hasattr(Alerte, 'NIVEAU_CHOICES') else [
        ('Critique', 'Critique'),
        ('Élevé', 'Élevé'),
        ('Moyen', 'Moyen'),
        ('Faible', 'Faible')
    ]
    
    context = {
        'alertes': alertes_actives_page,  # Pour compatibilité avec le template existant
        'alertes_historique': alertes_resolues_page,  # Pour compatibilité avec le template existant
        'alertes_actives': alertes_actives_page,
        'alertes_resolues': alertes_resolues_page,
        'active_count': alertes_actives.count(),
        'resolved_count': alertes_resolues.count(),
        'vehicules': vehicules,
        'niveaux_urgence': niveaux_urgence,
        'search_text': search_text,
        'search_niveau': search_niveau,
        'search_statut': search_statut,
        'search_vehicule': search_vehicule,
        'date_creation_min': date_creation_min,
        'date_creation_max': date_creation_max,
    }
    
    return render(request, 'fleet_app/alerte_list.html', context)

@login_required
def alerte_nouvelle(request):
    """
    Vue pour créer une nouvelle alerte manuellement
    """
    if request.method == 'POST':
        titre = request.POST.get('titre')
        description = request.POST.get('description')
        niveau = request.POST.get('niveau', 'Moyen')
        vehicule_id = request.POST.get('vehicule')
        
        if not titre or not description:
            messages.error(request, "Le titre et la description sont obligatoires.")
            return redirect('fleet_app:alerte_nouvelle')
        
        vehicule = None
        if vehicule_id:
            vehicule = get_object_or_404(Vehicule, id_vehicule=vehicule_id)
        
        alerte = Alerte(
            titre=titre,
            description=description,
            niveau=niveau,
            vehicule=vehicule,
            date_creation=timezone.now(),
            statut='Active'
        )
        alerte.save()
        
        messages.success(request, "L'alerte a été créée avec succès.")
        return redirect('fleet_app:alerte_list')
    
    vehicules = Vehicule.objects.filter(statut='EN_SERVICE')
    context = {
        'vehicules': vehicules,
        'niveaux': Alerte.NIVEAU_CHOICES,
    }
    
    return render(request, 'fleet_app/alerte_nouvelle.html', context)

@login_required
def alerte_resoudre(request, pk):
    """
    Vue pour marquer une alerte comme résolue
    """
    alerte = get_object_or_404(Alerte, pk=pk)
    
    if request.method == 'POST':
        resolution = request.POST.get('resolution')
        
        if not resolution:
            messages.error(request, "Veuillez fournir une description de la résolution.")
            return redirect('fleet_app:alerte_resoudre', pk=pk)
        
        alerte.statut = 'Résolue'
        alerte.resolution = resolution
        alerte.date_resolution = timezone.now()
        alerte.save()
        
        messages.success(request, "L'alerte a été marquée comme résolue.")
        return redirect('fleet_app:alerte_list')
    
    context = {
        'alerte': alerte,
    }
    
    return render(request, 'fleet_app/alerte_resoudre.html', context)

@login_required
def alerte_ignorer(request, pk):
    """
    Vue pour ignorer une alerte (la marquer comme résolue sans action)
    """
    alerte = get_object_or_404(Alerte, pk=pk)
    alerte.statut = 'Résolue'
    alerte.resolution = "Alerte ignorée par l'utilisateur."
    alerte.date_resolution = timezone.now()
    alerte.save()
    
    messages.success(request, "L'alerte a été ignorée.")
    return redirect('fleet_app:alerte_list')

@login_required
def alerte_supprimer(request, pk):
    """
    Vue pour supprimer une alerte
    """
    alerte = get_object_or_404(Alerte, pk=pk)
    alerte.delete()
    
    messages.success(request, "L'alerte a été supprimée.")
    return redirect('fleet_app:alerte_list')

@login_required
def get_alertes_kpi(request):
    """
    Vue API pour récupérer les données des alertes pour le tableau de bord
    """
    # Compter les alertes par niveau
    alertes_par_niveau = Alerte.objects.filter(statut='Active').values('niveau').annotate(count=Count('id'))
    
    # Compter les alertes par type de KPI
    alertes_par_type = []
    
    # Convertir en format adapté pour le frontend
    niveaux_data = {item['niveau']: item['count'] for item in alertes_par_niveau}
    
    # Récupérer les 5 alertes les plus récentes
    alertes_recentes = Alerte.objects.filter(statut='Active').order_by('-date_creation')[:5]
    alertes_recentes_data = []
    
    for alerte in alertes_recentes:
        vehicule_info = alerte.vehicule.immatriculation if alerte.vehicule else "N/A"
        alertes_recentes_data.append({
            'id': alerte.id,
            'titre': alerte.titre,
            'niveau': alerte.niveau,
            'date': alerte.date_creation.strftime('%d/%m/%Y %H:%M'),
            'vehicule': vehicule_info
        })
    
    data = {
        'alertes_par_niveau': niveaux_data,
        'alertes_par_type': alertes_par_type,
        'alertes_recentes': alertes_recentes_data,
        'total_actives': Alerte.objects.filter(statut='Active').count()
    }
    
    return JsonResponse(data)


@login_required
def alerte_search_ajax(request):
    """Vue AJAX pour la recherche dynamique des alertes"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)
    
    user = request.user
    
    # Récupération des paramètres de recherche
    search_text = request.GET.get('search_text', '').strip()
    search_niveau = request.GET.get('search_niveau', '').strip()
    search_statut = request.GET.get('search_statut', '').strip()
    search_vehicule = request.GET.get('search_vehicule', '').strip()
    date_creation_min = request.GET.get('date_creation_min', '').strip()
    date_creation_max = request.GET.get('date_creation_max', '').strip()
    section = request.GET.get('section', 'actives')  # 'actives' ou 'resolues'
    
    # Requête de base selon la section
    if section == 'actives':
        qs = Alerte.objects.filter(user=user, statut='Active').select_related('vehicule')
    else:
        qs = Alerte.objects.filter(user=user, statut__in=['Résolue', 'Ignorée']).select_related('vehicule')
    
    # Application des filtres
    if search_text:
        qs = qs.filter(
            Q(titre__icontains=search_text) |
            Q(description__icontains=search_text) |
            Q(type_alerte__icontains=search_text)
        )
    
    if search_niveau:
        qs = qs.filter(niveau_urgence=search_niveau)
    
    if search_vehicule:
        qs = qs.filter(
            Q(vehicule__immatriculation__icontains=search_vehicule) |
            Q(vehicule__marque__icontains=search_vehicule) |
            Q(vehicule__modele__icontains=search_vehicule)
        )
    
    if date_creation_min:
        try:
            qs = qs.filter(date_creation__gte=date_creation_min)
        except:
            pass
    
    if date_creation_max:
        try:
            qs = qs.filter(date_creation__lte=date_creation_max)
        except:
            pass
    
    # Tri
    qs = qs.order_by('-date_creation')
    
    # Pagination
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page', 1)
    alertes = paginator.get_page(page_number)
    
    # Rendu du template partiel selon la section
    if section == 'actives':
        template_name = 'fleet_app/alertes/alertes_actives_rows.html'
    else:
        template_name = 'fleet_app/alertes/alertes_resolues_rows.html'
    
    html = render_to_string(template_name, {
        'alertes': alertes
    }, request=request)
    
    return JsonResponse({
        'html': html,
        'has_next': alertes.has_next(),
        'has_previous': alertes.has_previous(),
        'page_number': alertes.number,
        'num_pages': alertes.paginator.num_pages,
        'count': alertes.paginator.count
    })
