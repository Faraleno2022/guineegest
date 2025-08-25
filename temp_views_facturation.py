from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
import json
from decimal import Decimal

from .models_inventaire import Facture, LigneFacture, Produit
from .forms_inventaire import FactureForm, LigneFactureForm, RechercheFactureForm

# Vues pour les factures
@login_required
def facture_list(request):
    """Liste des factures avec recherche et filtrage"""
    form_recherche = RechercheFactureForm(request.GET)
    factures = Facture.objects.all()
    
    # Filtrage selon les critères de recherche
    if form_recherche.is_valid():
        numero = form_recherche.cleaned_data.get('numero')
        tiers = form_recherche.cleaned_data.get('tiers')
        type_facture = form_recherche.cleaned_data.get('type_facture')
        statut = form_recherche.cleaned_data.get('statut')
        date_debut = form_recherche.cleaned_data.get('date_debut')
        date_fin = form_recherche.cleaned_data.get('date_fin')
        
        if numero:
            factures = factures.filter(numero__icontains=numero)
        if tiers:
            factures = factures.filter(tiers_nom__icontains=tiers)
        if type_facture:
            factures = factures.filter(type_facture=type_facture)
        if statut:
            factures = factures.filter(statut=statut)
        if date_debut:
            factures = factures.filter(date_emission__gte=date_debut)
        if date_fin:
            factures = factures.filter(date_emission__lte=date_fin)
    
    # Pagination
    paginator = Paginator(factures.order_by('-date_emission'), 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_factures = factures.count()
    total_montant = sum(facture.montant_ttc for facture in factures)
    factures_non_payees = factures.filter(statut__in=['Brouillon', 'Émise']).count()
    montant_non_paye = sum(facture.montant_ttc for facture in factures.filter(statut__in=['Brouillon', 'Émise']))
    
    context = {
        'factures': page_obj,
        'form_recherche': form_recherche,
        'titre': 'Liste des factures',
        'total_factures': total_factures,
        'total_montant': total_montant,
        'factures_non_payees': factures_non_payees,
        'montant_non_paye': montant_non_paye,
    }
    return render(request, 'fleet_app/inventaire/facture_list.html', context)

@login_required
def facture_create(request):
    """Création d'une nouvelle facture"""
    type_facture = request.GET.get('type', 'Vente')
    
    # Générer le prochain numéro de facture
    annee_courante = timezone.now().year
    dernieres_factures = Facture.objects.filter(numero__startswith=f'FG-{annee_courante}').order_by('-numero')
    
    if dernieres_factures.exists():
        derniere_facture = dernieres_factures.first()
        try:
            dernier_numero = int(derniere_facture.numero.split('-')[-1])
            next_numero = f"{dernier_numero + 1:03d}"
        except (ValueError, IndexError):
            next_numero = "001"
    else:
        next_numero = "001"
    
    # Récupérer tous les produits pour le formulaire
    produits = Produit.objects.all().order_by('nom')
    
    if request.method == 'POST':
        form = FactureForm(request.POST)
        if form.is_valid():
            facture = form.save(commit=False)
            facture.utilisateur = request.user
            
            # Le numéro de facture sera généré automatiquement par le modèle
            
            # Récupérer les champs supplémentaires du formulaire
            facture.tiers_nom = request.POST.get('tiers_nom', '')
            facture.tiers_adresse = request.POST.get('tiers_adresse', '')
            facture.tiers_telephone = request.POST.get('tiers_telephone', '')
            facture.tiers_email = request.POST.get('tiers_email', '')
            facture.mode_paiement = request.POST.get('mode_paiement', '')
            facture.conditions_paiement = request.POST.get('conditions_paiement', '')
            facture.notes = request.POST.get('notes', '')
            
            # Sauvegarder la facture
            facture.save()
            
            # Traitement des lignes de facture depuis le JSON
            lignes_json = request.POST.get('lignes_json', '[]')
            try:
                lignes_data = json.loads(lignes_json)
                for ligne_data in lignes_data:
                    produit_id = ligne_data.get('id')
                    produit = None
                    if produit_id:
                        try:
                            # Utiliser id_produit au lieu de id
                            produit = Produit.objects.get(id_produit=produit_id)
                        except Produit.DoesNotExist:
                            pass
                    
                    LigneFacture.objects.create(
                        facture=facture,
                        produit=produit,
                        description=ligne_data.get('nom', ''),
                        quantite=int(ligne_data.get('quantite', 0)),
                        prix_unitaire=Decimal(ligne_data.get('prix_unitaire', 0)),
                        montant_ht=Decimal(ligne_data.get('total', 0))
                    )
                
                # Mise à jour des montants de la facture
                facture.calculer_montants()
                facture.save()
                
                # Ajouter un message de succès
                total_produits = len(lignes_data)
                montant_total = facture.montant_ttc
                messages.success(request, f'Facture {facture.numero} créée avec succès. {total_produits} produit(s) ajouté(s) pour un montant total de {montant_total:,.0f} GNF.')
                
                # Rediriger vers la liste des factures
                return redirect('fleet_app:facture_list')
                
            except json.JSONDecodeError:
                messages.error(request, 'Erreur lors du traitement des lignes de facture.')
    else:
        form = FactureForm(initial={'type_facture': type_facture})
    
    context = {
        'form': form,
        'titre': f'Nouvelle facture de {type_facture.lower()}',
        'type_facture': type_facture,
        'mode': 'creation',
        'produits': produits,
        'next_numero': next_numero,
    }
    return render(request, 'fleet_app/inventaire/facture_form_dynamic.html', context)

@login_required
def facture_detail(request, numero):
    """Affichage des détails d'une facture"""
    facture = get_object_or_404(Facture, numero=numero)
    lignes = facture.lignes.all()
    
    context = {
        'facture': facture,
        'lignes': lignes,
        'titre': f'Détails de la facture {facture.numero}',
    }
    
    return render(request, 'fleet_app/inventaire/facture_detail.html', context)


@login_required
def facture_edit(request, numero):
    """Modification d'une facture existante"""
    facture = get_object_or_404(Facture, numero=numero)
    
    # Vérifier si la facture peut être modifiée
    if facture.statut in ['Payée', 'Annulée']:
        messages.error(request, f"La facture {facture.numero} ne peut pas être modifiée car elle est {facture.statut.lower()}.")
        return redirect('fleet_app:facture_detail', numero=facture.numero)
    
    # Récupérer tous les produits pour le formulaire
    produits = Produit.objects.all().order_by('nom')
    
    # Récupérer les lignes de facture existantes pour les afficher dans le formulaire
    lignes = facture.lignes.all()
    lignes_json = []
    for ligne in lignes:
        lignes_json.append({
            'id': ligne.produit.id_produit if ligne.produit else None,
            'nom': ligne.description,
            'categorie': ligne.produit.categorie if ligne.produit else '',
            'quantite': ligne.quantite,
            'prix_unitaire': float(ligne.prix_unitaire),
            'total': float(ligne.montant_ht)
        })
    
    if request.method == 'POST':
        form = FactureForm(request.POST, instance=facture)
        if form.is_valid():
            facture = form.save(commit=False)
            
            # Récupérer les champs supplémentaires du formulaire
            facture.tiers_nom = request.POST.get('tiers_nom', '')
            facture.tiers_adresse = request.POST.get('tiers_adresse', '')
            facture.tiers_telephone = request.POST.get('tiers_telephone', '')
            facture.tiers_email = request.POST.get('tiers_email', '')
            facture.mode_paiement = request.POST.get('mode_paiement', '')
            facture.conditions_paiement = request.POST.get('conditions_paiement', '')
            facture.notes = request.POST.get('notes', '')
            
            # Sauvegarder la facture
            facture.save()
            
            # Traitement des lignes de facture depuis le JSON
            lignes_json = request.POST.get('lignes_json', '[]')
            try:
                # Supprimer les lignes existantes
                facture.lignes.all().delete()
                
                # Ajouter les nouvelles lignes
                lignes_data = json.loads(lignes_json)
                for ligne_data in lignes_data:
                    produit_id = ligne_data.get('id')
                    produit = None
                    if produit_id:
                        try:
                            # Utiliser id_produit au lieu de id
                            produit = Produit.objects.get(id_produit=produit_id)
                        except Produit.DoesNotExist:
                            pass
                    
                    LigneFacture.objects.create(
                        facture=facture,
                        produit=produit,
                        description=ligne_data.get('nom', ''),
                        quantite=int(ligne_data.get('quantite', 0)),
                        prix_unitaire=Decimal(ligne_data.get('prix_unitaire', 0)),
                        montant_ht=Decimal(ligne_data.get('total', 0))
                    )
                
                # Mise à jour des montants de la facture
                facture.calculer_montants()
                facture.save()
                
                # Ajouter un message de succès
                messages.success(request, f'Facture {facture.numero} modifiée avec succès.')
                return redirect('fleet_app:facture_list')
            except json.JSONDecodeError:
                messages.error(request, 'Erreur lors du traitement des lignes de facture.')
    else:
        form = FactureForm(instance=facture)
    
    context = {
        'form': form,
        'facture': facture,
        'titre': f'Modification de la facture {facture.numero}',
        'type_facture': facture.type_facture,
        'mode': 'edition',
        'produits': produits,
        'lignes_json': json.dumps(lignes_json),
    }
    return render(request, 'fleet_app/inventaire/facture_form_dynamic.html', context)

@login_required
def facture_delete(request, numero):
    """Suppression d'une facture"""
    facture = get_object_or_404(Facture, numero=numero)
    
    if request.method == 'POST':
        facture.delete()
        messages.success(request, f'La facture {numero} a été supprimée avec succès.')
        return redirect('fleet_app:facture_list')
    
    context = {
        'facture': facture,
        'titre': f'Suppression de la facture {facture.numero}',
    }
    return render(request, 'fleet_app/inventaire/facture_confirm_delete.html', context)
