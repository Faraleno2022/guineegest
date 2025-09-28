from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Vehicule
from .forms import VehiculeForm


@login_required
def vehicule_create_simple(request):
    """Vue simple pour créer un véhicule avec gestion d'erreurs robuste."""
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            data = {
                'id_vehicule': request.POST.get('id_vehicule', '').strip(),
                'immatriculation': request.POST.get('immatriculation', '').strip(),
                'marque': request.POST.get('marque', '').strip(),
                'modele': request.POST.get('modele', '').strip(),
                'type_moteur': request.POST.get('type_moteur', ''),
                'categorie': request.POST.get('categorie', ''),
                'statut_actuel': request.POST.get('statut_actuel', ''),
                'date_acquisition': request.POST.get('date_acquisition', ''),
                'date_mise_service': request.POST.get('date_mise_service', ''),
                'kilometrage_initial': request.POST.get('kilometrage_initial', '0'),
                'affectation': request.POST.get('affectation', '').strip(),
                'numero_chassis': request.POST.get('numero_chassis', '').strip(),
                'numero_moteur': request.POST.get('numero_moteur', '').strip(),
                'observations': request.POST.get('observations', '').strip(),
            }
            
            # Validation manuelle
            errors = {}
            
            if not data['id_vehicule']:
                errors['id_vehicule'] = 'L\'ID véhicule est obligatoire'
            elif Vehicule.objects.filter(id_vehicule=data['id_vehicule']).exists():
                errors['id_vehicule'] = 'Un véhicule avec cet ID existe déjà'
                
            if not data['immatriculation']:
                errors['immatriculation'] = 'L\'immatriculation est obligatoire'
            elif Vehicule.objects.filter(immatriculation=data['immatriculation']).exists():
                errors['immatriculation'] = 'Un véhicule avec cette immatriculation existe déjà'
                
            if not data['marque']:
                errors['marque'] = 'La marque est obligatoire'
                
            if not data['modele']:
                errors['modele'] = 'Le modèle est obligatoire'
                
            if not data['type_moteur']:
                errors['type_moteur'] = 'Le type de moteur est obligatoire'
                
            if not data['categorie']:
                errors['categorie'] = 'La catégorie est obligatoire'
                
            if not data['statut_actuel']:
                errors['statut_actuel'] = 'Le statut actuel est obligatoire'
            
            # Validation du kilométrage
            try:
                kilometrage = int(data['kilometrage_initial']) if data['kilometrage_initial'] else 0
                if kilometrage < 0:
                    errors['kilometrage_initial'] = 'Le kilométrage ne peut pas être négatif'
            except ValueError:
                errors['kilometrage_initial'] = 'Le kilométrage doit être un nombre entier'
                kilometrage = 0
            
            # Si des erreurs, les afficher
            if errors:
                for field, error in errors.items():
                    messages.error(request, f"{error}")
                
                # Garder les données saisies
                context = {
                    'form_data': data,
                    'errors': errors,
                    'moteur_choices': Vehicule.MOTEUR_CHOICES,
                    'categorie_choices': Vehicule.CATEGORIE_CHOICES,
                    'statut_choices': Vehicule.STATUT_CHOICES,
                }
                return render(request, 'fleet_app/vehicule_form_simple.html', context)
            
            # Créer le véhicule
            vehicule = Vehicule(
                id_vehicule=data['id_vehicule'],
                immatriculation=data['immatriculation'],
                marque=data['marque'],
                modele=data['modele'],
                type_moteur=data['type_moteur'],
                categorie=data['categorie'],
                statut_actuel=data['statut_actuel'],
                kilometrage_initial=kilometrage,
                affectation=data['affectation'],
                numero_chassis=data['numero_chassis'],
                numero_moteur=data['numero_moteur'],
                observations=data['observations'],
                user=request.user,
            )
            
            # Assigner l'entreprise si disponible
            ent = getattr(getattr(request.user, 'profil', None), 'entreprise', None) or getattr(request.user, 'entreprise', None)
            if ent:
                vehicule.entreprise = ent
            
            # Dates optionnelles
            if data['date_acquisition']:
                try:
                    vehicule.date_acquisition = data['date_acquisition']
                except:
                    pass
                    
            if data['date_mise_service']:
                try:
                    vehicule.date_mise_service = data['date_mise_service']
                except:
                    pass
            
            # Sauvegarder
            vehicule.save()
            
            messages.success(request, f'Véhicule {vehicule.immatriculation} créé avec succès!')
            return redirect('fleet_app:vehicule_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            
            # Garder les données saisies en cas d'erreur
            context = {
                'form_data': data if 'data' in locals() else {},
                'moteur_choices': Vehicule.MOTEUR_CHOICES,
                'categorie_choices': Vehicule.CATEGORIE_CHOICES,
                'statut_choices': Vehicule.STATUT_CHOICES,
            }
            return render(request, 'fleet_app/vehicule_form_simple.html', context)
    
    # GET: afficher le formulaire vide
    context = {
        'form_data': {},
        'moteur_choices': Vehicule.MOTEUR_CHOICES,
        'categorie_choices': Vehicule.CATEGORIE_CHOICES,
        'statut_choices': Vehicule.STATUT_CHOICES,
    }
    return render(request, 'fleet_app/vehicule_form_simple.html', context)
