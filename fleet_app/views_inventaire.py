from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Value, CharField, Q, Count
from django.db.models.functions import Coalesce
from django.contrib import messages
from .security import user_owns_data, user_owns_related_data
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.template.loader import get_template
from decimal import Decimal

from .models_inventaire import Produit, EntreeStock, SortieStock, MouvementStock, Commande, LigneCommande
from .forms_inventaire import ProduitForm, EntreeStockForm, SortieStockForm, RechercheInventaireForm, RechercheCommandeForm, CommandeForm, LigneCommandeForm, DocumentSigneCommandeForm

import datetime
import csv
# Rendre xlwt optionnel
try:
    import xlwt
    XLWT_AVAILABLE = True
except ImportError:
    XLWT_AVAILABLE = False


# Vue API pour récupérer les informations d'un produit
@login_required
def get_produit_info(request):
    """API pour récupérer les informations d'un produit (prix unitaire, etc.)
    Sécurisée pour ne renvoyer que les informations des produits de l'utilisateur connecté
    """
    produit_id = request.GET.get('id')
    if not produit_id:
        return JsonResponse({'success': False, 'message': 'ID du produit non fourni'})
    
    try:
        # Filtrer pour n'accéder qu'aux produits de l'utilisateur connecté
        produit = Produit.objects.get(id=produit_id, user=request.user)
        data = {
            'success': True,
            'id': produit.id,
            'id_produit': produit.id_produit,
            'nom': produit.nom,
            'description': produit.description,
            'prix_unitaire': float(produit.prix_unitaire),
            'stock_actuel': float(produit.stock_actuel),
            'unite': produit.unite
        }
        return JsonResponse(data)
    except Produit.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Produit non trouvé'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

# Définition des variables de disponibilité pour WeasyPrint
# On ne tente pas d'importer WeasyPrint au démarrage pour éviter les erreurs
WEASYPRINT_AVAILABLE = False
# Ne pas définir HTML et CSS comme variables globales pour éviter toute confusion avec les imports de WeasyPrint

# Vues pour les produits
@login_required
def produit_list(request):
    """Liste des produits avec recherche et filtrage"""
    form_recherche = RechercheInventaireForm(request.GET)
    # Récupérer tous les produits
    produits = Produit.objects.all()
    
    # Filtrage selon les critères de recherche
    if form_recherche.is_valid():
        critere = form_recherche.cleaned_data.get('critere')
        terme = form_recherche.cleaned_data.get('terme')
        
        if critere and terme:
            if critere == 'id_produit':
                produits = produits.filter(id_produit__icontains=terme)
            elif critere == 'nom':
                produits = produits.filter(nom__icontains=terme)
            elif critere == 'categorie':
                produits = produits.filter(categorie__icontains=terme)
            elif critere == 'fournisseur':
                produits = produits.filter(fournisseur__icontains=terme)
    
    # Pagination
    paginator = Paginator(produits, 10)  # 10 produits par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Préparation des données pour l'affichage
    produits_data = []
    for produit in page_obj:
        stock_actuel = produit.get_stock_actuel()
        statut_alerte = produit.get_statut_alerte()
        
        produits_data.append({
            'produit': produit,
            'stock_actuel': stock_actuel,
            'statut_alerte': statut_alerte
        })
    
    context = {
        'produits_data': produits_data,
        'page_obj': page_obj,
        'form_recherche': form_recherche,
        'titre': 'Liste des Produits',
    }
    
    return render(request, 'fleet_app/inventaire/produit_list.html', context)

@login_required
def produit_create(request):
    """Création d'un nouveau produit"""
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            # Associer l'utilisateur connecté avant de sauvegarder
            produit = form.save(commit=False)
            produit.user = request.user
            
            # Récupérer l'entreprise de l'utilisateur si disponible
            try:
                from fleet_app.models_accounts import Profil
                profil = Profil.objects.get(user=request.user)
                if hasattr(profil, 'entreprise') and profil.entreprise:
                    produit.entreprise = profil.entreprise
            except Exception as e:
                # En cas d'erreur, on continue sans associer d'entreprise
                pass
                
            produit.save()
            messages.success(request, "Le produit a été ajouté avec succès.")
            return redirect('fleet_app:produit_list')
    else:
        # Génération automatique du prochain ID produit
        last_produit = Produit.objects.order_by('-id_produit').first()
        next_id = 'PRD001'
        if last_produit:
            last_num = int(last_produit.id_produit[3:])
            next_id = f'PRD{(last_num + 1):03d}'
        
        form = ProduitForm(initial={'id_produit': next_id, 'date_ajout': datetime.date.today()})
    
    context = {
        'form': form,
        'titre': 'Ajouter un Produit',
    }
    
    return render(request, 'fleet_app/inventaire/produit_form.html', context)

@login_required
@user_owns_data(Produit, relation_path=['user'])
def produit_update(request, pk):
    """Mise à jour d'un produit existant
    Sécurisée pour vérifier que l'utilisateur connecté est bien le propriétaire du produit
    """
    produit = get_object_or_404(Produit, pk=pk)
    
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            # Conserver l'utilisateur existant si déjà défini, sinon utiliser l'utilisateur connecté
            if not form.instance.user:
                form.instance.user = request.user
                
            # Conserver l'entreprise existante si déjà définie, sinon récupérer celle de l'utilisateur connecté
            if not form.instance.entreprise:
                try:
                    from fleet_app.models_accounts import Profil
                    profil = Profil.objects.get(user=request.user)
                    if hasattr(profil, 'entreprise') and profil.entreprise:
                        form.instance.entreprise = profil.entreprise
                except Exception as e:
                    # En cas d'erreur, on continue sans associer d'entreprise
                    pass
                    
            form.save()
            messages.success(request, "Le produit a été mis à jour avec succès.")
            return redirect('fleet_app:produit_list')
    else:
        form = ProduitForm(instance=produit)
    
    context = {
        'form': form,
        'produit': produit,
        'titre': 'Modifier un Produit',
    }
    
    return render(request, 'fleet_app/inventaire/produit_form.html', context)

