# CORRECTION URGENTE - Sécurisation de la page publique /accueil/
# À remplacer dans fleet_app/views_location.py

from django.shortcuts import render, redirect
from django.utils import timezone
from .models_location import LocationVehicule, FeuillePontageLocation
from .models import FournisseurVehicule

def accueil_public(request):
    """
    Page d'accueil publique SÉCURISÉE pour les propriétaires de véhicules.
    Nécessite un code d'accès unique par propriétaire.
    """
    # Récupérer le code d'accès
    code = request.GET.get('code', '').strip()
    
    # Si pas de code, afficher formulaire de saisie
    if not code:
        return render(request, 'fleet_app/locations/acces_code.html', {
            'error': None
        })
    
    # Vérifier le code et récupérer le fournisseur
    try:
        fournisseur = FournisseurVehicule.objects.get(
            code_acces=code,
            # Optionnel: vérifier que le fournisseur est actif
            # actif=True
        )
    except FournisseurVehicule.DoesNotExist:
        return render(request, 'fleet_app/locations/acces_code.html', {
            'error': 'Code d\'accès invalide ou expiré'
        })
    
    # Sauvegarder en session pour éviter de redemander le code
    request.session['code_proprietaire'] = code
    request.session['fournisseur_id'] = fournisseur.id
    
    today = timezone.now().date()
    
    # ✅ SÉCURISÉ : Filtrer UNIQUEMENT les véhicules de ce propriétaire
    locations_actives = LocationVehicule.objects.filter(
        fournisseur=fournisseur,  # ← FILTRAGE PAR PROPRIÉTAIRE
        statut='Active'
    ).select_related(
        'vehicule'
    ).order_by('vehicule__immatriculation')
    
    # ✅ SÉCURISÉ : Feuilles de pontage du jour pour ce propriétaire uniquement
    feuilles_today = FeuillePontageLocation.objects.filter(
        location__fournisseur=fournisseur,  # ← FILTRAGE PAR PROPRIÉTAIRE
        date=today
    ).select_related(
        'location',
        'location__vehicule'
    )
    
    # Créer un dictionnaire des véhicules avec leurs informations du jour
    vehicules_info = {}
    
    for location in locations_actives:
        vehicule = location.vehicule
        immat = vehicule.immatriculation
        
        # Chercher la feuille de pontage du jour pour ce véhicule
        feuille = feuilles_today.filter(location=location).first()
        
        vehicules_info[immat] = {
            'vehicule': vehicule,
            'location': location,
            'fournisseur': fournisseur,  # Toujours le même propriétaire
            'feuille': feuille,
            'statut_jour': feuille.statut if feuille else 'Non renseigné',
            'commentaire': feuille.commentaire if feuille else '',
            'a_travaille': feuille and feuille.statut == 'Travail',
            'en_panne': feuille and feuille.statut in ['Hors service', 'Panne'],
            'en_entretien': feuille and feuille.statut == 'Entretien',
        }
    
    context = {
        'today': today,
        'fournisseur': fournisseur,  # Informations du propriétaire
        'vehicules_info': vehicules_info,
        'total_vehicules': len(vehicules_info),
        'vehicules_travail': sum(1 for v in vehicules_info.values() if v['a_travaille']),
        'vehicules_panne': sum(1 for v in vehicules_info.values() if v['en_panne']),
        'vehicules_entretien': sum(1 for v in vehicules_info.values() if v['en_entretien']),
    }
    
    return render(request, 'fleet_app/locations/accueil_public.html', context)
