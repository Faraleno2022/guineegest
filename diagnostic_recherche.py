#!/usr/bin/env python3
"""
Script de diagnostic pour identifier pourquoi la recherche ne fonctionne pas
dans la page configuration-heures-supplementaires
"""

import os
import re

def diagnostic_recherche():
    print("🔍 DIAGNOSTIC DE LA RECHERCHE DYNAMIQUE")
    print("=" * 50)
    
    template_path = r"c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\configuration_heure_supplementaire.html"
    
    if not os.path.exists(template_path):
        print("❌ Fichier template non trouvé:", template_path)
        return
    
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("✅ Fichier template trouvé")
    
    # Vérifier les éléments HTML requis
    elements_requis = {
        'searchInput': r'id=["\']searchInput["\']',
        'clearSearch': r'id=["\']clearSearch["\']',
        'resultCount': r'id=["\']resultCount["\']',
        'visibleCount': r'id=["\']visibleCount["\']',
        'dataTable': r'id=["\']dataTable["\']'
    }
    
    print("\n📋 VÉRIFICATION DES ÉLÉMENTS HTML:")
    for element, pattern in elements_requis.items():
        if re.search(pattern, content):
            print(f"✅ {element} trouvé")
        else:
            print(f"❌ {element} MANQUANT")
    
    # Vérifier la fonction JavaScript
    print("\n🔧 VÉRIFICATION DU JAVASCRIPT:")
    
    if 'function initializeSearch()' in content:
        print("✅ Fonction initializeSearch() trouvée")
    else:
        print("❌ Fonction initializeSearch() MANQUANTE")
    
    if 'performDynamicSearch' in content:
        print("✅ Fonction performDynamicSearch trouvée")
    else:
        print("❌ Fonction performDynamicSearch MANQUANTE")
    
    # Vérifier les événements
    if "addEventListener('input'" in content:
        print("✅ Événement 'input' trouvé")
    else:
        print("❌ Événement 'input' MANQUANT")
    
    # Vérifier l'initialisation
    if 'document.addEventListener(\'DOMContentLoaded\', initializeSearch)' in content:
        print("✅ Initialisation DOMContentLoaded trouvée")
    else:
        print("❌ Initialisation DOMContentLoaded MANQUANTE")
    
    if '$(document).ready(function()' in content:
        print("✅ Initialisation jQuery ready trouvée")
    else:
        print("❌ Initialisation jQuery ready MANQUANTE")
    
    # Vérifier la structure du tableau
    print("\n📊 VÉRIFICATION DE LA STRUCTURE DU TABLEAU:")
    
    if '<table' in content and 'id="dataTable"' in content:
        print("✅ Tableau avec ID dataTable trouvé")
    else:
        print("❌ Tableau avec ID dataTable MANQUANT")
    
    if '<tbody>' in content:
        print("✅ Élément tbody trouvé")
    else:
        print("❌ Élément tbody MANQUANT")
    
    # Compter les lignes d'employés
    employe_rows = content.count('{% for employe in employes %}')
    print(f"📈 Nombre de boucles d'employés: {employe_rows}")
    
    # Vérifier les logs de débogage
    print("\n🐛 VÉRIFICATION DES LOGS DE DÉBOGAGE:")
    
    debug_logs = [
        'console.log(\'🚀 RECHERCHE DYNAMIQUE',
        'console.log(\'✅ Éléments trouvés',
        'console.log(\'🔍 Recherche dynamique pour:',
        'console.log(\'📈 Résultat dynamique:'
    ]
    
    for log in debug_logs:
        if log in content:
            print(f"✅ Log trouvé: {log[:30]}...")
        else:
            print(f"❌ Log manquant: {log[:30]}...")
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMANDATIONS:")
    
    # Analyser les problèmes potentiels
    problems = []
    
    if not re.search(r'id=["\']searchInput["\']', content):
        problems.append("- Ajouter l'ID 'searchInput' au champ de recherche")
    
    if not re.search(r'id=["\']dataTable["\']', content):
        problems.append("- Ajouter l'ID 'dataTable' au tableau")
    
    if 'function initializeSearch()' not in content:
        problems.append("- Ajouter la fonction initializeSearch()")
    
    if "addEventListener('input'" not in content:
        problems.append("- Ajouter les événements de recherche")
    
    if problems:
        print("❌ PROBLÈMES DÉTECTÉS:")
        for problem in problems:
            print(problem)
    else:
        print("✅ Tous les éléments semblent présents")
        print("💡 Le problème pourrait être:")
        print("- Erreur JavaScript dans la console")
        print("- Conflit avec d'autres scripts")
        print("- Problème de timing d'initialisation")
        print("- Cache du navigateur")
    
    print("\n🔧 ACTIONS SUGGÉRÉES:")
    print("1. Ouvrir la console du navigateur (F12)")
    print("2. Recharger la page")
    print("3. Vérifier les erreurs JavaScript")
    print("4. Tester la recherche et observer les logs")
    print("5. Vider le cache du navigateur si nécessaire")

if __name__ == "__main__":
    diagnostic_recherche()