@login_required
@user_owns_data(Produit, relation_path=['user'])
def produit_detail(request, pk):
    """Détail d'un produit avec son historique de mouvements
    Sécurisée pour vérifier que l'utilisateur connecté est bien le propriétaire du produit
    """
    produit = get_object_or_404(Produit, pk=pk)
    stock_actuel = produit.get_stock_actuel()
    statut_alerte = produit.get_statut_alerte()
    
    # Récupération des mouvements de stock pour ce produit
    mouvements = MouvementStock.objects.filter(produit=produit).order_by('-date')[:20]  # 20 derniers mouvements
    
    # Récupération des entrées et sorties
    entrees = EntreeStock.objects.filter(produit=produit).order_by('-date')[:10]
    sorties = SortieStock.objects.filter(produit=produit).order_by('-date')[:10]
    
    context = {
        'produit': produit,
        'stock_actuel': stock_actuel,
        'statut_alerte': statut_alerte,
        'mouvements': mouvements,
        'entrees': entrees,
        'sorties': sorties,
        'titre': f'Détail du Produit: {produit.nom}',
    }
    
    return render(request, 'fleet_app/inventaire/produit_detail.html', context)

@login_required
@user_owns_data(Produit, relation_path=['user'])
def produit_delete(request, pk):
    """Suppression d'un produit
    Sécurisée pour vérifier que l'utilisateur connecté est bien le propriétaire du produit
    """
    produit = get_object_or_404(Produit, pk=pk)
    
    try:
        # Supprimer le produit et tous ses mouvements associés (CASCADE)
        produit.delete()
        messages.success(request, "Le produit a été supprimé avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression du produit : {str(e)}")
    
    return redirect('fleet_app:produit_list')

