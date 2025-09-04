from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg, Q, Count
from django.urls import reverse
import csv
import io
from datetime import datetime

# Import des modèles et formulaires nécessaires
from .models_entreprise import PeseeCamion, FicheOr, FicheBordMachine
from .forms_entreprise import PeseeCamionForm, FicheOrForm, FicheOrFormManuel, FicheBordMachineForm

@login_required
def pesee_camion_list(request):
    """
    Vue pour afficher la liste des pesées de camions
    Filtrée pour n'afficher que les pesées de l'utilisateur connecté
    """
    # Récupérer uniquement les pesées de camions de l'utilisateur connecté
    qs = PeseeCamion.objects.filter(user=request.user)

    # Filtre dynamique unique 'q'
    q = (request.GET.get('q') or '').strip()
    from datetime import datetime as _dt
    import re
    if q:
        # 1) Plage de dates: YYYY-MM-DD..YYYY-MM-DD
        m = re.search(r'(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})', q)
        if m:
            try:
                d1 = _dt.strptime(m.group(1), '%Y-%m-%d').date()
                d2 = _dt.strptime(m.group(2), '%Y-%m-%d').date()
                qs = qs.filter(date__gte=d1, date__lte=d2)
            except ValueError:
                pass
            # retirer ce fragment de la requête pour ne pas le re-traiter
            q = q.replace(m.group(0), '').strip()

        # 2) Mots-clés: date_debut:, date_fin:, plate:, zone:
        # Exemple: plate:ABC123 zone:Mine-1 date_debut:2025-08-01 date_fin:2025-08-31
        tokens = q.split()
        remaining_terms = []
        for t in tokens:
            if t.lower().startswith('plate:'):
                val = t.split(':', 1)[1]
                if val:
                    qs = qs.filter(plate__icontains=val)
            elif t.lower().startswith('zone:'):
                val = t.split(':', 1)[1]
                if val:
                    qs = qs.filter(loading_zone__icontains=val)
            elif t.lower().startswith('date_debut:'):
                val = t.split(':', 1)[1]
                try:
                    d = _dt.strptime(val, '%Y-%m-%d').date()
                    qs = qs.filter(date__gte=d)
                except Exception:
                    pass
            elif t.lower().startswith('date_fin:'):
                val = t.split(':', 1)[1]
                try:
                    d = _dt.strptime(val, '%Y-%m-%d').date()
                    qs = qs.filter(date__lte=d)
                except Exception:
                    pass
            else:
                remaining_terms.append(t)

        # 3) Termes restants: recherche floue sur plaque et zone
        for term in remaining_terms:
            if term:
                qs = qs.filter(Q(plate__icontains=term) | Q(loading_zone__icontains=term))

    qs = qs.order_by('-date', '-weighing_end')

    # Statistiques sur le queryset filtré
    stats = {
        'total_pesees': qs.count(),
        'total_quantite': qs.aggregate(s=Sum('quantity'))['s'] or 0,
        'moyenne_quantite': qs.aggregate(a=Avg('quantity'))['a'] or 0,
        'top_plaques': list(qs.values('plate').annotate(total=Sum('quantity'), n=Count('id')).order_by('-total')[:5]),
        'top_zones': list(qs.values('loading_zone').annotate(total=Sum('quantity'), n=Count('id')).order_by('-total')[:5]),
    }

    # Pagination (25 par page)
    from django.core.paginator import Paginator
    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    pesees_page = paginator.get_page(page_number)

    context = {
        'pesees': pesees_page,
        'stats': stats,
        'message': "Liste des pesées de camions",
        'q': (request.GET.get('q') or '').strip(),
    }
    if request.GET.get('partial') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'fleet_app/entreprise/partials/pesee_camion_list_partial.html', context)
    return render(request, 'fleet_app/entreprise/pesee_camion_list.html', context)

