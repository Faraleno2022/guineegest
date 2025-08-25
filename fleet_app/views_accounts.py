from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from django.db import transaction

from .models_accounts import Profil, PersonnePhysique, Entreprise
from .forms_accounts import (
    TypeCompteForm, ProfilForm, PersonnePhysiqueForm, 
    EntrepriseForm, CompteUtilisateurForm, ConditionsForm
)


def check_profile_completion(request):
    """
    Vérifie si l'utilisateur a complété son profil.
    Si non, redirige vers le formulaire de création de compte.
    """
    if request.user.is_authenticated:
        try:
            profil = request.user.profil
            if not profil.compte_complete:
                return HttpResponseRedirect(reverse('fleet_app:creation_compte'))
        except Profil.DoesNotExist:
            return HttpResponseRedirect(reverse('fleet_app:creation_compte'))
    return None


@login_required
def creation_compte(request):
    """Vue pour le formulaire de création de compte après la première connexion"""
    # Vérifier si l'utilisateur a déjà un profil complet
    try:
        profil = request.user.profil
        if profil.compte_complete:
            messages.info(request, "Votre compte est déjà configuré.")
            return redirect('fleet_app:dashboard')
    except Profil.DoesNotExist:
        # Continuer avec la création du profil
        pass
    
    # Récupérer l'étape actuelle depuis la session ou définir la première étape
    etape = request.session.get('creation_compte_etape', 1)
    
    if etape == 1:
        # Étape 1: Choix du type de compte
        if request.method == 'POST':
            form = TypeCompteForm(request.POST)
            if form.is_valid():
                # Stocker le type de compte dans la session
                request.session['type_compte'] = form.cleaned_data['type_compte']
                request.session['creation_compte_etape'] = 2
                return redirect('fleet_app:creation_compte')
        else:
            form = TypeCompteForm()
        
        return render(request, 'fleet_app/accounts/creation_compte_etape1.html', {
            'form': form,
            'etape': etape,
            'titre': "Choix du type de compte"
        })
    
    elif etape == 2:
        # Étape 2: Informations spécifiques selon le type de compte
        type_compte = request.session.get('type_compte')
        
        if not type_compte:
            messages.error(request, "Veuillez d'abord choisir un type de compte.")
            request.session['creation_compte_etape'] = 1
            return redirect('fleet_app:creation_compte')
        
        if request.method == 'POST':
            if type_compte == 'personne':
                form = PersonnePhysiqueForm(request.POST, request.FILES)
            else:  # type_compte == 'entreprise'
                form = EntrepriseForm(request.POST, request.FILES)
            
            if form.is_valid():
                # Stocker les données du formulaire dans la session
                # Convertir les objets date en chaînes de caractères pour éviter les erreurs de sérialisation JSON
                form_data = {}
                for key, value in form.cleaned_data.items():
                    if hasattr(value, 'strftime'):  # Si c'est un objet date ou datetime
                        form_data[key] = value.strftime('%Y-%m-%d')
                    elif hasattr(value, 'read'):  # Si c'est un fichier uploadé (InMemoryUploadedFile)
                        # Ne pas stocker le fichier dans la session
                        # On le stockera temporairement dans request.FILES et on le récupérera à l'étape finale
                        if key == 'photo' or key == 'logo':
                            # Stocker uniquement le nom du fichier pour référence
                            form_data[key + '_name'] = value.name
                            # Marquer qu'un fichier a été uploadé
                            request.session['has_file_upload'] = True
                    else:
                        form_data[key] = value
                
                request.session['form_specifique_data'] = form_data
                request.session['creation_compte_etape'] = 3
                return redirect('fleet_app:creation_compte')
        else:
            if type_compte == 'personne':
                form = PersonnePhysiqueForm()
                titre = "Informations personnelles"
            else:  # type_compte == 'entreprise'
                form = EntrepriseForm()
                titre = "Informations sur l'entreprise"
        
        return render(request, 'fleet_app/accounts/creation_compte_etape2.html', {
            'form': form,
            'etape': etape,
            'type_compte': type_compte,
            'titre': titre
        })
    
    elif etape == 3:
        # Étape 3: Informations communes (téléphone, email, adresse, rôle)
        if request.method == 'POST':
            form = ProfilForm(request.POST)
            if form.is_valid():
                # Stocker les données du formulaire dans la session
                # Convertir les objets non sérialisables en chaînes de caractères
                form_data = {}
                for key, value in form.cleaned_data.items():
                    if hasattr(value, 'strftime'):  # Si c'est un objet date ou datetime
                        form_data[key] = value.strftime('%Y-%m-%d')
                    else:
                        form_data[key] = value
                
                request.session['form_profil_data'] = form_data
                request.session['creation_compte_etape'] = 4
                return redirect('fleet_app:creation_compte')
        else:
            form = ProfilForm()
        
        return render(request, 'fleet_app/accounts/creation_compte_etape3.html', {
            'form': form,
            'etape': etape,
            'titre': "Informations de contact"
        })
    
    elif etape == 4:
        # Étape 4: Conditions à accepter
        if request.method == 'POST':
            form = ConditionsForm(request.POST)
            if form.is_valid():
                # Stocker les données du formulaire dans la session
                # Convertir les objets non sérialisables en chaînes de caractères
                form_data = {}
                for key, value in form.cleaned_data.items():
                    if hasattr(value, 'strftime'):  # Si c'est un objet date ou datetime
                        form_data[key] = value.strftime('%Y-%m-%d')
                    else:
                        form_data[key] = value
                
                request.session['conditions_data'] = form_data
                request.session['creation_compte_etape'] = 5
                return redirect('fleet_app:creation_compte')
        else:
            form = ConditionsForm()
        
        return render(request, 'fleet_app/accounts/creation_compte_etape4.html', {
            'form': form,
            'etape': etape,
            'titre': "Conditions d'utilisation"
        })
    
    elif etape == 5:
        # Étape 5: Récapitulatif et confirmation
        type_compte = request.session.get('type_compte')
        form_specifique_data = request.session.get('form_specifique_data', {})
        form_profil_data = request.session.get('form_profil_data', {})
        conditions_data = request.session.get('conditions_data', {})
        has_file_upload = request.session.get('has_file_upload', False)
        
        # Si l'utilisateur a téléversé un fichier à l'étape 2, nous devons lui demander de le téléverser à nouveau
        # car nous ne pouvons pas stocker les fichiers dans la session
        if has_file_upload and 'photo' not in request.FILES and 'logo' not in request.FILES and request.method != 'POST':
            messages.warning(request, "Veuillez téléverser à nouveau votre photo/logo pour finaliser la création du compte.")
            # Afficher un formulaire pour téléverser à nouveau le fichier
            if type_compte == 'personne':
                return render(request, 'fleet_app/accounts/creation_compte_etape5_upload.html', {
                    'etape': 5,
                    'type_fichier': 'photo',
                    'nom_fichier': form_specifique_data.get('photo_name', ''),
                })
            else:  # type_compte == 'entreprise'
                return render(request, 'fleet_app/accounts/creation_compte_etape5_upload.html', {
                    'etape': 5,
                    'type_fichier': 'logo',
                    'nom_fichier': form_specifique_data.get('logo_name', ''),
                })
        
        if request.method == 'POST':
            # Enregistrer toutes les données
            with transaction.atomic():
                # Créer ou mettre à jour le profil
                try:
                    profil = request.user.profil
                except Profil.DoesNotExist:
                    profil = Profil(user=request.user)
                
                # Mettre à jour les champs du profil
                profil.type_compte = type_compte
                profil.telephone = form_profil_data.get('telephone', '')
                profil.email = form_profil_data.get('email', '')
                profil.adresse = form_profil_data.get('adresse', '')
                profil.role = form_profil_data.get('role', '')
                profil.conditions_acceptees = conditions_data.get('conditions_acceptees', False)
                profil.informations_certifiees = conditions_data.get('informations_certifiees', False)
                profil.compte_complete = True
                profil.save()
                
                # Créer l'objet spécifique selon le type de compte
                if type_compte == 'personne':
                    # Récupérer la date de naissance et la convertir si c'est une chaîne
                    date_naissance = form_specifique_data.get('date_naissance')
                    if isinstance(date_naissance, str) and date_naissance:
                        from datetime import datetime
                        try:
                            date_naissance = datetime.strptime(date_naissance, '%Y-%m-%d').date()
                        except ValueError:
                            # En cas d'erreur de conversion, utiliser None
                            date_naissance = None
                    
                    personne = PersonnePhysique(
                        profil=profil,
                        nom_prenom=form_specifique_data.get('nom_prenom', ''),
                        date_naissance=date_naissance,
                    )
                    # Gérer la photo de profil
                    if 'photo' in request.FILES:
                        # Si l'utilisateur a téléversé une nouvelle photo à l'étape 5
                        personne.photo = request.FILES['photo']
                    personne.save()
                else:  # type_compte == 'entreprise'
                    entreprise = Entreprise(
                        profil=profil,
                        nom_entreprise=form_specifique_data.get('nom_entreprise', ''),
                        forme_juridique=form_specifique_data.get('forme_juridique', ''),
                        nom_responsable=form_specifique_data.get('nom_responsable', ''),
                        rccm_nif=form_specifique_data.get('rccm_nif', ''),
                    )
                    # Gérer le logo de l'entreprise
                    if 'logo' in request.FILES:
                        # Si l'utilisateur a téléversé un nouveau logo à l'étape 5
                        entreprise.logo = request.FILES['logo']
                    entreprise.save()
                
                # Nettoyer la session
                for key in ['creation_compte_etape', 'type_compte', 'form_specifique_data', 'form_profil_data', 'conditions_data']:
                    if key in request.session:
                        del request.session[key]
                
                # Envoyer un email de confirmation
                try:
                    # Préparer les données pour l'email
                    email_context = {
                        'username': request.user.username,
                        'type_compte': 'Personne physique' if type_compte == 'personne' else 'Entreprise',
                        'nom': form_specifique_data.get('nom_prenom', '') if type_compte == 'personne' else form_specifique_data.get('nom_entreprise', ''),
                        'email': form_profil_data.get('email', ''),
                        'telephone': form_profil_data.get('telephone', ''),
                        'date_creation': profil.date_creation.strftime('%d/%m/%Y à %H:%M'),
                    }
                    
                    # Générer le contenu HTML de l'email
                    html_message = render_to_string('fleet_app/accounts/email_confirmation.html', email_context)
                    plain_message = strip_tags(html_message)
                    
                    # Envoyer l'email
                    send_mail(
                        subject='Confirmation de création de compte - Gestion de Parc',
                        message=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[form_profil_data.get('email', '')],
                        html_message=html_message,
                        fail_silently=True,
                    )
                    
                    messages.success(request, "Votre compte a été créé avec succès ! Un email de confirmation vous a été envoyé.")
                except Exception as e:
                    # En cas d'erreur lors de l'envoi de l'email, on continue quand même
                    messages.success(request, "Votre compte a été créé avec succès !")
                    messages.warning(request, "L'email de confirmation n'a pas pu être envoyé. Veuillez vérifier votre adresse email.")
                
                # Redirection vers la page d'accueil au lieu du tableau de bord
                return redirect('fleet_app:home')
        
        # Préparer les données pour l'affichage du récapitulatif
        context = {
            'etape': etape,
            'titre': "Récapitulatif et confirmation",
            'type_compte': type_compte,
            'form_specifique_data': form_specifique_data,
            'form_profil_data': form_profil_data,
            'conditions_data': conditions_data,
        }
        
        return render(request, 'fleet_app/accounts/creation_compte_etape5.html', context)
    
    # Si l'étape n'est pas valide, recommencer depuis le début
    request.session['creation_compte_etape'] = 1
    return redirect('fleet_app:creation_compte')


@login_required
def reinitialiser_creation_compte(request):
    """Réinitialise le processus de création de compte"""
    for key in ['creation_compte_etape', 'type_compte', 'form_specifique_data', 'form_profil_data', 'conditions_data']:
        if key in request.session:
            del request.session[key]
    
    messages.info(request, "Le processus de création de compte a été réinitialisé.")
    return redirect('fleet_app:creation_compte')


@login_required
def retour_etape(request, etape):
    """Permet de revenir à une étape spécifique du processus de création de compte"""
    # Vérifier que l'étape demandée est valide (entre 1 et 4)
    if etape < 1 or etape > 4:
        messages.error(request, "Étape invalide.")
        return redirect('fleet_app:creation_compte')
    
    # Vérifier que l'utilisateur a déjà commencé le processus
    if 'creation_compte_etape' not in request.session:
        messages.error(request, "Vous n'avez pas encore commencé le processus de création de compte.")
        return redirect('fleet_app:creation_compte')
    
    # Mettre à jour l'étape dans la session
    request.session['creation_compte_etape'] = etape
    
    # Message de confirmation
    messages.info(request, f"Vous êtes revenu à l'étape {etape}.")
    
    return redirect('fleet_app:creation_compte')
