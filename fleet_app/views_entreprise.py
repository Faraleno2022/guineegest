from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal, InvalidOperation
import csv
import datetime

from .models_entreprise import HeureSupplementaire, Employe, PaieEmploye
from .forms_entreprise import HeureSupplementaireForm

# Vues pour HeureSupplementaire
class HeureSupplementaireListView(LoginRequiredMixin, ListView):
    model = HeureSupplementaire
    template_name = 'fleet_app/entreprise/heure_supplementaire_list.html'
    context_object_name = 'heures_sup'
    paginate_by = 20
    
    def get_queryset(self):
        """
        Filtre les heures supplémentaires par utilisateur et période
        """
        queryset = HeureSupplementaire.objects.filter(
            employe__user=self.request.user
        ).select_related('employe').order_by('-date', '-id')
        
        # Filtrage par mois et année si spécifiés
        mois = self.request.GET.get('mois')
        annee = self.request.GET.get('annee')
        
        if mois and annee:
            try:
                queryset = queryset.filter(date__month=int(mois), date__year=int(annee))
            except ValueError:
                pass
        
        return queryset
    
    def get_context_data(self, **kwargs):
        """
        Ajoute des données contextuelles pour le template
        """
        context = super().get_context_data(**kwargs)
        
        # Ajouter la liste des employés pour les formulaires
        context['employes'] = Employe.objects.filter(user=self.request.user)
        
        return context
    
    def post(self, request, *args, **kwargs):
        """
        Gère les actions POST
        """
        action = request.POST.get('action')
        
        if action == 'definir_montant':
            return self.definir_montant_personnalise(request)
        elif action == 'delete':
            return self.supprimer_heure(request)
        elif action == 'edit':
            return self.modifier_heure(request)
        
        # Si l'action n'est pas reconnue, retourner à la vue normale
        return self.get(request, *args, **kwargs)
    
    def definir_montant_personnalise(self, request):
        """
        Définit un montant horaire personnalisé pour une heure supplémentaire
        """
        try:
            heure_id = request.POST.get('heure_id')
            montant_manuel = request.POST.get('montant_manuel')
            
            if not heure_id:
                messages.error(request, "ID de l'heure supplémentaire manquant.")
                return redirect('fleet_app:heure_supplementaire_list')
            
            # Récupérer l'heure supplémentaire
            heure_supp = get_object_or_404(HeureSupplementaire, 
                                         id=heure_id, 
                                         employe__user=request.user)
            
            # Si montant_manuel est vide, réinitialiser au taux global
            if not montant_manuel or montant_manuel.strip() == '':
                heure_supp.taux_horaire = None
                heure_supp.save()
                messages.success(request, "Taux horaire réinitialisé au taux global.")
                return redirect('fleet_app:heure_supplementaire_list')
            
            # Valider le montant
            try:
                montant_personnalise = Decimal(str(montant_manuel))
                if montant_personnalise <= 0:
                    messages.error(request, "Le montant doit être supérieur à zéro.")
                    return redirect('fleet_app:heure_supplementaire_list')
            except (ValueError, InvalidOperation):
                messages.error(request, "Format de montant invalide.")
                return redirect('fleet_app:heure_supplementaire_list')
            
            # Définir le taux horaire personnalisé
            heure_supp.taux_horaire = montant_personnalise
            
            # Sauvegarder avec protection contre l'écrasement automatique
            heure_supp.save(skip_auto_calc=True)
            
            messages.success(request, 
                           f"Taux horaire personnalisé défini: {montant_personnalise:,.0f} GNF")
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la définition du montant: {str(e)}")
        
        return redirect('fleet_app:heure_supplementaire_list')
    
    def supprimer_heure(self, request):
        """
        Supprime une heure supplémentaire
        """
        try:
            heure_id = request.POST.get('heure_id')
            heure_supp = get_object_or_404(HeureSupplementaire, 
                                         id=heure_id, 
                                         employe__user=request.user)
            heure_supp.delete()
            messages.success(request, "Heure supplémentaire supprimée avec succès.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la suppression: {str(e)}")
        
        return redirect('fleet_app:heure_supplementaire_list')
    
    def modifier_heure(self, request):
        """
        Modifie une heure supplémentaire via le modal
        """
        try:
            heure_id = request.POST.get('heure_id')
            heure_supp = get_object_or_404(HeureSupplementaire, 
                                         id=heure_id, 
                                         employe__user=request.user)
            
            # Récupérer les données du formulaire
            date = request.POST.get('date')
            heure_debut = request.POST.get('heure_debut')
            heure_fin = request.POST.get('heure_fin')
            duree = request.POST.get('duree')
            taux_horaire = request.POST.get('taux_horaire')
            
            # Mettre à jour les champs
            if date:
                heure_supp.date = date
            if heure_debut:
                heure_supp.heure_debut = heure_debut
            if heure_fin:
                heure_supp.heure_fin = heure_fin
            if duree:
                heure_supp.duree = Decimal(str(duree))
            if taux_horaire:
                heure_supp.taux_horaire = Decimal(str(taux_horaire))
            
            heure_supp.save()
            messages.success(request, "Heure supplémentaire modifiée avec succès.")
            
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification: {str(e)}")
        
        return redirect('fleet_app:heure_supplementaire_list')

