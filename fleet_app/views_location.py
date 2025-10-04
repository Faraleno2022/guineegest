from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.template.loader import render_to_string, get_template
from django.contrib import messages
import calendar
from .models import FournisseurVehicule, Vehicule
from .models_location import (
    LocationVehicule,
    FeuillePontageLocation,
    FactureLocation,
)
from .forms_location import (
    FournisseurVehiculeForm,
    LocationVehiculeForm,
    FeuillePontageLocationForm,
    FactureLocationForm,
)
from .utils.decorators import queryset_filter_by_tenant, object_belongs_to_tenant


@login_required
def locations_dashboard(request):
    user = request.user
    locations = queryset_filter_by_tenant(LocationVehicule.objects.all(), request).select_related("vehicule", "fournisseur")
    actifs = locations.filter(statut="Active").count()
    inactifs = locations.filter(statut__in=["Inactive", "Clôturée"]).count()

    feuilles = queryset_filter_by_tenant(FeuillePontageLocation.objects.all(), request)
    jours_travail = feuilles.filter(statut="Travail").count()
    jours_entretien = feuilles.filter(statut="Entretien").count()
    jours_hs = feuilles.filter(statut="Hors service").count()

    # Totaux factures existants
    recettes = queryset_filter_by_tenant(FactureLocation.objects.all(), request).aggregate(total=Sum("montant_ttc"))['total'] or 0

    # Calculs par périodes basés sur les feuilles de type "Travail" et le tarif journalier de la location
    today = timezone.now().date()
    start_month = today.replace(day=1)
    start_year = today.replace(month=1, day=1)

    # Revenus journaliers = somme des tarifs journaliers pour chaque feuille "Travail" du jour
    feuilles_jour = feuilles.filter(statut="Travail", date=today).select_related("location")
    revenu_jour = sum((f.location.tarif_journalier or 0) for f in feuilles_jour)

    # Revenus mensuels
    feuilles_mois = feuilles.filter(statut="Travail", date__gte=start_month, date__lte=today).select_related("location")
    revenu_mois = sum((f.location.tarif_journalier or 0) for f in feuilles_mois)

    # Revenus annuels
    feuilles_annee = feuilles.filter(statut="Travail", date__gte=start_year, date__lte=today).select_related("location")
    revenu_annee = sum((f.location.tarif_journalier or 0) for f in feuilles_annee)

    # Entretien: nombre de jours en entretien (mois courant) et montant "perdu" (tarif * jours entretien)
    feuilles_entretien_mois = feuilles.filter(statut="Entretien", date__gte=start_month, date__lte=today).select_related("location")
    entretien_jours_mois = feuilles_entretien_mois.count()
    entretien_perte_mois = sum((f.location.tarif_journalier or 0) for f in feuilles_entretien_mois)

    context = {
        "locations": locations[:10],
        "actifs": actifs,
        "inactifs": inactifs,
        "jours_travail": jours_travail,
        "jours_entretien": jours_entretien,
        "jours_hs": jours_hs,
        "recettes": recettes,
        # Nouveaux indicateurs
        "revenu_jour": revenu_jour,
        "revenu_mois": revenu_mois,
        "revenu_annee": revenu_annee,
        "entretien_jours_mois": entretien_jours_mois,
        "entretien_perte_mois": entretien_perte_mois,
    }
    return render(request, "fleet_app/locations/dashboard.html", context)


@login_required
def locations_dashboard_metrics_ajax(request):
    """AJAX endpoint retournant les métriques du dashboard filtrées par véhicule (optionnel)."""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)

    user = request.user
    vehicule_id = request.GET.get('vehicule_id', '').strip()

    feuilles = queryset_filter_by_tenant(FeuillePontageLocation.objects.all(), request)
    locations = queryset_filter_by_tenant(LocationVehicule.objects.all(), request)
    if vehicule_id:
        try:
            # vehicule_id correspond au PK string de Vehicule
            feuilles = feuilles.filter(location__vehicule__id_vehicule=vehicule_id)
            locations = locations.filter(vehicule__id_vehicule=vehicule_id)
        except Exception:
            pass

    actifs = locations.filter(statut="Active").count()
    inactifs = locations.filter(statut__in=["Inactive", "Clôturée"]).count()

    jours_travail = feuilles.filter(statut="Travail").count()
    jours_entretien = feuilles.filter(statut="Entretien").count()
    jours_hs = feuilles.filter(statut="Hors service").count()

    today = timezone.now().date()
    start_month = today.replace(day=1)
    start_year = today.replace(month=1, day=1)

    # Revenus
    f_jour = feuilles.filter(statut="Travail", date=today).select_related("location")
    revenu_jour = sum((f.location.tarif_journalier or 0) for f in f_jour)

    f_mois = feuilles.filter(statut="Travail", date__gte=start_month, date__lte=today).select_related("location")
    revenu_mois = sum((f.location.tarif_journalier or 0) for f in f_mois)

    f_annee = feuilles.filter(statut="Travail", date__gte=start_year, date__lte=today).select_related("location")
    revenu_annee = sum((f.location.tarif_journalier or 0) for f in f_annee)

    # Entretien pertes (mois)
    f_ent_mois = feuilles.filter(statut="Entretien", date__gte=start_month, date__lte=today).select_related("location")
    entretien_jours_mois = f_ent_mois.count()
    entretien_perte_mois = sum((f.location.tarif_journalier or 0) for f in f_ent_mois)

    return JsonResponse({
        'actifs': actifs,
        'inactifs': inactifs,
        'jours_travail': jours_travail,
        'jours_entretien': jours_entretien,
        'jours_hs': jours_hs,
        'revenu_jour': float(revenu_jour),
        'revenu_mois': float(revenu_mois),
        'revenu_annee': float(revenu_annee),
        'entretien_jours_mois': entretien_jours_mois,
        'entretien_perte_mois': float(entretien_perte_mois),
    })