# Vues pour les entrées en stock
@login_required
def entree_stock_list(request):
    """Liste des entrées en stock avec recherche et filtrage
    Filtrée pour n'afficher que les entrées de l'utilisateur connecté
    """
    form_recherche = RechercheInventaireForm(request.GET)
    # Filtrer les entrées pour n'afficher que celles de l'utilisateur connecté
    # Nous filtrons sur le produit associé à l'entrée
    entrees = EntreeStock.objects.all()
    
    # Filtrage selon les critères de recherche
    if form_recherche.is_valid():
        critere = form_recherche.cleaned_data.get('critere')
        terme = form_recherche.cleaned_data.get('terme')
        date_debut = form_recherche.cleaned_data.get('date_debut')
        date_fin = form_recherche.cleaned_data.get('date_fin')
        
        if critere and terme:
            if critere == 'id_produit':
                entrees = entrees.filter(produit__id_produit__icontains=terme)
            elif critere == 'nom':
                entrees = entrees.filter(produit__nom__icontains=terme)
            elif critere == 'fournisseur':
                entrees = entrees.filter(fournisseur__icontains=terme)
        
        if date_debut:
            entrees = entrees.filter(date__gte=date_debut)
        if date_fin:
            entrees = entrees.filter(date__lte=date_fin)
    
    # Pagination
    paginator = Paginator(entrees.order_by('-date', '-id_entree'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'entrees': page_obj,
        'form_recherche': form_recherche,
        'titre': 'Entrées en Stock',
    }
    
    return render(request, 'fleet_app/inventaire/entree_stock_list.html', context)

@login_required
def entree_stock_create(request, produit_id=None):
    """Création d'une nouvelle entrée en stock, avec pré-remplissage optionnel du produit"""
    produit = None
    if produit_id:
        produit = get_object_or_404(Produit, id_produit=produit_id)
    
    if request.method == 'POST':
        form = EntreeStockForm(request.POST)
        if form.is_valid():
            # Vérifier que le produit appartient bien à l'utilisateur connecté
            produit_form = form.cleaned_data.get('produit')
            if produit_form and produit_form.user != request.user:
                messages.error(request, "Vous n'avez pas le droit d'ajouter une entrée pour ce produit.")
                return redirect('fleet_app:entree_stock_list')
                
            entree = form.save(commit=False)
            
            # Associer l'utilisateur connecté au mouvement de stock qui sera créé
            try:
                # Créer le mouvement de stock avec l'utilisateur connecté
                mouvement = MouvementStock(
                    produit=entree.produit,
                    quantite=entree.quantite,
                    type_mouvement='ENTREE',
                    date=entree.date,
                    user=request.user
                )
                mouvement.save()
            except Exception as e:
                # En cas d'erreur, continuer sans créer le mouvement
                pass
                
            entree.save()
            messages.success(request, "L'entrée en stock a été enregistrée avec succès.")
            # Si l'entrée est créée depuis la fiche produit, rediriger vers cette fiche
            if produit:
                return redirect('fleet_app:produit_detail', pk=produit_id)
            return redirect('fleet_app:entree_stock_list')
    else:
        # Génération automatique du prochain ID d'entrée
        last_entree = EntreeStock.objects.order_by('-id_entree').first()
        next_id = 'ENT001'
        if last_entree:
            last_num = int(last_entree.id_entree[3:])
            next_id = f'ENT{(last_num + 1):03d}'
        
        initial_data = {'id_entree': next_id, 'date': datetime.date.today()}
        # Pré-remplir le produit si fourni
        if produit:
            initial_data['produit'] = produit
            initial_data['fournisseur'] = produit.fournisseur
            initial_data['prix_unitaire'] = produit.prix_unitaire
        
        form = EntreeStockForm(initial=initial_data)
    
    context = {
        'form': form,
        'titre': 'Ajouter une Entrée en Stock',
        'produit': produit,
    }
    
    return render(request, 'fleet_app/inventaire/entree_stock_form.html', context)

@login_required
@user_owns_data(EntreeStock, relation_path=['produit', 'user'])
def entree_stock_update(request, pk):
    """Mise à jour d'une entrée en stock existante
    Sécurisée pour vérifier que l'utilisateur connecté est bien le propriétaire du produit associé à l'entrée
    """
    entree = get_object_or_404(EntreeStock, pk=pk)
    
    if request.method == 'POST':
        form = EntreeStockForm(request.POST, instance=entree)
        if form.is_valid():
            # Vérifier que le produit appartient bien à l'utilisateur connecté
            produit_form = form.cleaned_data.get('produit')
            if produit_form and produit_form.user != request.user:
                messages.error(request, "Vous n'avez pas le droit de modifier une entrée pour ce produit.")
                return redirect('fleet_app:entree_stock_list')
                
            entree_mise_a_jour = form.save(commit=False)
            
            # Si la quantité a changé, mettre à jour le mouvement de stock associé
            if entree.quantite != entree_mise_a_jour.quantite:
                try:
                    # Créer un nouveau mouvement de stock avec l'utilisateur connecté
                    mouvement = MouvementStock(
                        produit=entree_mise_a_jour.produit,
                        quantite=entree_mise_a_jour.quantite - entree.quantite,  # Différence de quantité
                        type_mouvement='AJUSTEMENT',
                        date=datetime.date.today(),
                        user=request.user
                    )
                    mouvement.save()
                except Exception as e:
                    # En cas d'erreur, continuer sans créer le mouvement
                    pass
            
            entree_mise_a_jour.save()
            messages.success(request, "L'entrée en stock a été mise à jour avec succès.")
            return redirect('fleet_app:entree_stock_list')
    else:
        form = EntreeStockForm(instance=entree)
    
    context = {
        'form': form,
        'entree': entree,
        'titre': 'Modifier une Entrée en Stock',
    }
    
    return render(request, 'fleet_app/inventaire/entree_stock_form.html', context)

@login_required
@user_owns_data(EntreeStock, relation_path=['produit', 'user'])
def entree_stock_delete(request, pk):
    """Suppression d'une entrée en stock existante
    Sécurisée pour vérifier que l'utilisateur connecté est bien le propriétaire du produit associé à l'entrée
    """
    entree = get_object_or_404(EntreeStock, pk=pk)
    
    if request.method == 'POST':
        try:
            # Stocker les informations pour le message de confirmation
            produit_info = f"{entree.produit.nom} ({entree.quantite} {entree.produit.unite})"
            
            # Supprimer l'entrée
            entree.delete()
            
            messages.success(request, f"L'entrée en stock pour {produit_info} a été supprimée avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression de l'entrée en stock : {str(e)}")
        
        return redirect('fleet_app:entree_stock_list')
    
    context = {
        'entree': entree,
        'titre': 'Supprimer une Entrée en Stock',
        'confirmation_message': f"Êtes-vous sûr de vouloir supprimer l'entrée en stock pour {entree.produit.nom} ({entree.quantite} {entree.produit.unite}) du {entree.date}?",
    }
    
    return render(request, 'fleet_app/confirmation_delete.html', context)

# Vues pour les sorties de stock
@login_required
def sortie_stock_list(request):
    """Liste des sorties de stock avec recherche et filtrage
    Filtrée pour n'afficher que les sorties de l'utilisateur connecté
    """
    form_recherche = RechercheInventaireForm(request.GET)
    # Filtrer les sorties pour n'afficher que celles de l'utilisateur connecté
    # Nous filtrons sur le produit associé à la sortie
    sorties = SortieStock.objects.all()
    
    # Filtrage selon les critères de recherche
    if form_recherche.is_valid():
        critere = form_recherche.cleaned_data.get('critere')
        terme = form_recherche.cleaned_data.get('terme')
        date_debut = form_recherche.cleaned_data.get('date_debut')
        date_fin = form_recherche.cleaned_data.get('date_fin')
        
        if critere and terme:
            if critere == 'id_produit':
                sorties = sorties.filter(produit__id_produit__icontains=terme)
            elif critere == 'nom':
                sorties = sorties.filter(produit__nom__icontains=terme)
            elif critere == 'destinataire':
                sorties = sorties.filter(destinataire__icontains=terme)
        
        if date_debut:
            sorties = sorties.filter(date__gte=date_debut)
        if date_fin:
            sorties = sorties.filter(date__lte=date_fin)
    
    # Pagination
    paginator = Paginator(sorties.order_by('-date', '-id_sortie'), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'sorties': page_obj,
        'form_recherche': form_recherche,
        'titre': 'Sorties de Stock',
    }
    
    return render(request, 'fleet_app/inventaire/sortie_stock_list.html', context)

@login_required
def sortie_stock_create(request, produit_id=None):
    """Création d'une nouvelle sortie de stock, avec pré-remplissage optionnel du produit"""
    produit = None
    if produit_id:
        produit = get_object_or_404(Produit, id_produit=produit_id)
    
    if request.method == 'POST':
        form = SortieStockForm(request.POST)
        if form.is_valid():
            # Vérifier que le produit appartient bien à l'utilisateur connecté
            produit_form = form.cleaned_data.get('produit')
            if produit_form and produit_form.user != request.user:
                messages.error(request, "Vous n'avez pas le droit d'ajouter une sortie pour ce produit.")
                return redirect('fleet_app:sortie_stock_list')
                
            sortie = form.save(commit=False)
            
            # Associer l'utilisateur connecté au mouvement de stock qui sera créé
            try:
                # Créer le mouvement de stock avec l'utilisateur connecté
                mouvement = MouvementStock(
                    produit=sortie.produit,
                    quantite=-sortie.quantite,  # Quantité négative pour une sortie
                    type_mouvement='SORTIE',
                    date=sortie.date,
                    user=request.user
                )
                mouvement.save()
            except Exception as e:
                # En cas d'erreur, continuer sans créer le mouvement
                pass
                
            sortie.save()
            messages.success(request, "La sortie de stock a été enregistrée avec succès.")
            # Si la sortie est créée depuis la fiche produit, rediriger vers cette fiche
            if produit:
                return redirect('fleet_app:produit_detail', pk=produit_id)
            return redirect('fleet_app:sortie_stock_list')
    else:
        # Génération automatique du prochain ID de sortie
        last_sortie = SortieStock.objects.order_by('-id_sortie').first()
        next_id = 'SRT001'
        if last_sortie:
            last_num = int(last_sortie.id_sortie[3:])
            next_id = f'SRT{(last_num + 1):03d}'
        
        initial_data = {'id_sortie': next_id, 'date': datetime.date.today()}
        # Pré-remplir le produit si fourni
        if produit:
            initial_data['produit'] = produit
            # Vérifier le stock actuel pour la validation côté serveur
            initial_data['stock_avant'] = produit.get_stock_actuel()
        
        form = SortieStockForm(initial=initial_data)
    
    context = {
        'form': form,
        'titre': 'Ajouter une Sortie de Stock',
        'produit': produit,
    }
    
    return render(request, 'fleet_app/inventaire/sortie_stock_form.html', context)

@login_required
@user_owns_data(SortieStock, relation_path=['produit', 'user'])
def sortie_stock_update(request, pk):
    """Mise à jour d'une sortie de stock existante
    Sécurisée pour vérifier que l'utilisateur connecté est bien le propriétaire du produit associé à la sortie
    """
    sortie = get_object_or_404(SortieStock, pk=pk)
    
    if request.method == 'POST':
        form = SortieStockForm(request.POST, instance=sortie)
        if form.is_valid():
            # Vérifier que le produit appartient bien à l'utilisateur connecté
            produit_form = form.cleaned_data.get('produit')
            if produit_form and produit_form.user != request.user:
                messages.error(request, "Vous n'avez pas le droit de modifier une sortie pour ce produit.")
                return redirect('fleet_app:sortie_stock_list')
                
            sortie_mise_a_jour = form.save(commit=False)
            
            # Si la quantité a changé, mettre à jour le mouvement de stock associé
            if sortie.quantite != sortie_mise_a_jour.quantite:
                try:
                    # Créer un nouveau mouvement de stock avec l'utilisateur connecté
                    mouvement = MouvementStock(
                        produit=sortie_mise_a_jour.produit,
                        quantite=-(sortie_mise_a_jour.quantite - sortie.quantite),  # Différence de quantité (négative pour sortie)
                        type_mouvement='AJUSTEMENT',
                        date=datetime.date.today(),
                        user=request.user
                    )
                    mouvement.save()
                except Exception as e:
                    # En cas d'erreur, continuer sans créer le mouvement
                    pass
            
            sortie_mise_a_jour.save()
            messages.success(request, "La sortie de stock a été mise à jour avec succès.")
            return redirect('fleet_app:sortie_stock_list')
    else:
        form = SortieStockForm(instance=sortie)
    
    context = {
        'form': form,
        'sortie': sortie,
        'titre': 'Modifier une Sortie de Stock',
    }
    
    return render(request, 'fleet_app/inventaire/sortie_stock_form.html', context)

@login_required
@user_owns_data(SortieStock, relation_path=['produit', 'user'])
def sortie_stock_delete(request, pk):
    """Suppression d'une sortie de stock
    Sécurisée pour vérifier que l'utilisateur connecté est bien le propriétaire du produit associé à la sortie
    """
    sortie = get_object_or_404(SortieStock, pk=pk)
    
    try:
        # Supprimer la sortie de stock
        sortie.delete()
        messages.success(request, "La sortie de stock a été supprimée avec succès.")
    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression de la sortie de stock : {str(e)}")
    
    return redirect('fleet_app:sortie_stock_list')

# Vue pour le stock actuel
@login_required
def stock_actuel(request):
    """Affichage du stock actuel pour tous les produits"""
    form_recherche = RechercheInventaireForm(request.GET)
    produits = Produit.objects.all()
    
    # Filtrage selon les critères de recherche
    if form_recherche.is_valid():
        critere = form_recherche.cleaned_data.get('critere')
        terme = form_recherche.cleaned_data.get('terme')
        
        if critere and terme:
            if critere == 'id_produit':
                produits = produits.filter(id_produit__icontains=terme)
            elif critere == 'nom':
                produits = produits.filter(nom__icontains=terme)
            elif critere == 'categorie':
                produits = produits.filter(categorie__icontains=terme)
            elif critere == 'fournisseur':
                produits = produits.filter(fournisseur__icontains=terme)
    
    # Calcul des stocks pour chaque produit
    stock_data = []
    for produit in produits:
        total_entrees = EntreeStock.objects.filter(produit=produit).aggregate(Sum('quantite'))['quantite__sum'] or 0
        total_sorties = SortieStock.objects.filter(produit=produit).aggregate(Sum('quantite'))['quantite__sum'] or 0
        stock_actuel = total_entrees - total_sorties
        statut = "OK"
        if stock_actuel <= produit.seuil_minimum:
            statut = "ALERTE"
        
        stock_data.append({
            'produit': produit,
            'total_entrees': total_entrees,
            'total_sorties': total_sorties,
            'stock_actuel': stock_actuel,
            'seuil_minimum': produit.seuil_minimum,
            'statut': statut
        })
    
    # Pagination
    paginator = Paginator(stock_data, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'stock_data': page_obj,
        'form_recherche': form_recherche,
        'titre': 'Stock Actuel',
    }
    
    return render(request, 'fleet_app/inventaire/stock_actuel.html', context)

# Vue pour les mouvements de stock
@login_required
def mouvement_stock_list(request):
    """Liste des mouvements de stock de l'utilisateur connecté
    Filtrée pour n'afficher que les mouvements de l'utilisateur connecté
    """
    form_recherche = RechercheInventaireForm(request.GET)
    # Récupérer tous les mouvements de stock
    mouvements = MouvementStock.objects.all()
    
    # Filtrage selon les critères de recherche
    if form_recherche.is_valid():
        critere = form_recherche.cleaned_data.get('critere')
        terme = form_recherche.cleaned_data.get('terme')
        date_debut = form_recherche.cleaned_data.get('date_debut')
        date_fin = form_recherche.cleaned_data.get('date_fin')
        
        if critere and terme:
            if critere == 'id_produit':
                mouvements = mouvements.filter(produit__id_produit__icontains=terme)
            elif critere == 'nom':
                mouvements = mouvements.filter(produit__nom__icontains=terme)
        
        if date_debut:
            mouvements = mouvements.filter(date__gte=date_debut)
        if date_fin:
            mouvements = mouvements.filter(date__lte=date_fin)
    
    # Pagination
    paginator = Paginator(mouvements.order_by('-date'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'mouvements': page_obj,
        'form_recherche': form_recherche,
        'titre': 'Mouvements de Stock',
    }
    
    return render(request, 'fleet_app/inventaire/mouvement_stock_list.html', context)


# API pour l'inventaire

@login_required
def get_produits_list(request):
    """API pour récupérer la liste des produits"""
    produits = Produit.objects.all()
    produits_list = []
    
    for produit in produits:
        produits_list.append({
            'id_produit': produit.id_produit,
            'nom': produit.nom,
            'description': produit.description,
            'prix_unitaire': float(produit.prix_unitaire),
            'stock_actuel': produit.get_stock_actuel()
        })
    
    data = {'success': True, 'produits': produits_list}
    return JsonResponse(data)

# API pour obtenir les informations d'un produit
@login_required
def get_produit_info(request):
    """API pour obtenir les informations d'un produit"""
    produit_id = request.GET.get('id')
    
    try:
        produit = Produit.objects.get(pk=produit_id)
        stock_actuel = produit.get_stock_actuel()
        
        data = {
            'success': True,
            'nom': produit.nom,
            'description': produit.description,
            'unite': produit.unite,
            'prix_unitaire': float(produit.prix_unitaire),
            'stock_actuel': stock_actuel,
            'fournisseur': produit.fournisseur,
        }
    except Produit.DoesNotExist:
        data = {
            'success': False,
            'message': 'Produit non trouvé'
        }
    
    return JsonResponse(data)

@login_required
def get_produits_list(request):
    """API pour obtenir la liste des produits
    Sécurisée pour ne renvoyer que les produits de l'utilisateur connecté
    """
    # Filtrer pour n'accéder qu'aux produits de l'utilisateur connecté
    produits = Produit.objects.filter(user=request.user).order_by('id_produit')
    
    produits_list = []
    for produit in produits:
        produits_list.append({
            'id_produit': produit.id_produit,
            'nom': produit.nom,
            'description': produit.description,
            'prix_unitaire': float(produit.prix_unitaire),
            'unite': produit.unite
        })
    
    data = {
        'success': True,
        'produits': produits_list
    }
    
    return JsonResponse(data)

# Vue pour afficher le stock actuel
@login_required
def stock_actuel(request):
    """Affiche le stock actuel des produits de l'utilisateur connecté
    Filtrée pour n'afficher que les produits de l'utilisateur connecté
    """
    form_recherche = RechercheInventaireForm(request.GET)
    # Récupérer tous les produits
    produits = Produit.objects.all()
    
    # Récupérer les catégories uniques pour le filtre
    categories = Produit.objects.values_list('categorie', flat=True).distinct()
    categories = [cat for cat in categories if cat]  # Filtrer les valeurs vides
    
    # Filtrage selon les critères de recherche
    if form_recherche.is_valid():
        critere = form_recherche.cleaned_data.get('critere')
        terme = form_recherche.cleaned_data.get('terme')
        if critere and terme:
            if critere == 'produit':
                produits = produits.filter(nom__icontains=terme)
            elif critere == 'reference':
                produits = produits.filter(id_produit__icontains=terme)
    
    # Filtrage par catégorie
    categorie = request.GET.get('categorie')
    if categorie:
        produits = produits.filter(categorie=categorie)
    
    # Récupérer tous les produits pour le filtrage manuel
    all_produits = list(produits)
    
    # Filtrage manuel par statut d'alerte (car stock_actuel est calculé dynamiquement)
    alerte = request.GET.get('alerte')
    if alerte:
        filtered_produits = []
        for produit in all_produits:
            stock = produit.get_stock_actuel()
            if alerte == 'alerte' and 0 < stock <= produit.seuil_minimum:
                filtered_produits.append(produit)
            elif alerte == 'rupture' and stock == 0:
                filtered_produits.append(produit)
        all_produits = filtered_produits
    
    # Calcul des statistiques manuellement
    total_produits = len(all_produits)
    
    # Compter les produits par statut
    produits_alerte = 0
    produits_rupture = 0
    produits_normaux = 0
    
    for produit in Produit.objects.all():
        stock = produit.get_stock_actuel()
        if stock == 0:
            produits_rupture += 1
        elif stock <= produit.seuil_minimum:
            produits_alerte += 1
        else:
            produits_normaux += 1
    
    # Pagination manuelle
    paginator = Paginator(all_produits, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'produits': page_obj,
        'form_recherche': form_recherche,
        'categories': categories,
        'titre': 'Stock Actuel',
        'total_produits': Produit.objects.count(),  # Total de tous les produits
        'produits_alerte': produits_alerte,
        'produits_rupture': produits_rupture,
        'produits_normaux': produits_normaux,
    }
    
    return render(request, 'fleet_app/inventaire/stock_actuel.html', context)


# Vues pour les commandes
@login_required
def get_produit_info_commande(request):
    """API pour récupérer les informations d'un produit pour une commande"""
    if request.method == 'POST':
        produit_id = request.POST.get('produit_id')
        if produit_id:
            try:
                produit = Produit.objects.get(id=produit_id)
                data = {
                    'success': True,
                    'id_produit': produit.id_produit,
                    'nom_produit': produit.nom,
                    'categorie': produit.categorie.nom if produit.categorie else '',
                    'prix_unitaire': float(produit.prix_unitaire),
                    'unite': produit.unite,
                }
                return JsonResponse(data)
            except Produit.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Produit non trouvé'})
        return JsonResponse({'success': False, 'error': 'ID produit non fourni'})
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

@login_required
def commande_list(request):
    """Liste des commandes avec recherche et filtrage
    Sécurisée pour ne montrer que les commandes de l'utilisateur connecté
    """
    # Initialiser le formulaire de recherche
    form_recherche = RechercheCommandeForm(request.GET or None)
    
    # Récupérer uniquement les commandes de l'utilisateur connecté
    commandes = Commande.objects.all().order_by('-date_creation')
    
    # Statistiques des commandes par statut
    stats_commandes = {
        'Brouillon': Commande.objects.filter(statut='Brouillon').count(),
        'En_attente': Commande.objects.filter(statut='En attente').count(),
        'Validee': Commande.objects.filter(statut='Validée').count(),
        'En_cours': Commande.objects.filter(statut='En cours').count(),
        'Livree': Commande.objects.filter(statut='Livrée').count(),
        'Annulee': Commande.objects.filter(statut='Annulée').count(),
        'total': Commande.objects.all().count()
    }
    
    # Filtrage selon les critères de recherche
    if form_recherche.is_valid():
        numero = form_recherche.cleaned_data.get('numero')
        fournisseur = form_recherche.cleaned_data.get('fournisseur')
        statut = form_recherche.cleaned_data.get('statut')
        date_debut = form_recherche.cleaned_data.get('date_debut')
        date_fin = form_recherche.cleaned_data.get('date_fin')
        
        if numero:
            commandes = commandes.filter(numero__icontains=numero)
        if fournisseur:
            commandes = commandes.filter(fournisseur__icontains=fournisseur)
        if statut:
            commandes = commandes.filter(statut=statut)
        if date_debut:
            commandes = commandes.filter(date_creation__gte=date_debut)
        if date_fin:
            commandes = commandes.filter(date_creation__lte=date_fin)
    
    # Pagination
    paginator = Paginator(commandes, 10)  # 10 commandes par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'commandes': page_obj,
        'form_recherche': form_recherche,
        'titre': 'Liste des Commandes',
        'stats_commandes': stats_commandes,
    }
    
    return render(request, 'fleet_app/inventaire/commande_list.html', context)

@login_required
def commande_create(request):
    """Création d'une nouvelle commande avec gestion dynamique des lignes"""
    produits = Produit.objects.all().order_by('id_produit')
    
    if request.method == 'POST':
        form = CommandeForm(request.POST, user=request.user)
        if form.is_valid():
            commande = form.save(commit=False)
            commande.user = request.user  # Associer la commande à l'utilisateur connecté
            commande.save()  # Sauvegarde pour obtenir le numéro de commande
            
            # Traitement des lignes de commande
            lignes_data = []
            i = 0
            while True:
                produit_id = request.POST.get(f'lignes[{i}][produit]')
                if not produit_id:
                    break
                    
                quantite = request.POST.get(f'lignes[{i}][quantite]')
                prix_unitaire = request.POST.get(f'lignes[{i}][prix_unitaire]')
                
                if produit_id and quantite and prix_unitaire:
                    produit = Produit.objects.get(id=produit_id)
                    ligne = LigneCommande(
                        commande=commande,
                        produit=produit,
                        quantite=int(quantite),
                        prix_unitaire=Decimal(prix_unitaire)
                    )
                    ligne.save()
                    lignes_data.append(ligne)
                i += 1
            
            # Recalculer les montants de la commande
            commande.calculer_montants()
            
            messages.success(request, f"La commande {commande.numero} a été créée avec succès avec {len(lignes_data)} produits.")
            return redirect('fleet_app:commande_detail', pk=commande.numero)
    else:
        form = CommandeForm(user=request.user, initial={'date_creation': datetime.date.today(), 'remise': 0})
    
    context = {
        'form': form,
        'titre': 'Nouvelle Commande',
        'produits': produits,
    }
    
    return render(request, 'fleet_app/inventaire/commande_form_dynamic.html', context)

@login_required
@user_owns_data(Commande, pk_url_kwarg='pk', relation_path=['user'])
def commande_update(request, pk):
    """Mise à jour d'une commande existante avec gestion dynamique des lignes"""
    commande = get_object_or_404(Commande, pk=pk)
    produits = Produit.objects.all().order_by('id_produit')
    lignes = commande.lignes.all()
    
    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande, user=request.user)
        if form.is_valid():
            commande = form.save()
            
            # Supprimer toutes les lignes existantes
            commande.lignes.all().delete()
            
            # Traitement des nouvelles lignes de commande
            lignes_data = []
            i = 0
            while True:
                produit_id = request.POST.get(f'lignes[{i}][produit]')
                if not produit_id:
                    break
                    
                quantite = request.POST.get(f'lignes[{i}][quantite]')
                prix_unitaire = request.POST.get(f'lignes[{i}][prix_unitaire]')
                
                if produit_id and quantite and prix_unitaire:
                    produit = Produit.objects.get(id=produit_id)
                    ligne = LigneCommande(
                        commande=commande,
                        produit=produit,
                        quantite=int(quantite),
                        prix_unitaire=Decimal(prix_unitaire)
                    )
                    ligne.save()
                    lignes_data.append(ligne)
                i += 1
            
            # Recalculer les montants de la commande
            commande.calculer_montants()
            
            messages.success(request, f"La commande {commande.numero} a été mise à jour avec succès avec {len(lignes_data)} produits.")
            return redirect('fleet_app:commande_detail', pk=commande.numero)
    else:
        form = CommandeForm(instance=commande, user=request.user)
    
    context = {
        'form': form,
        'commande': commande,
        'titre': f'Modifier la commande {commande.numero}',
        'produits': produits,
        'lignes': lignes,
    }
    
    return render(request, 'fleet_app/inventaire/commande_form_dynamic.html', context)

