#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification du calcul corrigé du "Mt Sundays"
Vérifie que la nouvelle formule calcule correctement :
Mt Sundays = (Nombre P(dim_Am) × Montant P(dim_Am)) + (Nombre P(dim_Pm) × Montant P(dim_Pm)) + (Nombre P(dim_Am_&_Pm) × Montant P(dim_Am_&_Pm))
"""

import os
import sys
import django
from datetime import datetime

# Configuration Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import Employe, PresenceJournaliere
from fleet_app.models_entreprise import ConfigurationMontantStatut
from django.contrib.auth.models import User
from django.db.models import Count, Case, When, IntegerField

def verifier_calcul_mt_sundays():
    """
    Vérifie le calcul corrigé du montant des dimanches pour tous les employés
    """
    print("🔍 VÉRIFICATION DU CALCUL CORRIGÉ 'Mt Sundays'")
    print("=" * 60)
    
    # Date actuelle pour le mois en cours
    today = datetime.now()
    
    # Parcourir tous les utilisateurs
    for user in User.objects.all():
        print(f"\n👤 UTILISATEUR : {user.username}")
        print("-" * 50)
        
        # Récupérer la configuration des montants
        try:
            config_montants = ConfigurationMontantStatut.get_or_create_for_user(user)
            montants_dict = config_montants.get_montants_dict()
            
            print("💰 Configuration des montants dimanche :")
            print(f"   montant_dim_am: {montants_dict.get('montant_dim_am', 0):,} GNF")
            print(f"   montant_dim_pm: {montants_dict.get('montant_dim_pm', 0):,} GNF")
            print(f"   montant_dim_journee: {montants_dict.get('montant_dim_journee', 0):,} GNF")
            
        except Exception as e:
            print(f"⚠️ Erreur configuration montants : {e}")
            continue
        
        # Récupérer les employés de cet utilisateur
        employes = Employe.objects.filter(user=user)
        
        if not employes.exists():
            print("ℹ️ Aucun employé trouvé pour cet utilisateur")
            continue
        
        for employe in employes:
            print(f"\n🧑‍💼 EMPLOYÉ : {employe.matricule} - {employe.prenom} {employe.nom} ({employe.statut})")
            
            # Calculer les statistiques avec la nouvelle méthode
            stats = PresenceJournaliere.objects.filter(
                employe=employe,
                date__year=today.year,
                date__month=today.month
            ).aggregate(
                # Comptages séparés pour chaque type de présence dimanche
                nombre_dimanches_am=Count(Case(
                    When(statut='P(dim_Am)', then=1),
                    output_field=IntegerField()
                )),
                nombre_dimanches_pm=Count(Case(
                    When(statut='P(dim_Pm)', then=1),
                    output_field=IntegerField()
                )),
                nombre_dimanches_journee=Count(Case(
                    When(statut='P(dim_Am_&_Pm)', then=1),
                    output_field=IntegerField()
                )),
                # Total des présences dimanche pour comparaison
                nombre_dimanches_total=Count(Case(
                    When(statut__in=['P(dim_Am)', 'P(dim_Pm)', 'P(dim_Am_&_Pm)'], then=1),
                    output_field=IntegerField()
                ))
            )
            
            # Afficher les détails des présences dimanche
            print("   📊 Comptage des présences dimanche par type :")
            print(f"      P(dim_Am)       : {stats['nombre_dimanches_am'] or 0} fois")
            print(f"      P(dim_Pm)       : {stats['nombre_dimanches_pm'] or 0} fois")
            print(f"      P(dim_Am_&_Pm)  : {stats['nombre_dimanches_journee'] or 0} fois")
            print(f"      TOTAL           : {stats['nombre_dimanches_total'] or 0} fois")
            
            # Calculer le montant avec la NOUVELLE formule (correcte)
            montant_dimanches_nouveau = (
                (stats['nombre_dimanches_am'] or 0) * float(montants_dict.get('montant_dim_am', 0)) +
                (stats['nombre_dimanches_pm'] or 0) * float(montants_dict.get('montant_dim_pm', 0)) +
                (stats['nombre_dimanches_journee'] or 0) * float(montants_dict.get('montant_dim_journee', 0))
            )
            
            # Calculer le montant avec l'ANCIENNE formule (incorrecte) pour comparaison
            montant_dimanches_ancien = (stats['nombre_dimanches_total'] or 0) * (
                float(montants_dict.get('montant_dim_am', 0)) + 
                float(montants_dict.get('montant_dim_pm', 0)) + 
                float(montants_dict.get('montant_dim_journee', 0))
            )
            
            print("   💰 Calcul des montants :")
            print(f"      P(dim_Am)       : {stats['nombre_dimanches_am'] or 0} × {montants_dict.get('montant_dim_am', 0):,} = {(stats['nombre_dimanches_am'] or 0) * float(montants_dict.get('montant_dim_am', 0)):,.0f} GNF")
            print(f"      P(dim_Pm)       : {stats['nombre_dimanches_pm'] or 0} × {montants_dict.get('montant_dim_pm', 0):,} = {(stats['nombre_dimanches_pm'] or 0) * float(montants_dict.get('montant_dim_pm', 0)):,.0f} GNF")
            print(f"      P(dim_Am_&_Pm)  : {stats['nombre_dimanches_journee'] or 0} × {montants_dict.get('montant_dim_journee', 0):,} = {(stats['nombre_dimanches_journee'] or 0) * float(montants_dict.get('montant_dim_journee', 0)):,.0f} GNF")
            
            print("   🎯 RÉSULTATS :")
            print(f"      ✅ NOUVEAU (correct) : {montant_dimanches_nouveau:,.0f} GNF")
            print(f"      ❌ ANCIEN (incorrect): {montant_dimanches_ancien:,.0f} GNF")
            
            if montant_dimanches_nouveau != montant_dimanches_ancien:
                difference = montant_dimanches_nouveau - montant_dimanches_ancien
                print(f"      🔄 DIFFÉRENCE        : {difference:+,.0f} GNF")
            else:
                print("      ✅ Pas de différence (cas particulier)")
            
            print("   " + "="*50)
    
    print("\n✅ Vérification terminée avec succès !")
    print("\n📝 RÉSUMÉ DE LA CORRECTION :")
    print("   AVANT : Mt Sundays = Total Dimanches × (Montant dim_AM + Montant dim_PM + Montant dim_Journée)")
    print("   APRÈS : Mt Sundays = (P(dim_Am) × Montant dim_AM) + (P(dim_Pm) × Montant dim_PM) + (P(dim_Am_&_Pm) × Montant dim_Journée)")

if __name__ == "__main__":
    verifier_calcul_mt_sundays()
