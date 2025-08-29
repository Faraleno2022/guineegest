from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, F, Value, CharField
from django.db.models.functions import Coalesce
from django.contrib import messages
from .security import user_owns_data, user_owns_related_data
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.template.loader import get_template
from decimal import Decimal

from .models_inventaire import Produit
from .models_facturation import Facture, LigneFacture
from .forms_inventaire import FactureForm, LigneFactureForm, RechercheFactureForm, DocumentSigneForm

import datetime
import csv
import io
# Rendre xhtml2pdf (pisa) optionnel
try:
    from xhtml2pdf import pisa
    PISA_AVAILABLE = True
except ImportError:
    PISA_AVAILABLE = False

# Rendre xlwt optionnel
try:
    import xlwt
    XLWT_AVAILABLE = True
except ImportError:
    XLWT_AVAILABLE = False

# Définition des variables de disponibilité pour WeasyPrint
# On ne tente pas d'importer WeasyPrint au démarrage pour éviter les erreurs
WEASYPRINT_AVAILABLE = False

# Vues pour les factures
@login_required
def facture_list(request):
    """Liste des factures avec recherche et filtrage
    Filtrée pour n'afficher que les factures de l'utilisateur connecté
    """
    form_recherche = RechercheFactureForm(request.GET)
    
    # Filtrer les factures pour n'afficher que celles de l'utilisateur connecté
    factures = Facture.objects.filter(utilisateur=request.user)
    
    # Filtrage selon les critères de recherche
    if form_recherche.is_valid():
        numero = form_recherche.cleaned_data.get('numero')
        tiers = form_recherche.cleaned_data.get('tiers')
        statut = form_recherche.cleaned_data.get('statut')
        date_debut = form_recherche.cleaned_data.get('date_debut')
        date_fin = form_recherche.cleaned_data.get('date_fin')
        
        if numero:
            factures = factures.filter(numero__icontains=numero)
        if tiers:
            factures = factures.filter(tiers_nom__icontains=tiers)
        if statut:
            factures = factures.filter(statut=statut)
        if date_debut:
            factures = factures.filter(date_emission__gte=date_debut)
        if date_fin:
            factures = factures.filter(date_emission__lte=date_fin)
    
    # Récupérer toutes les factures avec leurs lignes associées pour calculer les montants
    factures = factures.prefetch_related('lignes')
    
    # Calculer les montants pour chaque facture et les sauvegarder
    for facture in factures:
        # Utiliser la méthode calculer_montants pour garantir la cohérence des calculs
        facture.calculer_montants()
    
    # Pagination
    paginator = Paginator(factures.order_by('-date_emission'), 10)  # 10 factures par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'factures': page_obj,
        'form_recherche': form_recherche,
        'titre': 'Liste des Factures',
    }
    
    return render(request, 'fleet_app/inventaire/facture_list.html', context)

@login_required
def facture_create(request):
    """Création d'une nouvelle facture avec gestion dynamique des lignes"""
    if request.method == 'POST':
        form = FactureForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                facture = form.save()
                messages.success(request, f"La facture {facture.numero} a été créée avec succès.")
                return redirect('fleet_app:facture_detail', pk=facture.numero)
            except Exception as e:
                messages.error(request, f"Erreur lors de la création de la facture: {str(e)}")
    else:
        # Initialiser le formulaire avec des valeurs par défaut
        form = FactureForm(user=request.user, initial={'tiers_nom': 'Client'})
    
    context = {
        'form': form,
        'titre': 'Nouvelle Facture',
    }
    
    return render(request, 'fleet_app/inventaire/facture_form.html', context)

@login_required
@user_owns_data(Facture, pk_url_kwarg='pk', relation_path=['utilisateur'])
def facture_update(request, pk):
    """Mise à jour d'une facture existante
    Sécurisée pour garantir que l'utilisateur ne peut modifier que ses propres factures
    """
    facture = get_object_or_404(Facture, numero=pk)
    
    if request.method == 'POST':
        form = FactureForm(request.POST, instance=facture, user=request.user)
        if form.is_valid():
            facture = form.save()
            messages.success(request, f"La facture {facture.numero} a été mise à jour avec succès.")
            return redirect('fleet_app:facture_detail', facture.numero)
    else:
        form = FactureForm(instance=facture, user=request.user)
    
    context = {
        'form': form,
        'facture': facture,
        'titre': f'Modifier la Facture {facture.numero}',
    }
    
    return render(request, 'fleet_app/inventaire/facture_form.html', context)

