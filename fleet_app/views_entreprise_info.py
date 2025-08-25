from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models_accounts import Profil, Entreprise
from django import forms

class EntrepriseForm(forms.ModelForm):
    """Formulaire pour les informations de l'entreprise"""
    
    class Meta:
        model = Entreprise
        fields = [
            'nom_entreprise', 'forme_juridique', 'nom_responsable', 'logo',
            'adresse', 'telephone', 'email', 'site_web',
            'rccm', 'nif', 'cnss', 'banque', 'numero_compte'
        ]
        widgets = {
            'nom_entreprise': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de votre entreprise'
            }),
            'forme_juridique': forms.Select(attrs={
                'class': 'form-control'
            }),
            'nom_responsable': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du responsable/dirigeant'
            }),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Adresse complète de l\'entreprise'
            }),
            'telephone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+224 XXX XX XX XX'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@entreprise.com'
            }),
            'site_web': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://www.entreprise.com'
            }),
            'rccm': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro RCCM'
            }),
            'nif': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro NIF'
            }),
            'cnss': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro CNSS'
            }),
            'banque': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la banque'
            }),
            'numero_compte': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Numéro de compte bancaire'
            }),
            'logo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

@login_required
def entreprise_info_view(request):
    """Vue pour gérer les informations de l'entreprise"""
    
    # Récupération ou création du profil et de l'entreprise
    profil, created = Profil.objects.get_or_create(
        user=request.user,
        defaults={
            'type_compte': 'entreprise',
            'telephone': '',
            'email': request.user.email or '',
            'role': 'admin'
        }
    )
    
    # Si le profil n'est pas de type entreprise, le convertir
    if profil.type_compte != 'entreprise':
        profil.type_compte = 'entreprise'
        profil.save()
    
    # Récupération ou création de l'entreprise
    entreprise = None
    if hasattr(profil, 'entreprise'):
        entreprise = profil.entreprise
    
    if request.method == 'POST':
        if entreprise:
            form = EntrepriseForm(request.POST, request.FILES, instance=entreprise)
        else:
            form = EntrepriseForm(request.POST, request.FILES)
        
        if form.is_valid():
            entreprise = form.save(commit=False)
            entreprise.profil = profil
            entreprise.save()
            
            messages.success(request, 'Informations de l\'entreprise mises à jour avec succès!')
            
            # Retourner JSON si c'est une requête AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Informations sauvegardées avec succès!'
                })
            
            return redirect('fleet_app:entreprise_info')
        else:
            messages.error(request, 'Erreur lors de la sauvegarde. Veuillez vérifier les champs.')
            
            # Retourner JSON si c'est une requête AJAX
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False,
                    'errors': form.errors
                })
    else:
        form = EntrepriseForm(instance=entreprise)
    
    context = {
        'form': form,
        'entreprise': entreprise,
        'profil': profil,
        'has_entreprise': entreprise is not None,
    }
    
    return render(request, 'fleet_app/entreprise/entreprise_info.html', context)

@login_required
def entreprise_info_api(request):
    """API pour récupérer les informations de l'entreprise (JSON)"""
    try:
        profil = Profil.objects.get(user=request.user)
        if hasattr(profil, 'entreprise'):
            entreprise = profil.entreprise
            data = {
                'nom_entreprise': entreprise.nom_entreprise,
                'forme_juridique': entreprise.get_forme_juridique_display(),
                'nom_responsable': entreprise.nom_responsable,
                'adresse': entreprise.adresse,
                'telephone': entreprise.telephone,
                'email': entreprise.email,
                'site_web': entreprise.site_web,
                'rccm': entreprise.rccm,
                'nif': entreprise.nif,
                'cnss': entreprise.cnss,
                'banque': entreprise.banque,
                'numero_compte': entreprise.numero_compte,
                'logo_url': entreprise.logo.url if entreprise.logo else None,
            }
            return JsonResponse({'success': True, 'data': data})
        else:
            return JsonResponse({'success': False, 'message': 'Aucune entreprise trouvée'})
    except Profil.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Profil non trouvé'})