def configuration_montant_employe_list(request):
    """Vue pour la configuration des montants employés"""
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    
    # Vue temporaire pour éviter l'AttributeError
    # TODO: Implémenter la logique complète de configuration des montants employés
    context = {
        'title': 'Configuration des montants employés',
        'message': 'Configuration des montants employés - En développement'
    }
    
    # Retourner une page temporaire ou rediriger vers une autre vue
    return render(request, 'fleet_app/entreprise/configuration_temp.html', context)

def configuration_montant_employe_form(request):
    """Vue pour le formulaire de configuration des montants employés"""
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    
    # Vue temporaire pour éviter l'AttributeError
    # TODO: Implémenter la logique complète du formulaire de configuration des montants employés
    context = {
        'title': 'Formulaire de configuration des montants employés',
        'message': 'Formulaire de configuration des montants employés - En développement'
    }
    
    # Retourner une page temporaire ou rediriger vers une autre vue
    return render(request, 'fleet_app/entreprise/configuration_temp.html', context)

def configuration_montant_employe_ajax(request):
    """Vue AJAX pour la configuration des montants employés"""
    from django.http import JsonResponse
    from django.contrib.auth.decorators import login_required
    
    # Vue temporaire pour éviter l'AttributeError
    # TODO: Implémenter la logique complète AJAX de configuration des montants employés
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': 'Configuration AJAX des montants employés - En développement'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Méthode non autorisée'
    })

def configuration_montant_statut(request):
    """Vue pour la configuration des montants par statut"""
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    
    # Vue temporaire pour éviter l'AttributeError
    # TODO: Implémenter la logique complète de configuration des montants par statut
    context = {
        'title': 'Configuration des montants par statut',
        'message': 'Configuration des montants par statut - En développement'
    }
    
    # Retourner une page temporaire ou rediriger vers une autre vue
    return render(request, 'fleet_app/entreprise/configuration_temp.html', context)

def config_charges_sociales(request):
    """Vue pour la configuration des charges sociales"""
    from django.shortcuts import render
    from django.contrib.auth.decorators import login_required
    from django.http import JsonResponse
    
    # Vue temporaire pour éviter l'AttributeError
    # TODO: Implémenter la logique complète de configuration des charges sociales
    if request.method == 'POST':
        return JsonResponse({
            'success': True,
            'message': 'Configuration des charges sociales - En développement'
        })
    
    context = {
        'title': 'Configuration des charges sociales',
        'message': 'Configuration des charges sociales - En développement'
    }
    
    # Retourner une page temporaire ou rediriger vers une autre vue
    return render(request, 'fleet_app/entreprise/configuration_temp.html', context)
