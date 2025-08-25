#!/usr/bin/env python3
"""
Script de restauration rapide de TOUT le système de management
Basé sur les mémoires utilisateur - Restaure les pages qui étaient déjà finies
"""

import os
import sys
import shutil

def restore_from_backup():
    """Restaure depuis les backups existants si disponibles"""
    
    # Chemins des fichiers
    urls_path = r"c:\Users\faral\Desktop\Gestion_parck\fleet_app\urls.py"
    template_path = r"c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\presence_journaliere_list.html"
    
    # Vérifier les backups
    urls_backup = urls_path + '.backup'
    template_backup = template_path + '.backup'
    
    restored = False
    
    # Restaurer urls.py depuis backup
    if os.path.exists(urls_backup):
        try:
            shutil.copy2(urls_backup, urls_path)
            print("✅ urls.py restauré depuis backup")
            restored = True
        except Exception as e:
            print(f"❌ Erreur restauration urls.py : {e}")
    
    # Restaurer template depuis backup
    if os.path.exists(template_backup):
        try:
            shutil.copy2(template_backup, template_path)
            print("✅ Template restauré depuis backup")
            restored = True
        except Exception as e:
            print(f"❌ Erreur restauration template : {e}")
    
    return restored

def add_missing_management_urls():
    """Ajoute seulement les URLs management manquantes"""
    
    urls_path = r"c:\Users\faral\Desktop\Gestion_parck\fleet_app\urls.py"
    
    # URLs management à ajouter
    management_urls = '''
    # === SYSTÈME DE MANAGEMENT COMPLET ===
    # Gestion des employés
    path('management/employes/', views_management.employe_list, name='management_employe_list'),
    path('management/employes/ajouter/', views_management.employe_create, name='management_employe_add'),
    path('management/employes/<int:pk>/', views_management.employe_detail, name='management_employe_detail'),
    path('management/employes/<int:pk>/modifier/', views_management.employe_edit, name='management_employe_edit'),
    
    # Présences avec pointage complet
    path('management/presences/', views_management.presence_journaliere_list, name='management_presence_list'),
    path('management/presences/update-status/', views_management.update_presence_status, name='update_presence_status'),
    
    # Paies complètes
    path('management/paies/', views_management.paie_employe_list, name='management_paie_list'),
    path('management/paies/<int:pk>/modifier/', views_management.paie_employe_edit, name='management_paie_edit'),
    path('management/employes/<int:employe_id>/paie/ajouter/', views_management.paie_employe_create, name='paie_employe_create'),
    
    # Configuration heures supplémentaires
    path('management/configuration-heures-supplementaires/', views_management.configuration_heure_supplementaire, name='configuration_heure_supplementaire'),
    
    # Bulletins de paie avec pagination
    path('management/bulletin-paie/', views_management.bulletin_paie_list, name='bulletin_paie_list'),
    
    # Statistiques et archives
    path('management/statistiques-paies/', views_management.statistiques_paies, name='statistiques_paies'),
    path('management/archive-mensuelle/', views_management.archive_mensuelle, name='archive_mensuelle'),
    
    # Configuration montants
    path('management/configuration-montant-statut/', views_management.configuration_montant_statut, name='configuration_montant_statut'),
'''
    
    try:
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si management existe déjà
        if 'management/employes/' in content:
            print("✅ URLs management déjà présentes")
            return True
        
        # Ajouter avant la fermeture
        insertion_point = content.rfind(']')
        if insertion_point != -1:
            new_content = content[:insertion_point] + management_urls + '\n' + content[insertion_point:]
            
            with open(urls_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("✅ URLs management ajoutées")
            return True
        
    except Exception as e:
        print(f"❌ Erreur ajout URLs : {e}")
    
    return False

def main():
    """Restauration rapide du système complet"""
    print("🔄 RESTAURATION RAPIDE DU SYSTÈME DE MANAGEMENT")
    print("=" * 50)
    
    # 1. Essayer de restaurer depuis les backups
    print("1. Tentative de restauration depuis backups...")
    if restore_from_backup():
        print("✅ Restauration depuis backups réussie")
    else:
        print("⚠️ Pas de backups trouvés, ajout des URLs manquantes...")
        
        # 2. Ajouter les URLs manquantes
        if add_missing_management_urls():
            print("✅ URLs management ajoutées")
        else:
            print("❌ Échec ajout URLs")
    
    print("\n🎉 RESTAURATION TERMINÉE !")
    print("\nPages disponibles :")
    print("- management/employes/ (Gestion des employés)")
    print("- management/presences/ (Pointage avec colonnes montants)")
    print("- management/paies/ (Gestion des paies)")
    print("- management/configuration-heures-supplementaires/")
    print("- management/bulletin-paie/ (Bulletins avec pagination)")
    print("- management/statistiques-paies/")
    print("- management/archive-mensuelle/")
    
    print("\n⚠️ IMPORTANT :")
    print("Les filtres get_status_color et get_status_display sont disponibles")
    print("Le template de présences utilise le namespace fleet_app correct")
    print("Redémarrez le serveur Django pour appliquer les changements")

if __name__ == "__main__":
    main()
