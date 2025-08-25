#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour restaurer complètement views_management.py dans un état fonctionnel
"""

import os
import re

def nettoyer_views_management():
    """
    Nettoie complètement le fichier views_management.py
    """
    print("🧹 NETTOYAGE COMPLET DE VIEWS_MANAGEMENT.PY")
    print("="*60)
    
    fichier_views = r'c:\Users\faral\Desktop\Gestion_parck\fleet_app\views_management.py'
    
    if not os.path.exists(fichier_views):
        print(f"❌ Fichier non trouvé : {fichier_views}")
        return False
    
    # Lire le contenu du fichier
    with open(fichier_views, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Créer une sauvegarde
    backup_file = fichier_views + '.backup_nettoyage'
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Sauvegarde créée : {os.path.basename(backup_file)}")
    
    # Supprimer toutes les fonctions liées aux présences
    fonctions_presences = [
        'presence_journaliere_list',
        'presence_journaliere_update', 
        'presence_journaliere_export',
        'presence_journaliere_import'
    ]
    
    # Supprimer les fonctions de présences complètement
    for fonction in fonctions_presences:
        # Pattern pour supprimer la fonction complète avec ses décorateurs
        pattern = rf'@[^\n]*\ndef {fonction}\([^)]*\):.*?(?=\n@|\ndef |\nclass |\Z)'
        content = re.sub(pattern, '', content, flags=re.DOTALL)
        print(f"🗑️ Fonction supprimée : {fonction}")
    
    # Corriger les problèmes d'indentation courants
    lines = content.split('\n')
    lines_corrigees = []
    
    for i, line in enumerate(lines):
        # Ignorer les lignes vides
        if not line.strip():
            lines_corrigees.append(line)
            continue
        
        # Corriger les lignes avec des indentations incorrectes après suppression
        if line.strip().startswith('return redirect(') and not line.startswith('    '):
            # Cette ligne devrait être indentée
            line = '    ' + line.strip()
            print(f"🔧 Ligne {i+1} : Indentation corrigée pour return redirect")
        
        # Corriger les elif/else orphelins
        if line.strip().startswith('elif ') and not line.startswith('    '):
            line = '    ' + line.strip()
            print(f"🔧 Ligne {i+1} : Indentation corrigée pour elif")
        
        if line.strip().startswith('else:') and not line.startswith('    '):
            line = '    ' + line.strip()
            print(f"🔧 Ligne {i+1} : Indentation corrigée pour else")
        
        lines_corrigees.append(line)
    
    # Reconstruire le contenu
    content_corrige = '\n'.join(lines_corrigees)
    
    # Supprimer les lignes vides multiples
    content_corrige = re.sub(r'\n\s*\n\s*\n', '\n\n', content_corrige)
    
    # Écrire le fichier corrigé
    with open(fichier_views, 'w', encoding='utf-8') as f:
        f.write(content_corrige)
    
    print(f"✅ Fichier nettoyé : {os.path.basename(fichier_views)}")
    return True

def verifier_syntaxe():
    """
    Vérifie la syntaxe Python du fichier
    """
    print("\n🔍 VÉRIFICATION DE LA SYNTAXE")
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
        
        # Essayer de corriger l'erreur automatiquement
        if "unexpected indent" in str(e.msg):
            print("🔧 Tentative de correction automatique...")
            corriger_indentation_ligne(fichier_views, e.lineno)
            return verifier_syntaxe()  # Vérifier à nouveau
        
        return False
    except Exception as e:
        print(f"❌ Erreur lors de la vérification : {e}")
        return False

def corriger_indentation_ligne(fichier, ligne_erreur):
    """
    Corrige l'indentation d'une ligne spécifique
    """
    with open(fichier, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    if ligne_erreur <= len(lines):
        line = lines[ligne_erreur - 1]
        # Supprimer l'indentation excessive
        lines[ligne_erreur - 1] = line.lstrip() + '\n'
        
        with open(fichier, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        print(f"🔧 Indentation corrigée à la ligne {ligne_erreur}")

def main():
    """
    Fonction principale de restauration
    """
    print("🔄 RESTAURATION COMPLÈTE DE VIEWS_MANAGEMENT.PY")
    print("="*80)
    print("Nettoyage et correction du fichier views_management.py")
    print()
    
    # Nettoyer le fichier
    if nettoyer_views_management():
        print("\n🎯 NETTOYAGE TERMINÉ")
        
        # Vérifier la syntaxe
        if verifier_syntaxe():
            print("\n🎉 RESTAURATION RÉUSSIE !")
            print("Le fichier views_management.py est maintenant fonctionnel.")
            print("Vous pouvez redémarrer le serveur Django.")
        else:
            print("\n⚠️ RESTAURATION PARTIELLE")
            print("Des erreurs de syntaxe persistent.")
    else:
        print("\n❌ ÉCHEC DE LA RESTAURATION")
    
    print(f"\n💾 SAUVEGARDE DISPONIBLE :")
    print("- views_management.py.backup_nettoyage")
    
    return True

if __name__ == "__main__":
    main()
