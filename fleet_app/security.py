from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect

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
