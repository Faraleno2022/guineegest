from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse
from django.db.models import Count
from .models_alertes import Alerte
from .models import Vehicule, DistanceParcourue, ConsommationCarburant, DisponibiliteVehicule, UtilisationVehicule, IncidentSecurite, CoutFonctionnement, CoutFinancier

@login_required
def alerte_list(request):
    """
    Vue pour afficher la liste des alertes actives et résolues
    """
    alertes_actives = Alerte.objects.filter(statut='Active').order_by('-date_creation')
    alertes_resolues = Alerte.objects.filter(statut='Résolue').order_by('-date_resolution')
    
    context = {
        'alertes_actives': alertes_actives,
        'alertes_resolues': alertes_resolues,
        'active_count': alertes_actives.count(),
        'resolved_count': alertes_resolues.count(),
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