@login_required
def feuille_pontage_search_ajax(request):
    """Recherche dynamique AJAX pour les feuilles de pontage (locations)."""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)

    user = request.user
    qs = queryset_filter_by_tenant(FeuillePontageLocation.objects.all(), request).select_related("location", "location__vehicule")

    search_vehicule = request.GET.get('search_vehicule', '').strip()
    search_statut = request.GET.get('search_statut', '').strip()
    search_type = request.GET.get('search_type', '').strip()
    date_min = request.GET.get('date_min', '').strip()
    date_max = request.GET.get('date_max', '').strip()
    search_comment = request.GET.get('search_comment', '').strip()

    if search_vehicule:
        qs = qs.filter(
            Q(location__vehicule__immatriculation__icontains=search_vehicule) |
            Q(location__vehicule__marque__icontains=search_vehicule) |
            Q(location__vehicule__modele__icontains=search_vehicule)
        )

    if search_statut:
        qs = qs.filter(statut=search_statut)

    if search_type:
        qs = qs.filter(location__type_location=search_type)

    if date_min:
        try:
            qs = qs.filter(date__gte=date_min)
        except Exception:
            pass

    if date_max:
        try:
            qs = qs.filter(date__lte=date_max)
        except Exception:
            pass

    if search_comment:
        qs = qs.filter(commentaire__icontains=search_comment)

    paginator = Paginator(qs.order_by('-date'), 20)
    page_number = request.GET.get('page', 1)
    feuilles = paginator.get_page(page_number)

    html = render_to_string('fleet_app/locations/feuille_pontage_rows.html', {
        'feuilles': feuilles
    }, request=request)

    return JsonResponse({
        'html': html,
        'has_next': feuilles.has_next(),
        'has_previous': feuilles.has_previous(),
        'page_number': feuilles.number,
        'num_pages': feuilles.paginator.num_pages,
        'count': feuilles.paginator.count,
    })


@login_required
def fournisseur_search_ajax(request):
    """Recherche dynamique AJAX pour les fournisseurs de véhicules."""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)

    user = request.user
    qs = queryset_filter_by_tenant(FournisseurVehicule.objects.all(), request)

    search_text = request.GET.get('search_text', '').strip()
    if search_text:
        qs = qs.filter(
            Q(nom__icontains=search_text) |
            Q(contact__icontains=search_text) |
            Q(telephone__icontains=search_text) |
            Q(email__icontains=search_text) |
            Q(adresse__icontains=search_text)
        )

    paginator = Paginator(qs.order_by('nom'), 20)
    page_number = request.GET.get('page', 1)
    fournisseurs = paginator.get_page(page_number)

    html = render_to_string('fleet_app/locations/fournisseur_rows.html', {
        'fournisseurs': fournisseurs
    }, request=request)

    return JsonResponse({
        'html': html,
        'has_next': fournisseurs.has_next(),
        'has_previous': fournisseurs.has_previous(),
        'page_number': fournisseurs.number,
        'num_pages': fournisseurs.paginator.num_pages,
        'count': fournisseurs.paginator.count,
    })