@login_required
def fiche_bord_machine_list(request):
    """
    Vue pour afficher la liste des fiches de bord machine
    Filtrée pour n'afficher que les fiches de l'utilisateur connecté
    """
    try:
        qs = FicheBordMachine.objects.filter(user=request.user)

        # Recherche dynamique 'q'
        q = (request.GET.get('q') or '').strip()
        from datetime import datetime as _dt
        import re
        if q:
            # Plage de dates: YYYY-MM-DD..YYYY-MM-DD
            m = re.search(r'(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})', q)
            if m:
                try:
                    d1 = _dt.strptime(m.group(1), '%Y-%m-%d').date()
                    d2 = _dt.strptime(m.group(2), '%Y-%m-%d').date()
                    qs = qs.filter(date__gte=d1, date__lte=d2)
                except ValueError:
                    pass
                q = q.replace(m.group(0), '').strip()

            tokens = q.split()
            remaining_terms = []
            for t in tokens:
                if t.lower().startswith('date_debut:'):
                    val = t.split(':', 1)[1]
                    try:
                        d = _dt.strptime(val, '%Y-%m-%d').date()
                        qs = qs.filter(date__gte=d)
                    except Exception:
                        pass
                elif t.lower().startswith('date_fin:'):
                    val = t.split(':', 1)[1]
                    try:
                        d = _dt.strptime(val, '%Y-%m-%d').date()
                        qs = qs.filter(date__lte=d)
                    except Exception:
                        pass
                elif t.lower().startswith('machine:'):
                    val = t.split(':', 1)[1]
                    if val:
                        qs = qs.filter(Q(machine__nom__icontains=val) | Q(machine__immatriculation__icontains=val))
                elif t.lower().startswith('chauffeur:'):
                    val = t.split(':', 1)[1]
                    if val:
                        qs = qs.filter(Q(chauffeur__prenom__icontains=val) | Q(chauffeur__nom__icontains=val))
                else:
                    remaining_terms.append(t)

            for term in remaining_terms:
                if term:
                    qs = qs.filter(
                        Q(machine__nom__icontains=term) |
                        Q(machine__immatriculation__icontains=term) |
                        Q(chauffeur__prenom__icontains=term) |
                        Q(chauffeur__nom__icontains=term)
                    )

        qs = qs.order_by('-date')

        # Statistiques
        stats = {
            'total_fiches': qs.count(),
            'total_heures': qs.aggregate(s=Sum('heures_travail'))['s'] or 0,
            'total_carburant': qs.aggregate(s=Sum('carburant_consomme'))['s'] or 0,
            'top_machines': list(qs.values('machine__nom', 'machine__immatriculation').annotate(n=Count('id'), heures=Sum('heures_travail')).order_by('-heures')[:5]),
            'top_chauffeurs': list(qs.values('chauffeur__prenom', 'chauffeur__nom').annotate(n=Count('id'), heures=Sum('heures_travail')).order_by('-heures')[:5]),
        }

        # Enrichir avec entrees_count
        from django.core.paginator import Paginator
        paginator = Paginator(qs, 25)
        page_number = request.GET.get('page')
        fiches_page = paginator.get_page(page_number)
        for fiche in fiches_page:
            try:
                fiche.entrees_count = fiche.entrees.count() if hasattr(fiche, 'entrees') else 0
            except Exception:
                fiche.entrees_count = 0

        context = {
            'fiches': fiches_page,
            'stats': stats,
            'message': "Liste des fiches de bord machine",
            'q': (request.GET.get('q') or '').strip(),
        }
        if request.GET.get('partial') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return render(request, 'fleet_app/entreprise/partials/fiche_bord_machine_list_partial.html', context)
        return render(request, 'fleet_app/entreprise/fiche_bord_machine_list.html', context)

    except Exception as e:
        context = {
            'fiches': [],
            'stats': None,
            'message': f"Erreur lors du chargement des fiches: {str(e)}. Veuillez appliquer les migrations en cours.",
            'error': True,
            'q': (request.GET.get('q') or '').strip(),
        }
        return render(request, 'fleet_app/entreprise/fiche_bord_machine_list.html', context)

@login_required
def fiche_bord_machine_add(request):
    """
    Vue pour ajouter une nouvelle fiche de bord machine
    Associe automatiquement l'utilisateur connecté à la fiche
    """
    if request.method == 'POST':
        form = FicheBordMachineForm(request.POST)
        if form.is_valid():
            # Créer la fiche sans l'enregistrer pour pouvoir associer l'utilisateur connecté
            fiche = form.save(commit=False)
            # Associer l'utilisateur connecté à la fiche
            fiche.user = request.user
            # Associer l'entreprise de l'utilisateur connecté si disponible
            if hasattr(request.user, 'entreprise'):
                fiche.entreprise = request.user.entreprise
            # Enregistrer la fiche avec les associations utilisateur et entreprise
            fiche.save()
            messages.success(request, f"La fiche de bord machine a été ajoutée avec succès.")
            return redirect('fleet_app:fiche_bord_machine_list')
        else:
            messages.error(request, "Erreur lors de l'ajout de la fiche de bord machine. Veuillez vérifier les informations saisies.")
    else:
        form = FicheBordMachineForm()
    
    context = {
        'form': form,
        'title': "Ajouter une fiche de bord machine"
    }
    
    return render(request, 'fleet_app/entreprise/fiche_bord_machine_form.html', context)

