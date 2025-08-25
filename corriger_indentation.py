#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour corriger les erreurs d'indentation dans views_management.py
"""

import os
import re

def corriger_indentation_views_management():
    """
    Corrige les erreurs d'indentation dans views_management.py
    """
    print("🔧 CORRECTION DES ERREURS D'INDENTATION")
    print("="*60)
    
    fichier_views = r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\views_management.py'
    
    if not os.path.exists(fichier_views):
        print(f"❌ Fichier non trouvé : {fichier_views}")
        return False
    
    # Lire le contenu du fichier
    with open(fichier_views, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_file = fichier_views + '.backup_indentation'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Sauvegarde créée : {os.path.basename(backup_file)}")
    
    # Corrections spécifiques des erreurs d'indentation
    corrections = [
        # Corriger les lignes orphelines mal indentées
        (r'(\n    employes = Employe\.objects\.filter\(user=request\.user\)\.order_by\(\'matricule\'\))\n\s+\n\s+return redirect\(\'fleet_app:parametre_paie_list\'\)\n\s+\n\s+# Si le formulaire concerne la suppression', 
         r'\1\n    \n    # Si le formulaire concerne la suppression'),
        
        # Corriger la boucle for orpheline
        (r'(\n\s+for employe in employes:\s*)\n(\s+context = \{)',
         r'\1\n        pass  # Placeholder pour la boucle\n    \n\2'),
        
        # Corriger les elif mal indentés
        (r'(\n\s+return redirect\(\'fleet_app:parametre_paie_list\'\))\n\s+\n\s+# Si le formulaire concerne la modification d\'un employé spécifique\n\s+elif \'modifier_employe\' in request\.POST',
         r'\1\n    \n    # Si le formulaire concerne la modification d\'un employé spécifique\n    elif request.method == \'POST\' and \'modifier_employe\' in request.POST'),
        
        # Corriger les blocs try/except mal indentés
        (r'(\n\s+elif request\.method == \'POST\' and \'modifier_employe\' in request\.POST and \'employe_id\' in request\.POST:)\n\s+employe_id = request\.POST\.get\(\'employe_id\'\)\n\s+try:',
         r'\1\n        employe_id = request.POST.get(\'employe_id\')\n        try:'),
        
        # Corriger les else orphelins
        (r'(\n\s+except [^:]+:)\n\s+([^:]+)\n\s+else:',
         r'\1\n            \2\n        else:'),
    ]
    
    # Appliquer les corrections
    content_corrige = content
    corrections_appliquees = 0
    
    for pattern, replacement in corrections:
        if re.search(pattern, content_corrige, re.MULTILINE):
            content_corrige = re.sub(pattern, replacement, content_corrige, flags=re.MULTILINE)
            corrections_appliquees += 1
            print(f"✅ Correction appliquée : {corrections_appliquees}")
    
    # Corrections générales d'indentation
    lines = content_corrige.split('\n')
    lines_corrigees = []
    
    for i, line in enumerate(lines):
        # Corriger les lignes avec des indentations incorrectes
        if line.strip():
            # Si la ligne précédente se termine par ':' et la ligne actuelle n'est pas indentée
            if i > 0 and lines[i-1].strip().endswith(':') and line.strip() and not line.startswith('    '):
                if not line.startswith('#') and not line.startswith('def ') and not line.startswith('class '):
                    # Ajouter une indentation de base
                    line = '    ' + line.strip()
                    print(f"🔧 Ligne {i+1} : Indentation ajoutée")
        
        lines_corrigees.append(line)
    
    content_final = '\n'.join(lines_corrigees)
    
    # Écrire le fichier corrigé
    with open(fichier_views, 'w', encoding='utf-8') as f:
        f.write(content_final)
    
    print(f"✅ Fichier corrigé : {os.path.basename(fichier_views)}")
    print(f"📊 Corrections appliquées : {corrections_appliquees}")
    
    return True

def verifier_syntaxe_python():
    """
    Vérifie la syntaxe Python du fichier corrigé
    """
    print("\n🔍 VÉRIFICATION DE LA SYNTAXE PYTHON")
    print("="*60)
    
    fichier_views = r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\views_management.py'
    
    try:
        with open(fichier_views, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tenter de compiler le code Python
        compile(content, fichier_views, 'exec')
        print("✅ Syntaxe Python valide !")
        return True
        
    except SyntaxError as e:
        print(f"❌ Erreur de syntaxe détectée :")
        print(f"   Ligne {e.lineno}: {e.text}")
        print(f"   Erreur: {e.msg}")
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        return False

def main():
    """
    Fonction principale de correction
    """
    print("🔧 CORRECTION COMPLÈTE DES ERREURS D'INDENTATION")
    print("="*80)
    print("Correction du fichier views_management.py endommagé par les suppressions automatiques")
    print()
    
    # Corriger les erreurs d'indentation
    if corriger_indentation_views_management():
        print("\n🎯 CORRECTION TERMINÉE")
        
        # Vérifier la syntaxe
        if verifier_syntaxe_python():
            print("\n🎉 SUCCÈS COMPLET !")
            print("Le fichier views_management.py a été corrigé avec succès.")
            print("Vous pouvez maintenant redémarrer le serveur Django.")
        else:
            print("\n⚠️ CORRECTION PARTIELLE")
            print("Des erreurs de syntaxe persistent. Vérification manuelle nécessaire.")
    else:
        print("\n❌ ÉCHEC DE LA CORRECTION")
        print("Impossible de corriger le fichier automatiquement.")
    
    print(f"\n💾 SAUVEGARDE DISPONIBLE :")
    print("- views_management.py.backup_indentation")
    
    return True

if __name__ == "__main__":
    main()
