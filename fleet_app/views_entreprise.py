from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
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

@login_required
@require_POST
def configuration_montant_employe_ajax(request):
    """Vue AJAX pour la configuration des montants employés
    Contrat d'entrée (POST):
      - employe_id: int (obligatoire)
      - type_montant: str parmi
          ['salaire_base','salaire_journalier','avance','hs_ouvrable','hs_dimanche_ferie','taux_horaire_specifique']
      - valeur: Decimal (>= 0, <= 99_999_999.99)
      - date_effet: str (YYYY-MM-DD) optionnel (accepté mais non encore historisé)
    Retour JSON:
      {success, message, updated_field, previous_value, new_value, employe: {id, matricule, nom, prenom}, date_effet}
    """
    from django.http import JsonResponse
    from django.utils.dateparse import parse_date
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Méthode non autorisée'}, status=405)
    
    # Authentification requise
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Authentification requise'}, status=401)
    
    employe_id = request.POST.get('employe_id')
    type_montant = request.POST.get('type_montant')
    valeur_raw = request.POST.get('valeur')
    date_effet_raw = request.POST.get('date_effet')
    
    # Champs obligatoires
    if not employe_id or not type_montant or valeur_raw is None:
        return JsonResponse({
            'success': False,
            'message': "Champs requis manquants: 'employe_id', 'type_montant', 'valeur'"
        }, status=400)
    
    # Mapping des champs autorisés -> attribut Employe
    field_map = {
        'salaire_base': 'salaire_base',
        'salaire_journalier': 'salaire_journalier',
        'avance': 'avances',
        'hs_ouvrable': 'montant_heure_supp_jour_ouvrable',
        'hs_dimanche_ferie': 'montant_heure_supp_dimanche_ferie',
        'taux_horaire_specifique': 'taux_horaire_specifique',
    }
    
    if type_montant not in field_map:
        return JsonResponse({'success': False, 'message': 'type_montant invalide'}, status=400)
    
    # Parse employe_id
    try:
        employe_id_int = int(employe_id)
    except (TypeError, ValueError):
        return JsonResponse({'success': False, 'message': "employe_id invalide"}, status=400)
    
    # Vérifier l'existence et l'appartenance de l'employé
    try:
        employe = get_object_or_404(Employe, id=employe_id_int, user=request.user)
    except Exception:
        return JsonResponse({'success': False, 'message': "Employé introuvable"}, status=404)
    
    # Validation de la valeur
    try:
        valeur_dec = Decimal(str(valeur_raw))
    except (InvalidOperation, ValueError):
        return JsonResponse({'success': False, 'message': 'Format de valeur invalide'}, status=400)
    if valeur_dec < 0:
        return JsonResponse({'success': False, 'message': 'La valeur doit être positive'}, status=400)
    # borne haute générique selon max_digits=10, decimal_places=2
    max_dec = Decimal('99999999.99')
    if valeur_dec > max_dec:
        return JsonResponse({'success': False, 'message': f'La valeur dépasse la limite {max_dec}'}, status=400)
    
    # date_effet optionnelle (acceptée mais pas encore historisée)
    date_effet = None
    if date_effet_raw:
        date_effet = parse_date(date_effet_raw)
        if date_effet is None:
            return JsonResponse({'success': False, 'message': 'date_effet invalide (YYYY-MM-DD)'}, status=400)
    
    # Mise à jour de l'attribut ciblé
    attr = field_map[type_montant]
    previous_value = getattr(employe, attr, None)
    setattr(employe, attr, valeur_dec)
    
    try:
        employe.save()
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Erreur lors de la sauvegarde: {str(e)}'}, status=500)
    
    return JsonResponse({
        'success': True,
        'message': 'Montant mis à jour avec succès',
        'updated_field': attr,
        'previous_value': f"{previous_value}" if previous_value is not None else None,
        'new_value': f"{valeur_dec}",
        'employe': {
            'id': employe.id,
            'matricule': employe.matricule,
            'prenom': employe.prenom,
            'nom': employe.nom,
        },
        'date_effet': date_effet.isoformat() if date_effet else None,
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