@login_required
def fiche_or_list(request):
    """
    Vue pour afficher la liste des fiches d'or
    Filtrée pour n'afficher que les fiches de l'utilisateur connecté
    """
    qs = FicheOr.objects.filter(user=request.user)

    # Recherche dynamique 'q'
    q = (request.GET.get('q') or '').strip()
    from datetime import datetime as _dt
    import re
    if q:
        m = re.search(r'(\d{4}-\d{2}-\d{2})\.\.(\d{4}-\d{2}-\d{2})', q)
        if m:
            try:
                d1 = _dt.strptime(m.group(1), '%Y-%m-%d').date()
                d2 = _dt.strptime(m.group(2), '%Y-%m-%d').date()
                qs = qs.filter(date__gte=d1, date__lte=d2)
            except ValueError:
                pass
            q = q.replace(m.group(0), '').strip()

        # Parsing des termes de recherche
        terms = q.split()
        remaining_terms = []
        for t in terms:
            if ':' in t:
                key, val = t.split(':', 1)
                if key == 'date_debut' and val:
                    try:
                        date_debut = datetime.strptime(val, '%Y-%m-%d').date()
                        qs = qs.filter(date__gte=date_debut)
                    except ValueError:
                        pass
                elif key == 'date_fin' and val:
                    try:
                        date_fin = datetime.strptime(val, '%Y-%m-%d').date()
                        qs = qs.filter(date__lte=date_fin)
                    except ValueError:
                        pass
                elif key == 'lieu' and val:
                    qs = qs.filter(entrees__lieu__icontains=val)
            else:
                remaining_terms.append(t)

        for term in remaining_terms:
            if term:
                qs = qs.filter(Q(entrees__lieu__icontains=term))

    qs = qs.order_by('-date')

    # Statistiques - agrégation depuis les entrées liées
    stats = {
        'total_fiches': qs.count(),
        'total_quantite': qs.aggregate(s=Sum('entrees__quantite'))['s'] or 0,
        'total_valeur': qs.aggregate(s=Sum('entrees__total_obtenu'))['s'] or 0,
        'top_sites': list(qs.values('entrees__lieu').annotate(n=Count('id'), q=Sum('entrees__quantite')).exclude(entrees__lieu__isnull=True).order_by('-q')[:5]),
        'top_responsables': [],  # Pas de champ responsable dans EntreeFicheOr
    }

    from django.core.paginator import Paginator
    paginator = Paginator(qs, 25)
    page_number = request.GET.get('page')
    fiches_page = paginator.get_page(page_number)
    # Ajouter entrees_count si relation disponible
    for fiche in fiches_page:
        try:
            fiche.entrees_count = fiche.entrees.count() if hasattr(fiche, 'entrees') else 0
        except Exception:
            fiche.entrees_count = 0

    context = {
        'fiches': fiches_page,
        'stats': stats,
        'message': "Liste des fiches d'or",
        'q': (request.GET.get('q') or '').strip(),
    }
    if request.GET.get('partial') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return render(request, 'fleet_app/entreprise/partials/fiche_or_list_partial.html', context)
    return render(request, 'fleet_app/entreprise/fiche_or_list.html', context)

