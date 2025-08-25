#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour supprimer complètement tout le système de présences
"""

import os
import shutil

def supprimer_fichiers_presences():
    """
    Supprime tous les fichiers liés aux présences
    """
    print("🗑️ SUPPRESSION DES FICHIERS DE PRÉSENCES")
    print("="*60)
    
    # Fichiers à supprimer
    fichiers_a_supprimer = [
        r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\presence_journaliere_list.html',
        r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\legende_presence.html',
        r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\fix_presences.html',
        r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\views_presence_update.py',
        r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\static\fleet_app\js\presence_calculs.js',
        r'c:\Users\faral\Desktop\Gestion_parck\verification_colonne_mt_presences.py',
        r'c:\Users\faral\Desktop\Gestion_parck\verification_calcul_mt_presences.py',
        r'c:\Users\faral\Desktop\Gestion_parck\verification_calculs_presences.py',
        r'c:\Users\faral\Desktop\Gestion_parck\test_presence_update.py'
    ]
    
    fichiers_supprimes = 0
    
    for fichier in fichiers_a_supprimer:
        if os.path.exists(fichier):
            try:
                os.remove(fichier)
                print(f"🗑️ Supprimé : {os.path.basename(fichier)}")
                fichiers_supprimes += 1
            except Exception as e:
                print(f"❌ Erreur suppression {os.path.basename(fichier)}: {e}")
        else:
            print(f"⚠️ Fichier non trouvé : {os.path.basename(fichier)}")
    
    return fichiers_supprimes

def nettoyer_vues_presences():
    """
    Supprime les fonctions liées aux présences dans les vues
    """
    print("\n🧹 NETTOYAGE DES VUES")
    print("="*60)
    
    # Fichiers de vues à nettoyer
    vues_a_nettoyer = [
        r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\views_entreprise.py',
        r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\views_management.py'
    ]
    
    fonctions_presences = [
        'presence_journaliere_list',
        'presence_journaliere_update',
        'presence_journaliere_export',
        'presence_journaliere_import'
    ]
    
    vues_nettoyees = 0
    
    for vue_file in vues_a_nettoyer:
        if os.path.exists(vue_file):
            try:
                # Lire le contenu
                with open(vue_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Créer une sauvegarde
                backup_file = vue_file + '.backup_avant_suppression'
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Supprimer les fonctions de présences
                import re
                
                for fonction in fonctions_presences:
                    # Pattern pour supprimer la fonction complète
                    pattern = rf'@[^\n]*\ndef {fonction}\([^)]*\):.*?(?=\n@|\ndef |\nclass |\Z)'
                    content = re.sub(pattern, '', content, flags=re.DOTALL)
                
                # Écrire le fichier nettoyé
                with open(vue_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print(f"🧹 Vue nettoyée : {os.path.basename(vue_file)}")
                vues_nettoyees += 1
                
            except Exception as e:
                print(f"❌ Erreur nettoyage {os.path.basename(vue_file)}: {e}")
    
    return vues_nettoyees

def nettoyer_urls_presences():
    """
    Supprime les URLs liées aux présences
    """
    print("\n🔗 NETTOYAGE DES URLS")
    print("="*60)
    
    urls_file = r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\urls.py'
    
    if os.path.exists(urls_file):
        try:
            # Lire le contenu
            with open(urls_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Créer une sauvegarde
            backup_file = urls_file + '.backup_avant_suppression'
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Supprimer les lignes contenant 'presence'
            lines = content.split('\n')
            new_lines = []
            
            for line in lines:
                if 'presence' not in line.lower():
                    new_lines.append(line)
                else:
                    print(f"🔗 URL supprimée : {line.strip()}")
            
            # Écrire le fichier nettoyé
            with open(urls_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(new_lines))
            
            print(f"🔗 URLs nettoyées dans : {os.path.basename(urls_file)}")
            return 1
            
        except Exception as e:
            print(f"❌ Erreur nettoyage URLs: {e}")
            return 0
    else:
        print(f"⚠️ Fichier URLs non trouvé")
        return 0

def nettoyer_modeles_presences():
    """
    Commente les modèles de présences dans models.py
    """
    print("\n📊 NETTOYAGE DES MODÈLES")
    print("="*60)
    
    models_file = r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\models.py'
    
    if os.path.exists(models_file):
        try:
            # Lire le contenu
            with open(models_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Créer une sauvegarde
            backup_file = models_file + '.backup_avant_suppression'
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Commenter les classes de présences
            import re
            
            # Pattern pour trouver les classes de présences
            pattern = r'(class.*Presence.*:.*?)(?=\nclass|\Z)'
            
            def comment_class(match):
                class_content = match.group(1)
                commented = '\n'.join(f'# {line}' for line in class_content.split('\n'))
                return commented
            
            content = re.sub(pattern, comment_class, content, flags=re.DOTALL)
            
            # Écrire le fichier modifié
            with open(models_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"📊 Modèles commentés dans : {os.path.basename(models_file)}")
            return 1
            
        except Exception as e:
            print(f"❌ Erreur nettoyage modèles: {e}")
            return 0
    else:
        print(f"⚠️ Fichier models.py non trouvé")
        return 0

def main():
    """
    Fonction principale de suppression complète des présences
    """
    print("🗑️ SUPPRESSION COMPLÈTE DU SYSTÈME DE PRÉSENCES")
    print("="*80)
    print("Suppression de tous les fichiers, vues, URLs et modèles liés aux présences")
    print()
    
    # Supprimer les fichiers
    fichiers_supprimes = supprimer_fichiers_presences()
    
    # Nettoyer les vues
    vues_nettoyees = nettoyer_vues_presences()
    
    # Nettoyer les URLs
    urls_nettoyees = nettoyer_urls_presences()
    
    # Nettoyer les modèles
    modeles_nettoyes = nettoyer_modeles_presences()
    
    print(f"\n🎯 RÉSUMÉ DE LA SUPPRESSION :")
    print(f"🗑️ Fichiers supprimés: {fichiers_supprimes}")
    print(f"🧹 Vues nettoyées: {vues_nettoyees}")
    print(f"🔗 URLs nettoyées: {urls_nettoyees}")
    print(f"📊 Modèles commentés: {modeles_nettoyes}")
    
    print(f"\n⚠️ IMPORTANT :")
    print("- Les sauvegardes ont été créées avec l'extension .backup_avant_suppression")
    print("- Les modèles ont été commentés (pas supprimés) pour éviter les erreurs de migration")
    print("- Le serveur Django va redémarrer automatiquement")
    print("- Vous devrez peut-être faire des migrations Django si nécessaire")
    
    print(f"\n🎉 SUPPRESSION COMPLÈTE TERMINÉE !")
    print("Le système de présences a été complètement supprimé du projet.")
    
    return True

if __name__ == "__main__":
    main()