@login_required
def facture_search_ajax(request):
    """Recherche dynamique AJAX pour les factures de location."""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)

    user = request.user
    qs = queryset_filter_by_tenant(FactureLocation.objects.all(), request).select_related('location', 'location__vehicule')

    search_numero = request.GET.get('search_numero', '').strip()
    search_statut = request.GET.get('search_statut', '').strip()
    search_vehicule = request.GET.get('search_vehicule', '').strip()
    date_min = request.GET.get('date_min', '').strip()
    date_max = request.GET.get('date_max', '').strip()

    if search_numero:
        qs = qs.filter(numero__icontains=search_numero)

    if search_statut:
        qs = qs.filter(statut__iexact=search_statut)

    if search_vehicule:
        qs = qs.filter(
            Q(location__vehicule__immatriculation__icontains=search_vehicule) |
            Q(location__vehicule__marque__icontains=search_vehicule) |
            Q(location__vehicule__modele__icontains=search_vehicule)
        )

    if date_min:
        try:
            qs = qs.filter(date__gte=date_min)
        except Exception:
            pass

    if date_max:
        try:
            qs = qs.filter(date__lte=date_max)
        except Exception:
            pass

    paginator = Paginator(qs.order_by('-date'), 20)
    page_number = request.GET.get('page', 1)
    factures = paginator.get_page(page_number)

    html = render_to_string('fleet_app/locations/facture_rows.html', {
        'factures': factures
    }, request=request)

    total = qs.aggregate(total=Sum('montant_ttc'))['total'] or 0

    return JsonResponse({
        'html': html,
        'has_next': factures.has_next(),
        'has_previous': factures.has_previous(),
        'page_number': factures.number,
        'num_pages': factures.paginator.num_pages,
        'count': factures.paginator.count,
        'total': float(total),
    })


@login_required
def location_list(request):
    user = request.user
    qs = queryset_filter_by_tenant(LocationVehicule.objects.all(), request).select_related("vehicule", "fournisseur")

    # Filtres de recherche
    search_vehicule = request.GET.get('search_vehicule', '').strip()
    search_fournisseur = request.GET.get('search_fournisseur', '').strip()
    search_type = request.GET.get('search_type', '').strip()
    search_statut = request.GET.get('search_statut', '').strip()
    date_debut_min = request.GET.get('date_debut_min', '').strip()
    date_debut_max = request.GET.get('date_debut_max', '').strip()

    # Application des filtres
    if search_vehicule:
        qs = qs.filter(
            Q(vehicule__immatriculation__icontains=search_vehicule) |
            Q(vehicule__marque__icontains=search_vehicule) |
            Q(vehicule__modele__icontains=search_vehicule)
        )

    if search_fournisseur:
        qs = qs.filter(fournisseur__nom__icontains=search_fournisseur)

    if search_type:
        qs = qs.filter(type_location=search_type)

    if search_statut:
        qs = qs.filter(statut=search_statut)

    if date_debut_min:
        qs = qs.filter(date_debut__gte=date_debut_min)

    if date_debut_max:
        qs = qs.filter(date_debut__lte=date_debut_max)

    # Pagination (ensure stable ordering)
    qs = qs.order_by('-date_debut', '-id')
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page')
    locations = paginator.get_page(page_number)

    # Données pour les filtres (tenant-aware)
    fournisseurs = queryset_filter_by_tenant(FournisseurVehicule.objects.all(), request).values_list('nom', flat=True).distinct()
    types_location = LocationVehicule.TYPE_CHOICES
    statuts_location = LocationVehicule.STATUT_CHOICES

    context = {
        "locations": locations,
        "fournisseurs": list(fournisseurs),
        "types_location": types_location,
        "statuts_location": statuts_location,
        "search_vehicule": search_vehicule,
        "search_fournisseur": search_fournisseur,
        "search_type": search_type,
        "search_statut": search_statut,
        "date_debut_min": date_debut_min,
        "date_debut_max": date_debut_max,
    }

    return render(request, "fleet_app/locations/location_list.html", context)


@login_required
def feuille_pontage_list(request):
    user = request.user
    today = timezone.now().date()
    qs = queryset_filter_by_tenant(FeuillePontageLocation.objects.all(), request).select_related("location", "location__vehicule")
    return render(request, "fleet_app/locations/feuille_pontage_list.html", {"feuilles": qs, "today": today})


@login_required
def fournisseur_list(request):
    user = request.user
    qs = queryset_filter_by_tenant(FournisseurVehicule.objects.all(), request)
    return render(request, "fleet_app/locations/fournisseur_list.html", {"fournisseurs": qs})


@login_required
def facture_list(request):
    user = request.user
    qs = queryset_filter_by_tenant(FactureLocation.objects.all(), request).select_related("location", "location__vehicule")
    total = qs.aggregate(total=Sum("montant_ttc"))['total'] or 0
    return render(request, "fleet_app/locations/facture_list.html", {"factures": qs, "total": total})


@login_required
def facture_detail(request, pk):
    facture = get_object_or_404(queryset_filter_by_tenant(FactureLocation.objects.all(), request), pk=pk)
    return render(request, "fleet_app/locations/facture_detail.html", {
        "facture": facture
    })


# ============================================================================
# VUES CRUD POUR LOCATIONS DE VÉHICULES
# ============================================================================

@login_required
def location_create(request):
    if request.method == 'POST':
        form = LocationVehiculeForm(request.POST, user=request.user)
        if form.is_valid():
            location = form.save(commit=False)
            location.user = request.user
            # Set entreprise from user profile if available
            ent = getattr(getattr(request.user, 'profil', None), 'entreprise', None) or getattr(request.user, 'entreprise', None)
            if hasattr(location, 'entreprise'):
                location.entreprise = ent
            location.save()
            messages.success(request, 'Location créée avec succès.')
            return redirect('fleet_app:location_list')
    else:
        form = LocationVehiculeForm(user=request.user)
    
    return render(request, 'fleet_app/locations/location_form.html', {
        'form': form,
        'title': 'Nouvelle Location'
    })