@login_required
def fiche_or_add(request):
    """
    Vue pour ajouter une nouvelle fiche d'or
    Associe automatiquement l'utilisateur connecté à la fiche
    """
    if request.method == 'POST':
        form = FicheOrFormManuel(request.POST)
        if form.is_valid():
            # Récupérer les données du formulaire
            date = form.cleaned_data['date']
            site = form.cleaned_data['site']
            responsable = form.cleaned_data['responsable']
            equipe = form.cleaned_data['equipe']
            quantite_totale = form.cleaned_data['quantite_totale']
            prix_unitaire = form.cleaned_data['prix_unitaire']
            valeur_estimee = form.cleaned_data['valeur_estimee']
            observations = form.cleaned_data['observations']
            
            # Créer une instance de FicheOr avec les champs disponibles
            fiche = FicheOr(
                mois=date.month,
                annee=date.year,
                # Associer l'utilisateur connecté à la fiche
                user=request.user
            )
            
            # Associer l'entreprise de l'utilisateur connecté si disponible
            if hasattr(request.user, 'entreprise'):
                fiche.entreprise = request.user.entreprise
                
            fiche.save()
            
            messages.success(request, f"La fiche d'or pour {site} a été ajoutée avec succès.")
            return redirect('fleet_app:fiche_or_list')
        else:
            messages.error(request, "Erreur lors de l'ajout de la fiche d'or. Veuillez vérifier les informations saisies.")
    else:
        form = FicheOrFormManuel()
    
    context = {
        'form': form,
        'title': "Ajouter une fiche d'or"
    }
    
    return render(request, 'fleet_app/entreprise/fiche_or_form.html', context)

@login_required
def fiche_or_export(request):
    """Vue pour exporter les fiches d'or au format CSV"""
    # Préparer la réponse CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes du CSV
    headers = ['ID', 'Mois', 'Année', 'Quantité Or Total (g)']
    writer.writerow(headers)
    
    # Filtrer les données selon les mêmes critères que la vue liste
    # Sécurité : Ne récupérer que les fiches d'or de l'utilisateur connecté
    queryset = FicheOr.objects.filter(user=request.user)
    
    # Filtrer par période (mois/année) si spécifiée
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if date_debut:
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            # Filtrer par mois et année
            queryset = queryset.filter(
                Q(annee__gt=date_debut.year) | 
                Q(annee=date_debut.year, mois__gte=date_debut.month)
            )
        except ValueError:
            pass
    
    if date_fin:
        try:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            # Filtrer par mois et année
            queryset = queryset.filter(
                Q(annee__lt=date_fin.year) | 
                Q(annee=date_fin.year, mois__lte=date_fin.month)
            )
        except ValueError:
            pass
    
    # Trier par année et mois
    queryset = queryset.order_by('-annee', '-mois')
    
    # Ajouter les données au CSV
    for fiche in queryset:
        # Calculer la quantité totale d'or pour cette fiche
        quantite_total = fiche.entrees.aggregate(Sum('quantite_or'))['quantite_or__sum'] or 0
        
        row = [
            fiche.id,
            fiche.mois,
            fiche.annee,
            quantite_total
        ]
        writer.writerow(row)
    
    # Préparer la réponse HTTP
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fiches_or.csv"'
    
    return response

