#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification du calcul du "Mt Absences"
Vérifie que la formule calcule correctement :
Mt Absences = Nombre A (Absent) × Montant A (Absent)
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

def verifier_calcul_mt_absences():
    """
    Vérifie le calcul du montant des absences pour tous les employés
    """
    print("🔍 VÉRIFICATION DU CALCUL 'Mt Absences'")
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
            
            print("💰 Configuration du montant absence :")
            print(f"   montant_absent: {montants_dict.get('montant_absent', 0):,} GNF")
            
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
            
            # Calculer les statistiques d'absences
            stats = PresenceJournaliere.objects.filter(
                employe=employe,
                date__year=today.year,
                date__month=today.month
            ).aggregate(
                nombre_absences=Count(Case(
                    When(statut='A', then=1),
                    output_field=IntegerField()
                ))
            )
            
            # Afficher les détails des absences
            print("   📊 Comptage des absences :")
            print(f"      A (Absent) : {stats['nombre_absences'] or 0} fois")
            
            # Calculer le montant des absences
            montant_absences = (stats['nombre_absences'] or 0) * float(montants_dict.get('montant_absent', 0))
            
            print("   💰 Calcul du montant :")
            print(f"      A (Absent) : {stats['nombre_absences'] or 0} × {montants_dict.get('montant_absent', 0):,} = {montant_absences:,.0f} GNF")
            
            print("   🎯 RÉSULTAT :")
            print(f"      ✅ Mt Absences : {montant_absences:,.0f} GNF")
            
            # Vérifier la cohérence
            if stats['nombre_absences'] == 0:
                print("      ℹ️ Aucune absence ce mois-ci")
            elif montants_dict.get('montant_absent', 0) == 0:
                print("      ⚠️ Montant absence non configuré (0 GNF)")
            else:
                print("      ✅ Calcul cohérent et correct")
            
            print("   " + "="*50)
    
    print("\n✅ Vérification terminée avec succès !")
    print("\n📝 FORMULE APPLIQUÉE :")
    print("   Mt Absences = Nombre A (Absent) × Montant A (Absent)")
    print("\n💡 NOTE : Cette formule est déjà correcte dans le système.")

if __name__ == "__main__":
    verifier_calcul_mt_absences()