@login_required
@user_owns_data(Facture, pk_url_kwarg='pk', relation_path=['utilisateur'])
def facture_detail(request, pk):
    """Détail d'une facture avec ses lignes
    Sécurisée pour garantir que l'utilisateur ne peut accéder qu'à ses propres factures
    """
    facture = get_object_or_404(Facture, numero=pk)
    
    # Recalculer les montants de la facture à partir des lignes
    facture.calculer_montants()
    
    # Gérer l'upload du document signé
    if request.method == 'POST':
        form_document = DocumentSigneForm(request.POST, request.FILES, instance=facture)
        if form_document.is_valid():
            form_document.save()
            messages.success(request, "Le document signé a été joint à la facture avec succès.")
            return redirect('fleet_app:facture_detail', facture.numero)
    else:
        form_document = DocumentSigneForm(instance=facture)
    
    lignes = facture.lignes.all()
    
    context = {
        'facture': facture,
        'lignes': lignes,
        'form_document': form_document,
        'titre': f'Détail de la Facture {facture.numero}',
    }
    
    return render(request, 'fleet_app/inventaire/facture_detail.html', context)

@login_required
@user_owns_data(Facture, pk_url_kwarg='pk', relation_path=['utilisateur'])
def facture_delete(request, pk):
    """Suppression d'une facture
    Sécurisée pour garantir que l'utilisateur ne peut supprimer que ses propres factures
    """
    facture = get_object_or_404(Facture, numero=pk)
    
    if request.method == 'POST':
        try:
            facture.delete()
            messages.success(request, f"La facture {facture.numero} a été supprimée avec succès.")
            return redirect('fleet_app:facture_list')
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression de la facture: {str(e)}")
            return redirect('fleet_app:facture_detail', facture.numero)
    
    context = {
        'facture': facture,
        'titre': f'Supprimer la Facture {facture.numero}',
    }
    
    return render(request, 'fleet_app/inventaire/facture_confirm_delete.html', context)

@login_required
def export_factures_excel(request):
    """Exporter la liste des factures au format Excel"""
    if not XLWT_AVAILABLE:
        messages.error(request, "Le module xlwt n'est pas installé. Impossible d'exporter en Excel.")
        return redirect('fleet_app:facture_list')
    
    try:
        # Filtrer les factures pour n'exporter que celles de l'utilisateur connecté
        factures = Facture.objects.filter(utilisateur=request.user).order_by('-date_emission')
        
        # Créer un classeur Excel
        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Factures')
        
        # Styles pour Excel
        header_style = xlwt.easyxf('font: bold on; align: wrap on, vert centre, horiz center; borders: bottom thin')
        date_style = xlwt.easyxf('align: wrap on, vert centre, horiz center', num_format_str='DD/MM/YYYY')
        currency_style = xlwt.easyxf('align: wrap on, vert centre, horiz right', num_format_str='#,##0')
        
        # Écrire les en-têtes
        headers = ['Numéro', 'Date Émission', 'Client', 'Montant HT', 'TVA', 'Montant TTC', 'Statut']
        for col, header in enumerate(headers):
            ws.write(0, col, header, header_style)
        
        # Écrire les données
        for row, facture in enumerate(factures, 1):
            ws.write(row, 0, facture.numero)
            ws.write(row, 1, facture.date_emission, date_style)
            ws.write(row, 2, facture.tiers_nom)
            ws.write(row, 3, float(facture.montant_total), currency_style)
            ws.write(row, 4, float(facture.tva), currency_style)
            ws.write(row, 5, float(facture.montant_final), currency_style)
            ws.write(row, 6, facture.statut)
        
        # Ajuster la largeur des colonnes
        for col in range(len(headers)):
            ws.col(col).width = 256 * 15  # Environ 15 caractères
        
        # Préparer la réponse HTTP
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="factures.xls"'
        wb.save(response)
        
        return response
    except Exception as e:
        messages.error(request, f"Erreur lors de l'exportation Excel: {str(e)}")
        return redirect('fleet_app:facture_list')

@login_required
def supprimer_ligne_facture(request, pk):
    """Supprimer une ligne de facture existante"""
    # Vérifier que la ligne appartient à une facture de l'utilisateur connecté
    ligne = get_object_or_404(LigneFacture, id=pk, facture__utilisateur=request.user)
    facture = ligne.facture
    
    if request.method == 'POST':
        # Supprimer la ligne
        ligne.delete()
        
        # Recalculer les montants de la facture
        facture.calculer_montants()
        
        messages.success(request, "Ligne supprimée avec succès.")
        return redirect('fleet_app:facture_detail', pk=facture.numero)
    
    context = {
        'ligne': ligne,
        'facture': facture,
        'titre': "Confirmer la suppression"
    }
    
    return render(request, 'fleet_app/inventaire/confirmer_suppression.html', context)