@login_required
def location_update(request, pk):
    location = get_object_or_404(LocationVehicule, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = LocationVehiculeForm(request.POST, instance=location, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Location modifiée avec succès.')
            return redirect('fleet_app:location_list')
    else:
        form = LocationVehiculeForm(instance=location, user=request.user)
    
    return render(request, 'fleet_app/locations/location_form.html', {
        'form': form,
        'location': location,
        'title': 'Modifier Location'
    })


@login_required
def location_delete(request, pk):
    location = get_object_or_404(LocationVehicule, pk=pk, user=request.user)
    
    if request.method == 'POST':
        location.delete()
        messages.success(request, 'Location supprimée avec succès.')
        return redirect('fleet_app:location_list')
    
    return render(request, 'fleet_app/locations/location_confirm_delete.html', {
        'location': location
    })


@login_required
def location_detail(request, pk):
    location = get_object_or_404(LocationVehicule, pk=pk, user=request.user)
    
    # Récupérer les feuilles de pontage
    feuilles = location.feuilles.all().order_by('-date')[:10]
    
    # Récupérer les factures
    factures = location.factures.all().order_by('-date')
    
    # Statistiques
    stats = {
        'jours_travail': location.jours_actifs,
        'jours_entretien': location.jours_entretien,
        'jours_hs': location.jours_hors_service,
        'total_factures': factures.aggregate(total=Sum('montant_ttc'))['total'] or 0
    }
    
    return render(request, 'fleet_app/locations/location_detail.html', {
        'location': location,
        'feuilles': feuilles,
        'factures': factures,
        'stats': stats
    })


# ============================================================================
# VUES CRUD POUR FOURNISSEURS DE VÉHICULES
# ============================================================================

@login_required
def fournisseur_create(request):
    if request.method == 'POST':
        form = FournisseurVehiculeForm(request.POST, user=request.user)
        if form.is_valid():
            fournisseur = form.save(commit=False)
            fournisseur.user = request.user
            ent = getattr(getattr(request.user, 'profil', None), 'entreprise', None) or getattr(request.user, 'entreprise', None)
            if hasattr(fournisseur, 'entreprise'):
                fournisseur.entreprise = ent
            fournisseur.save()
            messages.success(request, 'Fournisseur créé avec succès.')
            return redirect('fleet_app:fournisseur_location_list')
    else:
        form = FournisseurVehiculeForm(user=request.user)
    
    return render(request, 'fleet_app/locations/fournisseur_form.html', {
        'form': form,
        'title': 'Nouveau Fournisseur'
    })


@login_required
def fournisseur_update(request, pk):
    fournisseur = get_object_or_404(FournisseurVehicule, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = FournisseurVehiculeForm(request.POST, instance=fournisseur, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Fournisseur modifié avec succès.')
            return redirect('fleet_app:fournisseur_location_list')
    else:
        form = FournisseurVehiculeForm(instance=fournisseur, user=request.user)
    
    return render(request, 'fleet_app/locations/fournisseur_form.html', {
        'form': form,
        'fournisseur': fournisseur,
        'title': 'Modifier Fournisseur'
    })


@login_required
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(FournisseurVehicule, pk=pk, user=request.user)
    
    if request.method == 'POST':
        fournisseur.delete()
        messages.success(request, 'Fournisseur supprimé avec succès.')
        return redirect('fleet_app:fournisseur_location_list')
    
    return render(request, 'fleet_app/locations/fournisseur_confirm_delete.html', {
        'fournisseur': fournisseur
    })


# ============================================================================
# VUES CRUD POUR FEUILLES DE PONTAGE
# ============================================================================

@login_required
def feuille_pontage_create(request):
    if request.method == 'POST':
        form = FeuillePontageLocationForm(request.POST, user=request.user)
        if form.is_valid():
            feuille = form.save(commit=False)
            feuille.user = request.user
            ent = getattr(getattr(request.user, 'profil', None), 'entreprise', None) or getattr(request.user, 'entreprise', None)
            if hasattr(feuille, 'entreprise'):
                feuille.entreprise = ent
            feuille.save()
            messages.success(request, 'Feuille de pontage créée avec succès.')
            return redirect('fleet_app:feuille_pontage_location_list')
    else:
        form = FeuillePontageLocationForm(user=request.user)
    
    return render(request, 'fleet_app/locations/feuille_pontage_form.html', {
        'form': form,
        'title': 'Nouvelle Feuille de Pontage'
    })


@login_required
def feuille_pontage_update(request, pk):
    feuille = get_object_or_404(FeuillePontageLocation, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = FeuillePontageLocationForm(request.POST, instance=feuille, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Feuille de pontage modifiée avec succès.')
            return redirect('fleet_app:feuille_pontage_location_list')
    else:
        form = FeuillePontageLocationForm(instance=feuille, user=request.user)
    
    return render(request, 'fleet_app/locations/feuille_pontage_form.html', {
        'form': form,
        'feuille': feuille,
        'title': 'Modifier Feuille de Pontage'
    })


@login_required
def feuille_pontage_delete(request, pk):
    feuille = get_object_or_404(FeuillePontageLocation, pk=pk, user=request.user)
    
    if request.method == 'POST':
        feuille.delete()
        messages.success(request, 'Feuille de pontage supprimée avec succès.')
        return redirect('fleet_app:feuille_pontage_location_list')
    
    return render(request, 'fleet_app/locations/feuille_pontage_confirm_delete.html', {
        'feuille': feuille
    })


# ============================================================================
# VUES CRUD POUR FACTURES DE LOCATION
# ============================================================================

@login_required
def facture_create(request):
    if request.method == 'POST':
        form = FactureLocationForm(request.POST, user=request.user)
        if form.is_valid():
            facture = form.save(commit=False)
            facture.user = request.user
            ent = getattr(getattr(request.user, 'profil', None), 'entreprise', None) or getattr(request.user, 'entreprise', None)
            if hasattr(facture, 'entreprise'):
                facture.entreprise = ent
            facture.save()
            messages.success(request, 'Facture créée avec succès.')
            return redirect('fleet_app:facture_location_list')
    else:
        form = FactureLocationForm(user=request.user)
    
    return render(request, 'fleet_app/locations/facture_form.html', {
        'form': form,
        'title': 'Nouvelle Facture'
    })


@login_required
def facture_update(request, pk):
    facture = get_object_or_404(FactureLocation, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = FactureLocationForm(request.POST, instance=facture, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Facture modifiée avec succès.')
            return redirect('fleet_app:facture_location_list')
    else:
        form = FactureLocationForm(instance=facture, user=request.user)
    
    return render(request, 'fleet_app/locations/facture_form.html', {
        'form': form,
        'facture': facture,
        'title': 'Modifier Facture'
    })


@login_required
def facture_delete(request, pk):
    facture = get_object_or_404(FactureLocation, pk=pk, user=request.user)
    
    if request.method == 'POST':
        facture.delete()
        messages.success(request, 'Facture supprimée avec succès.')
        return redirect('fleet_app:facture_location_list')
    
    return render(request, 'fleet_app/locations/facture_confirm_delete.html', {
        'facture': facture
    })


# ============================================================================
# VUES AJAX ET UTILITAIRES
# ============================================================================

@login_required
@require_http_methods(["POST"])
def generer_facture_automatique(request, location_pk):
    """Génère automatiquement une facture basée sur les feuilles de pontage"""
    location = get_object_or_404(LocationVehicule, pk=location_pk, user=request.user)
    
    # Compter les jours de travail non facturés
    jours_travail = location.feuilles.filter(statut="Travail").count()
    
    if jours_travail == 0:
        return JsonResponse({
            'success': False,
            'message': 'Aucun jour de travail à facturer.'
        })
    
    # Calculer le montant
    montant_ht = jours_travail * location.tarif_journalier
    tva = montant_ht * 0.18  # TVA 18%
    montant_ttc = montant_ht + tva
    
    # Générer le numéro de facture
    import datetime
    numero = f"FACT-{location.pk}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Récupérer l'entreprise de l'utilisateur
    ent = getattr(getattr(request.user, 'profil', None), 'entreprise', None) or getattr(request.user, 'entreprise', None)
    
    # Créer la facture
    facture = FactureLocation.objects.create(
        location=location,
        numero=numero,
        montant_ht=montant_ht,
        tva=tva,
        montant_ttc=montant_ttc,
        user=request.user,
        entreprise=ent,
        jours_travail_mois=jours_travail,
        jours_non_travail_mois=0
    )
    
    return JsonResponse({
        'success': True,
        'message': f'Facture {numero} générée avec succès.',
        'facture_id': facture.pk,
        'montant_ttc': float(montant_ttc)
    })


@login_required
@require_http_methods(["POST"])
def generer_factures_mensuelles(request):
    """Génère (ou met à jour) les factures mensuelles pour toutes les locations de l'utilisateur
    en se basant sur les feuilles de pontage du mois indiqué (ou du mois courant par défaut).

    Calcule pour chaque location:
    - jours_travail (statut="Travail")
    - jours_non_travail = jours_totaux_du_mois_dans_la_location - jours_travail
    - montant = jours_travail * tarif_journalier (+ TVA)

    Évite les doublons en utilisant un numéro de facture unique par location et mois: "LOC-{location.pk}-{YYYYMM}".
    Si une facture existe déjà pour ce mois, met à jour ses montants.
    """
    user = request.user
    try:
        year = int(request.POST.get('year', '')) if request.POST.get('year') else timezone.now().year
        month = int(request.POST.get('month', '')) if request.POST.get('month') else timezone.now().month
    except ValueError:
        return JsonResponse({'success': False, 'message': 'Paramètres year/month invalides.'}, status=400)

    # Début/fin du mois
    first_day = timezone.datetime(year, month, 1).date()
    last_day = timezone.datetime(year, month, calendar.monthrange(year, month)[1]).date()

    locations = queryset_filter_by_tenant(LocationVehicule.objects.all(), request).select_related('vehicule')
    results = []
    total_factures = 0

    for loc in locations:
        # Calculer l'intervalle de recouvrement entre la période de la location et le mois
        loc_start = loc.date_debut or first_day
        loc_end = loc.date_fin or last_day
        period_start = max(loc_start, first_day)
        period_end = min(loc_end, last_day)
        if period_start > period_end:
            continue  # pas de recouvrement ce mois

        # Nombre de jours calendaires couverts ce mois pour cette location
        jours_couverts = (period_end - period_start).days + 1

        # Feuilles de pontage "Travail" dans cet intervalle
        feuilles_travail = loc.feuilles.filter(statut="Travail", date__gte=period_start, date__lte=period_end)
        jours_travail = feuilles_travail.count()
        jours_non_travail = max(jours_couverts - jours_travail, 0)

        # Montants
        tarif = loc.tarif_journalier or 0
        montant_ht = jours_travail * tarif
        tva = montant_ht * 0.18
        montant_ttc = montant_ht + tva

        numero = f"LOC-{loc.pk}-{year}{month:02d}"
        
        # Récupérer l'entreprise de l'utilisateur
        ent = getattr(getattr(user, 'profil', None), 'entreprise', None) or getattr(user, 'entreprise', None)

        # Créer ou mettre à jour la facture du mois
        facture, created = FactureLocation.objects.update_or_create(
            user=user,
            location=loc,
            numero=numero,
            defaults={
                'date': period_end,
                'montant_ht': montant_ht,
                'tva': tva,
                'montant_ttc': montant_ttc,
                'jours_travail_mois': jours_travail,
                'jours_non_travail_mois': jours_non_travail,
                'statut': getattr(FactureLocation, 'STATUT_BROUILLON', 'Brouillon'),
                'entreprise': ent,
            }
        )

        total_factures += float(montant_ttc)
        results.append({
            'location_id': loc.pk,
            'vehicule': str(loc.vehicule),
            'jours_travail': jours_travail,
            'jours_non_travail': jours_non_travail,
            'montant_ttc': float(montant_ttc),
            'facture_id': facture.pk,
            'numero': numero,
            'created': created,
        })

    return JsonResponse({
        'success': True,
        'message': f'Factures générées/mises à jour pour {len(results)} location(s) sur {year}-{month:02d}.',
        'total_mois': total_factures,
        'details': results,
    })


@login_required
def location_search_ajax(request):
    """Vue AJAX pour la recherche dynamique des locations"""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)
    
    user = request.user
    qs = LocationVehicule.objects.filter(user=user).select_related("vehicule", "fournisseur")
    
    # Récupération des paramètres de recherche
    search_vehicule = request.GET.get('search_vehicule', '').strip()
    search_fournisseur = request.GET.get('search_fournisseur', '').strip()
    search_type = request.GET.get('search_type', '').strip()
    search_statut = request.GET.get('search_statut', '').strip()
    date_debut_min = request.GET.get('date_debut_min', '').strip()
    date_debut_max = request.GET.get('date_debut_max', '').strip()
    
    # Application des filtres
    if search_vehicule:
        qs = qs.filter(
            Q(vehicule__immatriculation__icontains=search_vehicule) |
            Q(vehicule__marque__icontains=search_vehicule) |
            Q(vehicule__modele__icontains=search_vehicule)
        )
    
    if search_fournisseur:
        qs = qs.filter(fournisseur__nom__icontains=search_fournisseur)
    
    if search_type:
        qs = qs.filter(type_location=search_type)
    
    if search_statut:
        qs = qs.filter(statut=search_statut)
    
    if date_debut_min:
        try:
            qs = qs.filter(date_debut__gte=date_debut_min)
        except:
            pass
    
    if date_debut_max:
        try:
            qs = qs.filter(date_debut__lte=date_debut_max)
        except:
            pass
    
    # Pagination (ensure stable ordering)
    qs = qs.order_by('-date_debut', '-id')
    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page', 1)
    locations = paginator.get_page(page_number)
    
    # Rendu du template partiel
    html = render_to_string('fleet_app/locations/location_table_rows.html', {
        'locations': locations
    }, request=request)
    
    return JsonResponse({
        'html': html,
        'has_next': locations.has_next(),
        'has_previous': locations.has_previous(),
        'page_number': locations.number,
        'num_pages': locations.paginator.num_pages,
        'count': locations.paginator.count
    })


@login_required
def search_vehicules_ajax(request):
    """Retourne une liste JSON de véhicules filtrés pour Select2."""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)

    term = request.GET.get('term', '').strip()
    qs = Vehicule.objects.filter(user=request.user)
    if term:
        qs = qs.filter(
            Q(immatriculation__icontains=term) |
            Q(marque__icontains=term) |
            Q(modele__icontains=term)
        )
    results = [
        {
            'id': v.pk,
            'text': f"{v.immatriculation} - {v.marque} {v.modele}".strip()
        }
        for v in qs.order_by('immatriculation')[:20]
    ]
    return JsonResponse({'results': results})


@login_required
def search_fournisseurs_ajax(request):
    """Retourne une liste JSON de fournisseurs filtrés pour Select2."""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)

    term = request.GET.get('term', '').strip()
    qs = FournisseurVehicule.objects.filter(user=request.user)
    if term:
        qs = qs.filter(nom__icontains=term)
    results = [
        {
            'id': f.pk,
            'text': f.nom
        }
        for f in qs.order_by('nom')[:20]
    ]
    return JsonResponse({'results': results})


@login_required
@require_http_methods(["POST"])
def fournisseur_quick_create_ajax(request):
    """Crée rapidement un fournisseur via AJAX et renvoie son id et nom."""
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)

    nom = request.POST.get('nom', '').strip()
    contact = request.POST.get('contact', '').strip()
    telephone = request.POST.get('telephone', '').strip()
    email = request.POST.get('email', '').strip()
    adresse = request.POST.get('adresse', '').strip()

    if not nom:
        return JsonResponse({'success': False, 'message': "Le nom du fournisseur est requis."}, status=400)

    ent = getattr(getattr(request.user, 'profil', None), 'entreprise', None) or getattr(request.user, 'entreprise', None)
    fournisseur = FournisseurVehicule.objects.create(
        nom=nom,
        contact=contact or None,
        telephone=telephone or None,
        email=email or None,
        adresse=adresse or None,
        user=request.user,
        entreprise=ent,
    )

    return JsonResponse({
        'success': True,
        'id': fournisseur.pk,
        'text': fournisseur.nom,
        'message': 'Fournisseur ajouté avec succès.'
    })


@login_required
@require_http_methods(["POST"])
def vehicule_quick_create_ajax(request):
    """Crée rapidement un véhicule via AJAX et renvoie son id et libellé pour Select2.
    Les champs requis du modèle Vehicule sont nombreux; on crée un enregistrement minimal
    en générant un id_vehicule unique et en utilisant les champs basiques fournis.
    """
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Requête non autorisée'}, status=400)

    immatriculation = request.POST.get('immatriculation', '').strip()
    marque = request.POST.get('marque', '').strip()
    modele = request.POST.get('modele', '').strip()
    type_moteur = request.POST.get('type_moteur', '').strip()
    categorie = request.POST.get('categorie', '').strip()
    statut_actuel = request.POST.get('statut_actuel', '').strip()

    # validations minimales
    missing = []
    if not immatriculation: missing.append('immatriculation')
    if not marque: missing.append('marque')
    if not modele: missing.append('modele')
    if not type_moteur: missing.append('type_moteur')
    if not categorie: missing.append('categorie')
    if not statut_actuel: missing.append('statut_actuel')
    if missing:
        return JsonResponse({'success': False, 'message': f"Champs requis manquants: {', '.join(missing)}"}, status=400)

    # Génération d'un id_vehicule unique (max_length=20)
    # Format compact: A + yymmddHHMMSS + 3 chiffres aléatoires (<= 1+12+3 = 16)
    import datetime, random
    ts = datetime.datetime.now().strftime('%y%m%d%H%M%S')  # 12 chars
    rnd = random.randint(100, 999)  # 3 chars
    id_vehicule = f"A{ts}{rnd}"

    # Création du véhicule
    ent = getattr(getattr(request.user, 'profil', None), 'entreprise', None) or getattr(request.user, 'entreprise', None)
    v = Vehicule.objects.create(
        id_vehicule=id_vehicule,
        immatriculation=immatriculation,
        marque=marque,
        modele=modele,
        type_moteur=type_moteur,
        categorie=categorie,
        statut_actuel=statut_actuel,
        user=request.user,
        entreprise=ent,
    )

    return JsonResponse({
        'success': True,
        'id': v.pk,
        'text': f"{v.immatriculation} - {v.marque} {v.modele}",
        'message': 'Véhicule ajouté avec succès.'
    })


@login_required
def facture_pdf(request, pk):
    """Génère et télécharge une facture en PDF"""
    facture = get_object_or_404(queryset_filter_by_tenant(FactureLocation.objects.all(), request), pk=pk)
    
    # Récupérer les informations de l'entreprise
    entreprise = None
    if hasattr(request.user, 'profil') and request.user.profil.entreprise:
        entreprise = request.user.profil.entreprise
    elif hasattr(request.user, 'entreprise'):
        entreprise = request.user.entreprise
    
    # Récupérer les détails des feuilles de pontage pour cette facture
    # Calculer la période de facturation basée sur la date de la facture
    date_facture = facture.date
    if date_facture.day <= 15:
        # Facture du mois précédent
        if date_facture.month == 1:
            year = date_facture.year - 1
            month = 12
        else:
            year = date_facture.year
            month = date_facture.month - 1
    else:
        # Facture du mois courant
        year = date_facture.year
        month = date_facture.month
    
    first_day = timezone.datetime(year, month, 1).date()
    last_day = timezone.datetime(year, month, calendar.monthrange(year, month)[1]).date()
    
    # Récupérer les feuilles de pontage de la période
    feuilles_travail = facture.location.feuilles.filter(
        statut="Travail",
        date__gte=first_day,
        date__lte=last_day
    ).order_by('date')
    
    feuilles_autres = facture.location.feuilles.filter(
        statut__in=["Entretien", "Hors service", "Inactif"],
        date__gte=first_day,
        date__lte=last_day
    ).order_by('date')
    
    context = {
        'facture': facture,
        'entreprise': entreprise,
        'location': facture.location,
        'vehicule': facture.location.vehicule,
        'fournisseur': facture.location.fournisseur,
        'periode_debut': first_day,
        'periode_fin': last_day,
        'feuilles_travail': feuilles_travail,
        'feuilles_autres': feuilles_autres,
        'jours_travail': feuilles_travail.count(),
        'jours_autres': feuilles_autres.count(),
        'today': timezone.now().date(),
    }
    
    # Rendu du template HTML
    template = get_template('fleet_app/locations/facture_pdf_template.html')
    html = template.render(context)
    
    # Création du PDF
    try:
        from xhtml2pdf import pisa
    except Exception:
        messages.error(request, "Génération PDF indisponible: dépendances non installées (xhtml2pdf/reportlab).")
        return redirect('fleet_app:facture_location_detail', pk=pk)

    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        # Retourner le PDF en réponse
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{facture.numero}.pdf"'
        return response
    
    # En cas d'erreur, rediriger avec un message d'erreur
    messages.error(request, 'Erreur lors de la génération du PDF')
    return redirect('fleet_app:facture_location_detail', pk=pk)


@login_required
def factures_batch_pdf(request):
    """Génère un PDF contenant plusieurs factures sélectionnées"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    facture_ids = request.POST.getlist('facture_ids[]')
    if not facture_ids:
        return JsonResponse({'error': 'Aucune facture sélectionnée'}, status=400)
    
    factures = queryset_filter_by_tenant(FactureLocation.objects.all(), request).filter(
        id__in=facture_ids
    ).select_related('location', 'location__vehicule', 'location__fournisseur')
    
    if not factures.exists():
        return JsonResponse({'error': 'Aucune facture trouvée'}, status=404)
    
    # Récupérer les informations de l'entreprise
    entreprise = None
    if hasattr(request.user, 'profil') and request.user.profil.entreprise:
        entreprise = request.user.profil.entreprise
    elif hasattr(request.user, 'entreprise'):
        entreprise = request.user.entreprise
    
    context = {
        'factures': factures,
        'entreprise': entreprise,
        'today': timezone.now().date(),
        'total_ht': factures.aggregate(total=Sum('montant_ht'))['total'] or 0,
        'total_tva': factures.aggregate(total=Sum('tva'))['total'] or 0,
        'total_ttc': factures.aggregate(total=Sum('montant_ttc'))['total'] or 0,
    }
    
    # Rendu du template HTML
    template = get_template('fleet_app/locations/factures_batch_pdf_template.html')
    html = template.render(context)
    
    # Création du PDF
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        # Retourner le PDF en réponse
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        filename = f"factures_lot_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    return JsonResponse({'error': 'Erreur lors de la génération du PDF'}, status=500)


@login_required
def get_vehicule_fournisseur_ajax(request):
    """Vue AJAX pour récupérer le fournisseur d'un véhicule"""
    vehicule_id = request.GET.get('vehicule_id', '')
    
    if not vehicule_id:
        return JsonResponse({'error': 'ID véhicule manquant'}, status=400)
    
    try:
        vehicule = Vehicule.objects.filter(id_vehicule=vehicule_id, user=request.user).first()
        
        if not vehicule:
            return JsonResponse({'error': 'Véhicule non trouvé'}, status=404)
        
        if vehicule.fournisseur:
            return JsonResponse({
                'fournisseur_id': vehicule.fournisseur.id,
                'fournisseur_nom': vehicule.fournisseur.nom,
                'fournisseur_contact': vehicule.fournisseur.contact or '',
                'fournisseur_telephone': vehicule.fournisseur.telephone or '',
            })
        else:
            return JsonResponse({'fournisseur_id': None})
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
