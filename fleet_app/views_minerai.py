from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.db.models import Sum, Avg, Q
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
    pesees = PeseeCamion.objects.filter(user=request.user).order_by('-date')
    
    context = {
        'pesees': pesees,
        'message': "Liste des pesées de camions"
    }
    
    return render(request, 'fleet_app/entreprise/pesee_camion_list.html', context)

@login_required
def fiche_bord_machine_list(request):
    """
    Vue pour afficher la liste des fiches de bord machine
    Filtrée pour n'afficher que les fiches de l'utilisateur connecté
    """
    try:
        # Récupérer uniquement les fiches de bord machine de l'utilisateur connecté
        fiches = FicheBordMachine.objects.filter(user=request.user).order_by('-annee', '-mois')
        
        # Ajouter le comptage des entrées pour chaque fiche
        for fiche in fiches:
            try:
                fiche.entrees_count = fiche.entrees.count() if hasattr(fiche, 'entrees') else 0
            except:
                fiche.entrees_count = 0
        
        context = {
            'fiches': fiches,
            'message': "Liste des fiches de bord machine"
        }
        
        return render(request, 'fleet_app/entreprise/fiche_bord_machine_list.html', context)
    
    except Exception as e:
        # En cas d'erreur (comme la colonne manquante), afficher un message d'erreur
        context = {
            'fiches': [],
            'message': f"Erreur lors du chargement des fiches: {str(e)}. Veuillez appliquer les migrations en cours.",
            'error': True
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
    # Récupérer uniquement les fiches d'or de l'utilisateur connecté
    fiches_or = FicheOr.objects.filter(user=request.user).order_by('-annee', '-mois')
    
    context = {
        'fiches_or': fiches_or,
        'message': "Liste des fiches d'or"
    }
    
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