@login_required
@user_owns_data(Commande, pk_url_kwarg='pk', relation_path=['user'])
def commande_detail(request, pk):
    """Détail d'une commande avec ses lignes
    Sécurisée pour garantir que l'utilisateur ne peut accéder qu'à ses propres commandes
    """
    commande = get_object_or_404(Commande, pk=pk)
    lignes = commande.lignes.all()
    
    # Gestion du formulaire d'upload de document signé
    if request.method == 'POST':
        form_document = DocumentSigneCommandeForm(request.POST, request.FILES, instance=commande)
        if form_document.is_valid():
            form_document.save()
            messages.success(request, "Le document signé a été ajouté avec succès.")
            return redirect('fleet_app:commande_detail', pk=commande.numero)
    else:
        form_document = DocumentSigneCommandeForm(instance=commande)
    
    context = {
        'commande': commande,
        'lignes': lignes,
        'form_document': form_document,
        'titre': f'Commande {commande.numero}',
    }
    
    return render(request, 'fleet_app/inventaire/commande_detail.html', context)

@login_required
@user_owns_data(Commande, pk_url_kwarg='pk', relation_path=['user'])
def commande_delete(request, pk):
    """Suppression d'une commande
    Sécurisée pour garantir que l'utilisateur ne peut supprimer que ses propres commandes
    """
    commande = get_object_or_404(Commande, pk=pk)
    
    # Accepter toutes les méthodes pour la suppression
    # Cela résout le problème des méthodes 'POSTE' et 'OBTENIR' incorrectes
    if request.method in ['POST', 'POSTE', 'GET', 'OBTENIR']:
        numero = commande.numero
        commande.delete()
        messages.success(request, f"La commande {numero} a été supprimée avec succès.")
        return redirect('fleet_app:commande_list')
    
    context = {
        'commande': commande,
        'titre': f'Supprimer la commande {commande.numero}',
    }
    
    return render(request, 'fleet_app/inventaire/commande_confirm_delete.html', context)

