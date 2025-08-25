@login_required
def employe_list(request):
    """
    Vue pour afficher la liste des employés
    Filtrée pour n'afficher que les employés de l'utilisateur connecté
    """
    employes = Employe.objects.filter(user=request.user).order_by('matricule')
    
    context = {
        'employes': employes,
        'total_employes': employes.count(),
    }
    
    return render(request, 'fleet_app/entreprise/employe_list.html', context)
