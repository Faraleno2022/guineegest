from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models_location import FournisseurVehicule


@login_required
def fournisseur_create_simple(request):
    """Vue simple pour créer un fournisseur avec gestion d'erreurs robuste."""
    
    if request.method == 'POST':
        try:
            # Récupérer les données du formulaire
            data = {
                'nom': request.POST.get('nom', '').strip(),
                'contact': request.POST.get('contact', '').strip(),
                'telephone': request.POST.get('telephone', '').strip(),
                'email': request.POST.get('email', '').strip(),
                'adresse': request.POST.get('adresse', '').strip(),
                'ville': request.POST.get('ville', '').strip(),
                'pays': request.POST.get('pays', '').strip(),
                'notes': request.POST.get('notes', '').strip(),
            }
            
            # Validation manuelle
            errors = {}
            
            if not data['nom']:
                errors['nom'] = 'Le nom du fournisseur est obligatoire'
            elif FournisseurVehicule.objects.filter(nom=data['nom'], user=request.user).exists():
                errors['nom'] = 'Un fournisseur avec ce nom existe déjà'
                
            if not data['contact']:
                errors['contact'] = 'Le nom du contact est obligatoire'
                
            if not data['telephone']:
                errors['telephone'] = 'Le numéro de téléphone est obligatoire'
            
            # Validation email optionnelle mais format correct si fourni
            if data['email']:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, data['email']):
                    errors['email'] = 'Format d\'email invalide'
            
            # Si des erreurs, les afficher
            if errors:
                for field, error in errors.items():
                    messages.error(request, f"{error}")
                
                # Garder les données saisies
                context = {
                    'form_data': data,
                    'errors': errors,
                }
                return render(request, 'fleet_app/fournisseur_form_simple.html', context)
            
            # Créer le fournisseur
            fournisseur = FournisseurVehicule(
                nom=data['nom'],
                contact=data['contact'],
                telephone=data['telephone'],
                email=data['email'],
                adresse=data['adresse'],
                ville=data['ville'],
                pays=data['pays'],
                notes=data['notes'],
                user=request.user,
            )
            
            # Assigner l'entreprise si disponible
            ent = getattr(getattr(request.user, 'profil', None), 'entreprise', None) or getattr(request.user, 'entreprise', None)
            if ent and hasattr(fournisseur, 'entreprise'):
                fournisseur.entreprise = ent
            
            # Sauvegarder
            fournisseur.save()
            
            messages.success(request, f'Fournisseur {fournisseur.nom} créé avec succès!')
            return redirect('fleet_app:fournisseur_location_list')
            
        except Exception as e:
            messages.error(request, f'Erreur lors de la création: {str(e)}')
            
            # Garder les données saisies en cas d'erreur
            context = {
                'form_data': data if 'data' in locals() else {},
            }
            return render(request, 'fleet_app/fournisseur_form_simple.html', context)
    
    # GET: afficher le formulaire vide
    context = {
        'form_data': {},
    }
    return render(request, 'fleet_app/fournisseur_form_simple.html', context)