@login_required
def modifier_ligne_facture(request, pk):
    """Modifier une ligne de facture existante"""
    # Vérifier que la ligne appartient à une facture de l'utilisateur connecté
    ligne = get_object_or_404(LigneFacture, id=pk, facture__utilisateur=request.user)
    facture = ligne.facture
    
    if request.method == 'POST':
        form = LigneFactureForm(request.POST, instance=ligne)
        if form.is_valid():
            ligne_modifiee = form.save(commit=False)
            
            # Calculer automatiquement le montant
            ligne_modifiee.montant = ligne_modifiee.prix_unitaire * ligne_modifiee.quantite
            ligne_modifiee.save()
            
            # Recalculer les montants de la facture
            facture.calculer_montants()
            
            messages.success(request, "Ligne modifiée avec succès.")
            return redirect('fleet_app:facture_detail', pk=facture.numero)
    else:
        form = LigneFactureForm(instance=ligne)
    
    context = {
        'form': form,
        'facture': facture,
        'ligne': ligne,
        'titre': f"Modifier la ligne de facture"
    }
    
    return render(request, 'fleet_app/inventaire/ligne_facture_form.html', context)


@login_required
def ajouter_ligne_facture(request, pk):
    """Ajouter une ligne à une facture existante"""
    # Vérifier que la facture appartient à l'utilisateur connecté
    facture = get_object_or_404(Facture, numero=pk, utilisateur=request.user)
    
    if request.method == 'POST':
        form = LigneFactureForm(request.POST)
        if form.is_valid():
            ligne = form.save(commit=False)
            ligne.facture = facture
            
            # Calculer automatiquement le montant
            ligne.montant = ligne.prix_unitaire * ligne.quantite
            ligne.save()
            
            # Recalculer les montants de la facture
            facture.calculer_montants()
            
            messages.success(request, "Ligne ajoutée avec succès.")
            return redirect('fleet_app:facture_detail', pk=facture.numero)
    else:
        form = LigneFactureForm()
    
    context = {
        'form': form,
        'facture': facture,
        'titre': f"Ajouter une ligne à la facture {facture.numero}"
    }
    
    return render(request, 'fleet_app/inventaire/ligne_facture_form.html', context)


@login_required
@user_owns_data(Facture, pk_url_kwarg='pk', relation_path=['utilisateur'])
def export_facture_pdf(request, pk):
    """Exporter une facture spécifique au format PDF
    Sécurisée pour garantir que l'utilisateur ne peut exporter que ses propres factures
    """
    facture = get_object_or_404(Facture, numero=pk)
    lignes = facture.lignes.all()
    
    # Vérifier la disponibilité de xhtml2pdf (pisa)
    if not PISA_AVAILABLE:
        messages.error(request, "La génération de PDF n'est pas disponible (xhtml2pdf non installé).")
        return redirect('facture_detail', facture.numero)

    try:
        # Préparer le contexte pour le template
        context = {
            'facture': facture,
            'lignes': lignes,
        }
        
        # Rendre le template HTML
        template = get_template('fleet_app/inventaire/facture_pdf.html')
        html_string = template.render(context)
        
        # Créer un buffer pour stocker le PDF
        buffer = io.BytesIO()
        
        # Générer le PDF avec xhtml2pdf
        pisa_status = pisa.CreatePDF(
            html_string,
            dest=buffer,
        )
        
        # Vérifier si la génération du PDF a réussi
        if pisa_status.err:
            messages.error(request, "Une erreur est survenue lors de la génération du PDF.")
            return redirect('facture_detail', facture.numero)
        
        # Récupérer le contenu du buffer
        buffer.seek(0)
        pdf_content = buffer.getvalue()
        buffer.close()
        
        # Créer la réponse HTTP avec le PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="facture_{facture.numero}.pdf"'
        
        return response
    except Exception as e:
        messages.error(request, f"Erreur lors de la génération du PDF : {str(e)}")
        return redirect('facture_detail', facture.numero)

 

@require_POST
@login_required
def get_produit_info_facture(request):
    """API pour obtenir les informations d'un produit pour une facture"""
    produit_id = request.POST.get('produit_id')
    
    if not produit_id:
        return JsonResponse({
            'success': False,
            'message': 'ID produit manquant dans la requête'
        })
    
    try:
        # Le produit utilise id_produit comme clé primaire (qui est une chaîne de caractères)
        # Filtrer pour n'obtenir que les produits de l'utilisateur connecté
        produit = Produit.objects.get(id_produit=produit_id, user=request.user)
        data = {
            'success': True,
            'nom_produit': produit.nom,
            'categorie': produit.categorie,
            'prix_unitaire': str(produit.prix_unitaire),  # Convertir en string pour éviter les problèmes de sérialisation
        }
    except Produit.DoesNotExist:
        data = {
            'success': False,
            'message': f'Produit avec ID {produit_id} non trouvé',
        }
    except Exception as e:
        data = {
            'success': False,
            'message': f'Erreur lors de la récupération du produit: {str(e)}',
        }
    
    return JsonResponse(data)
