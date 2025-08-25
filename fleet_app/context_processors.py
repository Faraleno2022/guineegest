from .models_alertes import Alerte

def alerts_count(request):
    """
    Contexte global pour fournir le nombre d'alertes actives à tous les templates.
    """
    if request.user.is_authenticated:
        count = Alerte.objects.filter(statut='Active').count()
        return {'alerts_count': count}
    return {'alerts_count': 0}
