from fleet_app.models import Employe

# Modifier la méthode de tri des employés dans la vue
def update_employe_list_view():
    # Ouvrir le fichier
    with open('fleet_app/views_management.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remplacer la ligne de tri
    content = content.replace("employes = Employe.objects.filter(user=request.user).order_by('nom', 'prenom')", 
                             "employes = Employe.objects.filter(user=request.user).order_by('matricule')")
    
    # Écrire les modifications
    with open('fleet_app/views_management.py', 'w', encoding='utf-8') as file:
        file.write(content)
    
    print('Tri des employés modifié avec succès')

update_employe_list_view()