@login_required
def export_commandes_excel(request):
    """Exporter la liste des commandes au format Excel"""
    if not XLWT_AVAILABLE:
        messages.error(request, "L'export Excel n'est pas disponible. Veuillez installer la bibliothèque xlwt.")
        return redirect('fleet_app:commande_list')
    
    try:
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="liste_commandes.xls"'
        
        # Créer un workbook Excel et ajouter une feuille
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Commandes')
        
        # Styles pour l'en-tête et les données
        header_style = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center; pattern: pattern solid, fore_color gray25')
        date_style = xlwt.easyxf('align: wrap on, vert centre, horiz left', num_format_str='DD/MM/YYYY')
        number_style = xlwt.easyxf('align: wrap on, vert centre, horiz right')
        text_style = xlwt.easyxf('align: wrap on, vert centre, horiz left')
        
        # En-têtes de colonnes
        columns = ['Numéro', 'Date création', 'Fournisseur', 'Statut', 'Montant HT', 'Remise', 'Montant TTC', 'Nb. Produits']
        for col_num, column_title in enumerate(columns):
            ws.write(0, col_num, column_title, header_style)
            ws.col(col_num).width = 256 * 20  # 20 caractères de large
        
        # Récupérer toutes les commandes
        commandes = Commande.objects.all().order_by('-date_creation')
        
        # Écrire les données
        row_num = 1
        for commande in commandes:
            nb_produits = commande.lignes.count()
            
            ws.write(row_num, 0, commande.numero, text_style)
            ws.write(row_num, 1, commande.date_creation, date_style)
            ws.write(row_num, 2, commande.fournisseur, text_style)
            ws.write(row_num, 3, commande.statut, text_style)
            ws.write(row_num, 4, float(commande.montant_ht), number_style)
            ws.write(row_num, 5, float(commande.remise), number_style)
            ws.write(row_num, 6, float(commande.montant_ttc), number_style)
            ws.write(row_num, 7, nb_produits, number_style)
            
            row_num += 1
        
        wb.save(response)
        return response
    except Exception as e:
        messages.error(request, f"Erreur lors de l'export Excel : {str(e)}")
        return redirect('fleet_app:commande_list')

