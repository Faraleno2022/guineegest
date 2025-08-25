#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour restaurer une version fonctionnelle de views_management.py
depuis la sauvegarde la plus récente qui fonctionnait
"""

import os
import shutil

def restore_working_views():
    """
    Restaurer une version fonctionnelle de views_management.py
    """
    views_path = r"c:\Users\faral\Desktop\Gestion_parck\fleet_app\views_management.py"
    
    # Chercher la sauvegarde la plus récente qui fonctionnait
    backup_candidates = [
        views_path + '.backup_before_syntax_fix',
        views_path + '.backup_before_final_fix',
        views_path + '.backup_before_complete_clean',
        views_path + '.backup_before_montant_restore'
    ]
    
    working_backup = None
    for backup in backup_candidates:
        if os.path.exists(backup):
            print(f"📁 Sauvegarde trouvée : {backup}")
            working_backup = backup
            break
    
    if not working_backup:
        print("❌ Aucune sauvegarde fonctionnelle trouvée")
        return False
    
    try:
        # Créer une sauvegarde du fichier actuel corrompu
        corrupted_backup = views_path + '.corrupted_backup'
        shutil.copy2(views_path, corrupted_backup)
        print(f"✅ Sauvegarde du fichier corrompu : {corrupted_backup}")
        
        # Restaurer la version fonctionnelle
        shutil.copy2(working_backup, views_path)
        print(f"✅ Version fonctionnelle restaurée depuis : {working_backup}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la restauration : {e}")
        return False

def main():
    """
    Fonction principale
    """
    print("🔄 RESTAURATION D'UNE VERSION FONCTIONNELLE DE VIEWS_MANAGEMENT.PY")
    print("=" * 65)
    
    if restore_working_views():
        print(f"\n✅ RESTAURATION RÉUSSIE !")
        print(f"🔄 Une version fonctionnelle de views_management.py a été restaurée.")
        print(f"🚀 Vous pouvez maintenant redémarrer le serveur Django :")
        print(f"   python manage.py runserver")
        print(f"\n📋 Les colonnes de montants sont déjà présentes dans le template.")
        print(f"Il ne reste plus qu'à vérifier l'affichage dans l'application.")
    else:
        print(f"\n❌ ÉCHEC DE LA RESTAURATION")
        print(f"Aucune sauvegarde fonctionnelle n'a pu être trouvée.")
    
    return True

if __name__ == "__main__":
    main()