@login_required
def fiche_bord_machine_export(request):
    """Vue pour exporter les fiches de bord machine au format CSV"""
    # Préparer la réponse CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # En-têtes du CSV
    headers = [
        'ID', 'Mois', 'Année', 
        'Date dernier service', 'Heure dernier service', 'Compteur dernier service',
        'Date prochain service', 'Heure prochain service', 'Compteur prochain service'
    ]
    writer.writerow(headers)
    
    # Filtrer les données selon les mêmes critères que la vue liste
    # Sécurité : Ne récupérer que les fiches de bord machine de l'utilisateur connecté
    queryset = FicheBordMachine.objects.filter(user=request.user)
    
    # Filtrer par période (mois/année) si spécifiée
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    if date_debut:
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            # Filtrer par mois et année
            queryset = queryset.filter(
                Q(annee__gt=date_debut.year) | 
                Q(annee=date_debut.year, mois__gte=date_debut.month)
            )
        except ValueError:
            pass
    
    if date_fin:
        try:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            # Filtrer par mois et année
            queryset = queryset.filter(
                Q(annee__lt=date_fin.year) | 
                Q(annee=date_fin.year, mois__lte=date_fin.month)
            )
        except ValueError:
            pass
    
    # Trier par année et mois
    queryset = queryset.order_by('-annee', '-mois')
    
    # Ajouter les données au CSV
    for fiche in queryset:
        row = [
            fiche.id,
            fiche.mois,
            fiche.annee,
            fiche.dernier_service_date,
            fiche.dernier_service_heure,
            fiche.dernier_service_compteur,
            fiche.prochain_service_date,
            fiche.prochain_service_heure,
            fiche.prochain_service_compteur
        ]
        writer.writerow(row)
    
    # Préparer la réponse HTTP
    response = HttpResponse(output.getvalue(), content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="fiches_bord_machine.csv"'
    
    return response

@login_required
def pesee_camion_add(request):
    """
    Vue pour ajouter une nouvelle pesée de camion
    Sécurisée pour associer automatiquement l'utilisateur connecté à la nouvelle pesée
    """
    if request.method == 'POST':
        form = PeseeCamionForm(request.POST)
        if form.is_valid():
            # Associer l'utilisateur connecté à la nouvelle pesée
            pesee = form.save(commit=False)
            pesee.user = request.user
            
            # Récupérer l'entreprise de l'utilisateur connecté
            try:
                from fleet_app.models_accounts import Profil
                profil = Profil.objects.get(user=request.user)
                if hasattr(profil, 'entreprise') and profil.entreprise:
                    pesee.entreprise = profil.entreprise
            except Exception as e:
                # En cas d'erreur, on continue sans associer d'entreprise
                pass
                
            pesee.save()
            messages.success(request, "La pesée de camion a été ajoutée avec succès.")
            return redirect('fleet_app:pesee_camion_list')
    else:
        # Initialiser le formulaire avec la date du jour
        form = PeseeCamionForm(initial={'date': timezone.now().date()})
    
    context = {
        'form': form,
        'message': "Formulaire d'ajout de pesée de camion"
    }
    
    return render(request, 'fleet_app/entreprise/pesee_camion_form.html', context)

@login_required
def pesee_camion_detail(request, pk):
    """
    Vue pour afficher les détails d'une pesée de camion
    Sécurisée pour n'afficher que les pesées de l'utilisateur connecté
    """
    # Récupérer la pesée de camion de l'utilisateur connecté ou renvoyer une erreur 404
    pesee = get_object_or_404(PeseeCamion, pk=pk, user=request.user)
    
    context = {
        'pesee': pesee,
        'title': f"Détails de la pesée de camion {pesee.plate} du {pesee.date}"
    }
    
    return render(request, 'fleet_app/entreprise/pesee_camion_detail.html', context)

@login_required
def pesee_camion_update(request, pk):
    """
    Vue pour modifier une pesée de camion existante
    Sécurisée pour ne permettre la modification que des pesées de l'utilisateur connecté
    """
    # Récupérer la pesée de camion de l'utilisateur connecté ou renvoyer une erreur 404
    pesee = get_object_or_404(PeseeCamion, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = PeseeCamionForm(request.POST, instance=pesee)
        if form.is_valid():
            form.save()
            messages.success(request, "La pesée de camion a été modifiée avec succès.")
            return redirect('fleet_app:pesee_camion_detail', pk=pesee.pk)
    else:
        form = PeseeCamionForm(instance=pesee)
    
    context = {
        'form': form,
        'pesee': pesee,
        'title': f"Modifier la pesée de camion {pesee.plate} du {pesee.date}"
    }
    
    return render(request, 'fleet_app/entreprise/pesee_camion_form.html', context)

@login_required
def pesee_camion_edit(request, pk):
    """
    Alias pour pesee_camion_update pour compatibilité avec les URLs existantes
    """
    return pesee_camion_update(request, pk)

@login_required
def pesee_camion_delete(request, pk):
    """
    Vue pour supprimer une pesée de camion
    Sécurisée pour ne permettre la suppression que des pesées de l'utilisateur connecté
    """
    # Récupérer la pesée de camion de l'utilisateur connecté ou renvoyer une erreur 404
    pesee = get_object_or_404(PeseeCamion, pk=pk, user=request.user)
    
    if request.method == 'POST':
        # Stocker les informations pour le message de confirmation
        plate = pesee.plate
        date = pesee.date
        
        # Supprimer la pesée
        pesee.delete()
        
        messages.success(request, f"La pesée de camion {plate} du {date} a été supprimée avec succès.")
        return redirect('fleet_app:pesee_camion_list')
    
    context = {
        'pesee': pesee,
        'title': f"Supprimer la pesée de camion {pesee.plate} du {pesee.date}"
    }
    
    return render(request, 'fleet_app/entreprise/pesee_camion_confirm_delete.html', context)