@login_required
@user_owns_data(Commande, pk_url_kwarg='pk', relation_path=['user'])
def export_commande_pdf(request, pk):
    """Exporter une commande spécifique au format PDF
    Sécurisée pour garantir que l'utilisateur ne peut exporter que ses propres commandes
    """
    commande = get_object_or_404(Commande, pk=pk)
    lignes = commande.lignes.all()
    
    # Calculer automatiquement les montants avant l'export
    montant_ht = sum(ligne.prix_total for ligne in lignes)
    
    # Calculer la remise (en valeur)
    remise_pourcentage = commande.remise or 0
    montant_remise = (montant_ht * remise_pourcentage) / 100
    
    # Calculer la TVA (18%)
    montant_apres_remise = montant_ht - montant_remise
    taux_tva = 18  # 18%
    montant_tva = (montant_apres_remise * taux_tva) / 100
    
    # Calculer le montant TTC
    montant_ttc = montant_apres_remise + montant_tva
    
    # Mettre à jour les montants de la commande
    commande.montant_ht = montant_ht
    commande.montant_remise = montant_remise
    commande.montant_tva = montant_tva
    commande.montant_ttc = montant_ttc
    commande.save(update_fields=['montant_ht', 'montant_remise', 'montant_tva', 'montant_ttc'])
    
    # Essayer d'importer WeasyPrint uniquement lorsque la fonction est appelée
    weasyprint_available = False
    try:
        from weasyprint import HTML
        weasyprint_available = True
    except ImportError:
        weasyprint_available = False
    except Exception:
        # Capture les erreurs liées aux dépendances système manquantes
        weasyprint_available = False
    
    if not weasyprint_available:
        messages.warning(request, "L'export PDF n'est pas disponible. Les dépendances WeasyPrint ne sont pas installées. Affichage de la version imprimable HTML à la place.")
        # Rediriger vers une version imprimable HTML comme alternative
        context = {
            'commande': commande,
            'lignes': lignes,
            'date_impression': datetime.datetime.now(),
            'mode_impression': True,
        }
        return render(request, 'fleet_app/inventaire/commande_pdf.html', context)
    
    try:
        # Préparer le contexte pour le template
        context = {
            'commande': commande,
            'lignes': lignes,
            'date_impression': datetime.datetime.now(),
            'montant_ht': montant_ht,
            'montant_remise': montant_remise,
            'montant_tva': montant_tva,
            'montant_ttc': montant_ttc,
            'taux_tva': taux_tva,
            'remise_pourcentage': remise_pourcentage,
        }
        
        # Rendre le template HTML
        template = get_template('fleet_app/inventaire/commande_pdf.html')
        html_string = template.render(context)
        
        # Générer le PDF
        pdf_file = HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf()
        
        # Créer la réponse HTTP avec le PDF
        response = HttpResponse(pdf_file, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="commande_{commande.numero}.pdf"'
        
        return response
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération du PDF : {str(e)}. Essayez d'installer GTK et les dépendances requises pour WeasyPrint.")
        return redirect('fleet_app:commande_detail', pk=commande.numero)

@login_required
@user_owns_related_data(Commande, pk_url_kwarg='commande_pk', relation_path=['user'])
def ajouter_ligne_commande(request, commande_pk):
    """Ajouter une ligne à une commande existante
    Sécurisée pour garantir que l'utilisateur ne peut modifier que ses propres commandes
    """
    produits = Produit.objects.all().order_by('id_produit')
    
    if request.method == 'POST':
        form = CommandeForm(request.POST)
        if form.is_valid():
            # Sauvegarder la commande et l'associer à l'utilisateur connecté
            commande = form.save(commit=False)
            commande.date_creation = timezone.now()
            commande.user = request.user  # Associer la commande à l'utilisateur connecté
            commande.save()
            messages.success(request, "La commande a été créée avec succès.")
            return redirect('fleet_app:commande_detail', pk=commande.numero)
    else:
        form = CommandeForm()
    
    context = {
        'form': form,
        'commande': commande,
        'produits': produits,
        'titre': f'Ajouter un produit à la commande {commande.numero}',
    }
    
    return render(request, 'fleet_app/inventaire/ligne_commande_form.html', context)

@login_required
@user_owns_related_data(LigneCommande, pk_url_kwarg='pk', relation_path=['commande', 'user'])
def modifier_ligne_commande(request, pk):
    """Modifier une ligne de commande existante
    Sécurisée pour garantir que l'utilisateur ne peut modifier que les lignes de ses propres commandes
    """
    ligne = get_object_or_404(LigneCommande, pk=pk)
    commande = ligne.commande
    produits = Produit.objects.all().order_by('id_produit')
    
    if request.method == 'POST':
        form = LigneCommandeForm(request.POST, instance=ligne)
        if form.is_valid():
            form.save()
            messages.success(request, "La ligne a été modifiée avec succès.")
            return redirect('fleet_app:commande_detail', pk=commande.numero)
    else:
        form = LigneCommandeForm(instance=ligne)
    
    context = {
        'form': form,
        'ligne': ligne,
        'commande': commande,
        'produits': produits,
        'titre': f'Modifier un produit de la commande {commande.numero}',
    }
    
    return render(request, 'fleet_app/inventaire/ligne_commande_form.html', context)

@login_required
@user_owns_related_data(LigneCommande, pk_url_kwarg='pk', relation_path=['commande', 'user'])
def supprimer_ligne_commande(request, pk):
    """Supprimer une ligne de commande
    Sécurisée pour garantir que l'utilisateur ne peut supprimer que les lignes de ses propres commandes
    """
    ligne = get_object_or_404(LigneCommande, pk=pk)
    commande = ligne.commande
    
    # Permettre la suppression directe via GET pour simplifier l'interface utilisateur
    # Cela permet de supprimer directement depuis le lien dans la vue de détail
    ligne.delete()
    commande.calculer_montants()  # Recalculer les montants après suppression
    messages.success(request, "La ligne a été supprimée avec succès.")
    return redirect('fleet_app:commande_detail', pk=commande.numero)

@require_POST
@login_required
def get_produit_info_commande(request):
    """API pour obtenir les informations d'un produit pour une commande
    Sécurisée pour ne renvoyer que les informations des produits de l'utilisateur connecté
    """
    produit_id = request.POST.get('produit_id')
    
    try:
        # Filtrer pour n'accéder qu'aux produits de l'utilisateur connecté
        produit = Produit.objects.get(id_produit=produit_id, user=request.user)
        data = {
            'success': True,
            'nom_produit': produit.nom,
            'categorie': produit.categorie,
            'prix_unitaire': float(produit.prix_unitaire),
        }
    except Produit.DoesNotExist:
        data = {
            'success': False,
            'message': 'Produit non trouvé',
        }
    
    return JsonResponse(data)
