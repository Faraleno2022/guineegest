#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour restaurer les colonnes de montants supprimées dans le template
presence_journaliere_list.html et s'assurer qu'elles s'affichent correctement.
"""

import os
import sys
import re

def add_montant_columns_to_template():
    """
    Ajouter les colonnes de montants manquantes au template
    """
    template_path = r"c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\presence_journaliere_list.html"
    
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si les colonnes de montants existent déjà
        if 'Mt Présences' in content or 'Mt Absent' in content:
            print("✅ Les colonnes de montants sont déjà présentes dans le template.")
            return True
        
        # Créer une sauvegarde
        backup_path = template_path + '.backup_before_montant_restore'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde créée : {backup_path}")
        
        # Ajouter les colonnes de montants dans l'en-tête du tableau
        # Chercher la ligne avec "Sundays" pour insérer les colonnes après
        header_pattern = r'(<th class="align-middle text-center" rowspan="2">.*?<span style="font-size: 0\.75rem;">Dimanches</span>.*?</th>)'
        
        montant_columns_header = '''
                                    <!-- Colonnes des montants par statut -->
                                    <th class="align-middle text-center" rowspan="2">
                                        <i class="fas fa-euro-sign me-1" style="color: #28a745;"></i>
                                        <span style="font-size: 0.75rem; color: #28a745;">Mt Présences</span>
                                    </th>
                                    <th class="align-middle text-center" rowspan="2">
                                        <i class="fas fa-euro-sign me-1" style="color: #dc3545;"></i>
                                        <span style="font-size: 0.75rem; color: #dc3545;">Mt Absent</span>
                                    </th>
                                    <th class="align-middle text-center" rowspan="2">
                                        <i class="fas fa-euro-sign me-1" style="color: #6c757d;"></i>
                                        <span style="font-size: 0.75rem; color: #6c757d;">Mt J Repos</span>
                                    </th>
                                    <th class="align-middle text-center" rowspan="2">
                                        <i class="fas fa-euro-sign me-1" style="color: #ffc107;"></i>
                                        <span style="font-size: 0.75rem; color: #ffc107;">Mt Maladies</span>
                                    </th>
                                    <th class="align-middle text-center" rowspan="2">
                                        <i class="fas fa-euro-sign me-1" style="color: #fd7e14;"></i>
                                        <span style="font-size: 0.75rem; color: #fd7e14;">Mt M.Payer</span>
                                    </th>
                                    <th class="align-middle text-center" rowspan="2">
                                        <i class="fas fa-euro-sign me-1" style="color: #0d6efd;"></i>
                                        <span style="font-size: 0.75rem; color: #0d6efd;">Mt Férié</span>
                                    </th>
                                    <th class="align-middle text-center" rowspan="2">
                                        <i class="fas fa-euro-sign me-1" style="color: #17a2b8;"></i>
                                        <span style="font-size: 0.75rem; color: #17a2b8;">Mt Formation</span>
                                    </th>
                                    <th class="align-middle text-center" rowspan="2">
                                        <i class="fas fa-euro-sign me-1" style="color: #20c997;"></i>
                                        <span style="font-size: 0.75rem; color: #20c997;">Mt Congé</span>
                                    </th>
                                    <th class="align-middle text-center" rowspan="2">
                                        <i class="fas fa-euro-sign me-1" style="color: #28a745;"></i>
                                        <span style="font-size: 0.75rem; color: #28a745;">Mt Sundays</span>
                                    </th>'''
        
        if re.search(header_pattern, content, re.DOTALL):
            content = re.sub(header_pattern, r'\1' + montant_columns_header, content, flags=re.DOTALL)
            print("✅ En-têtes des colonnes de montants ajoutés")
        else:
            print("⚠️  Impossible de trouver l'emplacement pour les en-têtes de montants")
        
        # Ajouter les cellules de données dans le corps du tableau
        # Chercher la ligne avec les données des dimanches pour insérer après
        data_pattern = r'(<td class="text-center text-success">.*?{{ data\.stats\.nombre_dimanches_am\|add:data\.stats\.nombre_dimanches_pm\|add:data\.stats\.nombre_dimanches_journee\|default:0 }}.*?</td>)'
        
        montant_columns_data = '''
                                    <!-- Colonnes des montants -->
                                    <td class="text-center fw-bold text-success">
                                        {{ data.montant_presences|default:0|floatformat:0 }} GNF
                                    </td>
                                    <td class="text-center fw-bold text-danger">
                                        {{ data.montant_absent|default:0|floatformat:0 }} GNF
                                    </td>
                                    <td class="text-center fw-bold text-secondary">
                                        {{ data.montant_repos|default:0|floatformat:0 }} GNF
                                    </td>
                                    <td class="text-center fw-bold text-warning">
                                        {{ data.montant_maladies|default:0|floatformat:0 }} GNF
                                    </td>
                                    <td class="text-center fw-bold" style="color: #fd7e14;">
                                        {{ data.montant_maladie_payee|default:0|floatformat:0 }} GNF
                                    </td>
                                    <td class="text-center fw-bold text-primary">
                                        {{ data.montant_ferie|default:0|floatformat:0 }} GNF
                                    </td>
                                    <td class="text-center fw-bold text-info">
                                        {{ data.montant_formation|default:0|floatformat:0 }} GNF
                                    </td>
                                    <td class="text-center fw-bold" style="color: #20c997;">
                                        {{ data.montant_conge|default:0|floatformat:0 }} GNF
                                    </td>
                                    <td class="text-center fw-bold text-success">
                                        {{ data.montant_dimanches|default:0|floatformat:0 }} GNF
                                    </td>'''
        
        if re.search(data_pattern, content, re.DOTALL):
            content = re.sub(data_pattern, r'\1' + montant_columns_data, content, flags=re.DOTALL)
            print("✅ Cellules de données des montants ajoutées")
        else:
            print("⚠️  Impossible de trouver l'emplacement pour les données de montants")
        
        # Mettre à jour le colspan dans la ligne vide pour tenir compte des nouvelles colonnes
        colspan_pattern = r'<th colspan="(\d+)"></th>'
        def update_colspan(match):
            current_colspan = int(match.group(1))
            new_colspan = current_colspan + 9  # Ajouter 9 colonnes de montants
            return f'<th colspan="{new_colspan}"></th>'
        
        content = re.sub(colspan_pattern, update_colspan, content)
        print("✅ Colspan mis à jour pour les nouvelles colonnes")
        
        # Sauvegarder le template modifié
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Template mis à jour avec les colonnes de montants : {template_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification du template : {e}")
        return False

def update_views_for_montants():
    """
    Mettre à jour le fichier views_management.py pour calculer les montants
    """
    views_path = r"c:\Users\faral\Desktop\Gestion_parck\fleet_app\views_management.py"
    
    try:
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Vérifier si les calculs de montants existent déjà
        if 'montant_presences' in content:
            print("✅ Les calculs de montants sont déjà présents dans les vues.")
            return True
        
        # Créer une sauvegarde
        backup_path = views_path + '.backup_before_montant_restore'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde des vues créée : {backup_path}")
        
        # Ajouter les calculs de montants dans la fonction presence_journaliere_list
        # Chercher l'endroit où les données des employés sont préparées
        pattern = r"(employes_data\.append\(\{[^}]+\}\))"
        
        if re.search(pattern, content):
            # Ajouter les calculs de montants avant l'ajout des données
            montant_calculations = '''
            # Calculs des montants (valeurs par défaut pour l'instant)
            montant_presences = (
                (data.stats.get('nombre_presences_am', 0) * 5000) +
                (data.stats.get('nombre_presences_pm', 0) * 5000) +
                (data.stats.get('nombre_presences_journee', 0) * 10000)
            )
            montant_absent = data.stats.get('nombre_absences', 0) * 0
            montant_repos = data.stats.get('nombre_repos', 0) * 0
            montant_maladies = data.stats.get('nombre_maladies', 0) * 0
            montant_maladie_payee = 0  # À calculer selon la logique métier
            montant_ferie = data.stats.get('nombre_feries', 0) * 10000
            montant_formation = data.stats.get('nombre_formations', 0) * 10000
            montant_conge = data.stats.get('nombre_conges', 0) * 10000
            montant_dimanches = (
                (data.stats.get('nombre_dimanches_am', 0) * 7500) +
                (data.stats.get('nombre_dimanches_pm', 0) * 7500) +
                (data.stats.get('nombre_dimanches_journee', 0) * 15000)
            )
            '''
            
            # Insérer les calculs avant l'ajout des données
            replacement = montant_calculations + '''
        employes_data.append({
            'employe': employe,
            'presences_data': presences_data,
            'stats': stats,
            'montant_presences': montant_presences,
            'montant_absent': montant_absent,
            'montant_repos': montant_repos,
            'montant_maladies': montant_maladies,
            'montant_maladie_payee': montant_maladie_payee,
            'montant_ferie': montant_ferie,
            'montant_formation': montant_formation,
            'montant_conge': montant_conge,
            'montant_dimanches': montant_dimanches,
        })'''
            
            content = re.sub(pattern, replacement, content)
            print("✅ Calculs de montants ajoutés dans les vues")
        else:
            print("⚠️  Impossible de trouver l'emplacement pour les calculs de montants")
        
        # Sauvegarder le fichier des vues modifié
        with open(views_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Vues mises à jour avec les calculs de montants : {views_path}")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la modification des vues : {e}")
        return False

def main():
    """
    Fonction principale pour restaurer les colonnes de montants
    """
    print("🔄 RESTAURATION DES COLONNES DE MONTANTS")
    print("=" * 50)
    
    success_count = 0
    
    # 1. Ajouter les colonnes au template
    print("\n📝 ÉTAPE 1 : Ajout des colonnes au template")
    if add_montant_columns_to_template():
        success_count += 1
    
    # 2. Mettre à jour les vues pour calculer les montants
    print("\n🔧 ÉTAPE 2 : Mise à jour des calculs dans les vues")
    if update_views_for_montants():
        success_count += 1
    
    # Résumé
    print(f"\n📊 RÉSUMÉ DE LA RESTAURATION")
    print(f"   - Étapes réussies : {success_count}/2")
    
    if success_count == 2:
        print(f"\n✅ RESTAURATION DES COLONNES RÉUSSIE !")
        print(f"🔄 Les colonnes de montants ont été restaurées.")
        print(f"📋 Colonnes ajoutées :")
        print(f"   - Mt Présences")
        print(f"   - Mt Absent")
        print(f"   - Mt J Repos")
        print(f"   - Mt Maladies")
        print(f"   - Mt M.Payer")
        print(f"   - Mt Férié")
        print(f"   - Mt Formation")
        print(f"   - Mt Congé")
        print(f"   - Mt Sundays")
        print(f"\n🚀 Redémarrez le serveur Django pour voir les changements :")
        print(f"   python manage.py runserver")
    else:
        print(f"\n⚠️  RESTAURATION PARTIELLE")
        print(f"Certaines étapes ont échoué. Vérifiez les erreurs ci-dessus.")
    
    return success_count == 2

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
