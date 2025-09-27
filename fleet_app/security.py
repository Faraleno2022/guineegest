from functools import wraps
from django.http import HttpResponseForbidden, Http404
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied

def user_owns_data(model_class, pk_url_kwarg='pk', owner_field=None, relation_path=None):
    """
    Décorateur qui vérifie que l'utilisateur connecté est bien le propriétaire 
    des données qu'il essaie d'accéder.
    
    Paramètres:
    - model_class: La classe du modèle à vérifier
    - pk_url_kwarg: Le nom du paramètre d'URL contenant l'ID de l'objet (par défaut 'pk')
    - owner_field: DÉPRÉCIÉ - Le nom du champ qui relie l'objet à l'utilisateur (par défaut 'user')
    - relation_path: Liste des attributs à suivre pour atteindre l'utilisateur propriétaire
      Par exemple: ['user'] signifie obj.user
    
    Exemple d'utilisation:
    @login_required
    @user_owns_data(Profil, relation_path=['user'])
    def vue_profil(request, pk):
        profil = get_object_or_404(Profil, pk=pk)
        return render(request, 'template.html', {'profil': profil})
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Récupérer l'ID de l'objet depuis les paramètres d'URL
            pk = kwargs.get(pk_url_kwarg)
            if pk:
                # Récupérer l'objet
                obj = get_object_or_404(model_class, pk=pk)
                
                # Pour la rétrocompatibilité, si owner_field est spécifié mais pas relation_path
                if owner_field and not relation_path:
                    # Vérifier si l'utilisateur est le propriétaire
                    owner = getattr(obj, owner_field)
                    
                    # Si owner est un objet avec un attribut 'user' (comme un Profil)
                    if hasattr(owner, 'user'):
                        owner = owner.user
                else:
                    # Suivre le chemin de relation pour trouver l'utilisateur propriétaire
                    owner = obj
                    if relation_path:
                        for attr in relation_path:
                            if hasattr(owner, attr):
                                owner = getattr(owner, attr)
                            else:
                                # Si un attribut n'existe pas, on considère que l'utilisateur n'est pas propriétaire
                                messages.error(request, "Vous n'êtes pas autorisé à accéder à ces données.")
                                return redirect('fleet_app:home')
                
                if owner != request.user:
                    messages.error(request, "Vous n'êtes pas autorisé à accéder à ces données.")
                    return redirect('fleet_app:home')
            
            # Si tout est OK, exécuter la vue normalement
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def require_user_ownership(model_class, pk_url_kwarg='pk', user_field='user'):
    """
    Décorateur strict qui vérifie que l'utilisateur connecté possède l'objet.
    Lève une exception 404 si l'objet n'appartient pas à l'utilisateur.
    
    Paramètres:
    - model_class: La classe du modèle à vérifier
    - pk_url_kwarg: Le nom du paramètre d'URL contenant l'ID de l'objet
    - user_field: Le nom du champ qui relie l'objet à l'utilisateur
    
    Exemple d'utilisation:
    @login_required
    @require_user_ownership(Vehicule)
    def vehicule_edit(request, pk):
        vehicule = get_object_or_404(Vehicule, pk=pk)  # Déjà filtré par utilisateur
        # ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            pk = kwargs.get(pk_url_kwarg)
            if pk:
                # Vérifier que l'objet existe ET appartient à l'utilisateur
                try:
                    filter_kwargs = {pk_url_kwarg: pk, user_field: request.user}
                    obj = model_class.objects.get(**filter_kwargs)
                except model_class.DoesNotExist:
                    # L'objet n'existe pas ou n'appartient pas à l'utilisateur
                    raise Http404(f"{model_class.__name__} non trouvé")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def get_user_object_or_404(model_class, user, **kwargs):
    """
    Version sécurisée de get_object_or_404 qui filtre automatiquement par utilisateur.
    
    Paramètres:
    - model_class: La classe du modèle
    - user: L'utilisateur connecté
    - **kwargs: Les critères de filtrage supplémentaires
    
    Retourne l'objet s'il appartient à l'utilisateur, sinon lève Http404.
    """
    kwargs['user'] = user
    return get_object_or_404(model_class, **kwargs)


def user_owns_related_data(model_class, pk_url_kwarg='pk', relation_path=None):
    """
    Décorateur qui vérifie que l'utilisateur connecté est bien le propriétaire 
    des données reliées qu'il essaie d'accéder.
    
    Paramètres:
    - model_class: La classe du modèle à vérifier
    - pk_url_kwarg: Le nom du paramètre d'URL contenant l'ID de l'objet (par défaut 'pk')
    - relation_path: Liste des attributs à suivre pour atteindre l'utilisateur propriétaire
      Par exemple: ['profil', 'user'] signifie obj.profil.user
    
    Exemple d'utilisation:
    @login_required
    @user_owns_related_data(Entreprise, relation_path=['profil', 'user'])
    def vue_entreprise(request, pk):
        entreprise = get_object_or_404(Entreprise, pk=pk)
        return render(request, 'template.html', {'entreprise': entreprise})
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Récupérer l'ID de l'objet depuis les paramètres d'URL
            pk = kwargs.get(pk_url_kwarg)
            if pk:
                # Récupérer l'objet
                obj = get_object_or_404(model_class, pk=pk)
                
                # Suivre le chemin de relation pour trouver l'utilisateur propriétaire
                owner = obj
                if relation_path:
                    for attr in relation_path:
                        if hasattr(owner, attr):
                            owner = getattr(owner, attr)
                        else:
                            # Si un attribut n'existe pas, on considère que l'utilisateur n'est pas propriétaire
                            messages.error(request, "Vous n'êtes pas autorisé à accéder à ces données.")
                            return redirect('fleet_app:home')
                
                # Vérifier si l'utilisateur final est le propriétaire
                if owner != request.user:
                    messages.error(request, "Vous n'êtes pas autorisé à accéder à ces données.")
                    return redirect('fleet_app:home')
            
            # Si tout est OK, exécuter la vue normalement
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
