#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de correction des calculs des heures supplémentaires
Corrige automatiquement :
1. Total Hours = Fin - Début (gestion du passage de minuit)
2. Met à jour la base de données avec les bonnes durées
3. Vérifie que les montants se recalculent correctement
"""

import os
import sys
import django
from datetime import datetime, timedelta, time
from decimal import Decimal, ROUND_HALF_UP

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models_entreprise import HeureSupplementaire, Employe
from django.contrib.auth.models import User
from django.db import transaction

def calculer_duree_heures_correcte(heure_debut, heure_fin):
    """
    Calcule la durée entre deux heures avec gestion correcte du passage de minuit
    """
    if not heure_debut or not heure_fin:
        return Decimal('0.00')
    
    # Convertir en datetime pour faciliter les calculs
    debut = datetime.combine(datetime.today(), heure_debut)
    fin = datetime.combine(datetime.today(), heure_fin)
    
    # Si l'heure de fin est inférieure à l'heure de début, on assume que c'est le lendemain
    if fin < debut:
        fin += timedelta(days=1)
    
    # Calculer la différence en heures
    duree_timedelta = fin - debut
    duree_heures = duree_timedelta.total_seconds() / 3600
    
    return Decimal(str(duree_heures)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def corriger_calculs_heures_supplementaires():
    """
    Corrige tous les calculs des heures supplémentaires
    """
    print("🔧 CORRECTION DES CALCULS DES HEURES SUPPLÉMENTAIRES")
    print("=" * 80)
    
    # Récupérer toutes les heures supplémentaires
    heures_sup = HeureSupplementaire.objects.all().select_related('employe').order_by('employe', 'date')
    
    if not heures_sup.exists():
        print("❌ Aucune heure supplémentaire trouvée dans la base de données")
        return False
    
    print(f"📊 Total des heures supplémentaires à corriger : {heures_sup.count()}")
    print()
    
    corrections_effectuees = 0
    erreurs_corrigees = []
    
    with transaction.atomic():
        print("1️⃣ CORRECTION DES DURÉES (Total Hours = Fin - Début)")
        print("-" * 60)
        
        for heure in heures_sup:
            # Calculer la durée correcte
            duree_correcte = calculer_duree_heures_correcte(heure.heure_debut, heure.heure_fin)
            duree_actuelle = heure.duree
            
            # Vérifier si une correction est nécessaire (tolérance de 0.01h)
            difference = abs(duree_correcte - duree_actuelle)
            
            if difference > Decimal('0.01'):
                print(f"🔧 Correction pour {heure.employe.matricule} - {heure.date}")
                print(f"   Heures : {heure.heure_debut} à {heure.heure_fin}")
                print(f"   Avant : {duree_actuelle}h")
                print(f"   Après : {duree_correcte}h")
                print(f"   Gain : +{duree_correcte - duree_actuelle}h")
                
                # Sauvegarder l'ancienne valeur pour le rapport
                erreurs_corrigees.append({
                    'employe': heure.employe,
                    'date': heure.date,
                    'debut': heure.heure_debut,
                    'fin': heure.heure_fin,
                    'duree_avant': duree_actuelle,
                    'duree_apres': duree_correcte,
                    'gain': duree_correcte - duree_actuelle,
                    'montant_defini': heure.total_a_payer or Decimal('0.00')
                })
                
                # Appliquer la correction
                heure.duree = duree_correcte
                heure.save()
                corrections_effectuees += 1
                
                print(f"   ✅ Correction appliquée")
            else:
                print(f"✅ {heure.employe.matricule} - {heure.date} : Durée correcte ({duree_correcte}h)")
            
            print()
    
    print("2️⃣ VÉRIFICATION POST-CORRECTION")
    print("-" * 40)
    
    # Recalculer les totaux par employé après correction
    totaux_employes = {}
    
    # Recharger les données après correction
    heures_sup_corrigees = HeureSupplementaire.objects.all().select_related('employe').order_by('employe', 'date')
    
    for heure in heures_sup_corrigees:
        cle_employe_mois = f"{heure.employe.id}_{heure.date.year}_{heure.date.month}"
        
        if cle_employe_mois not in totaux_employes:
            totaux_employes[cle_employe_mois] = {
                'employe': heure.employe,
                'mois': heure.date.month,
                'annee': heure.date.year,
                'total_heures': Decimal('0.00'),
                'montant_defini': heure.total_a_payer or Decimal('0.00'),
                'nombre_entrees': 0
            }
        
        totaux_employes[cle_employe_mois]['total_heures'] += heure.duree
        totaux_employes[cle_employe_mois]['nombre_entrees'] += 1
        
        # Utiliser le montant le plus récent
        if heure.total_a_payer and heure.total_a_payer > 0:
            totaux_employes[cle_employe_mois]['montant_defini'] = heure.total_a_payer
    
    print("📊 TOTAUX MENSUELS APRÈS CORRECTION :")
    print("-" * 45)
    
    for cle, data in totaux_employes.items():
        employe = data['employe']
        total_heures = data['total_heures']
        montant_defini = data['montant_defini']
        nombre_entrees = data['nombre_entrees']
        
        print(f"👤 {employe.matricule} - {employe.prenom} {employe.nom}")
        print(f"   📅 Période : {data['mois']:02d}/{data['annee']}")
        print(f"   📊 Entrées : {nombre_entrees}")
        print(f"   ⏱️  Total heures : {total_heures}h")
        print(f"   💰 Montant défini : {montant_defini} GNF")
        
        if montant_defini > 0:
            montant_total = total_heures * montant_defini
            print(f"   🧮 Montant total : {total_heures}h × {montant_defini} = {montant_total} GNF")
        else:
            print(f"   ⚠️  Aucun montant défini")
        
        print()
    
    print("3️⃣ RÉSUMÉ DES CORRECTIONS")
    print("-" * 35)
    
    if corrections_effectuees > 0:
        print(f"✅ {corrections_effectuees} correction(s) appliquée(s)")
        print()
        
        print("📋 DÉTAIL DES CORRECTIONS :")
        for correction in erreurs_corrigees:
            employe = correction['employe']
            print(f"• {employe.matricule} - {correction['date']}")
            print(f"  Heures : {correction['debut']} à {correction['fin']}")
            print(f"  Durée : {correction['duree_avant']}h → {correction['duree_apres']}h")
            print(f"  Gain : +{correction['gain']}h")
            
            if correction['montant_defini'] > 0:
                gain_montant = correction['gain'] * correction['montant_defini']
                print(f"  Gain financier : +{gain_montant} GNF")
            
            print()
        
        # Calculer le gain total
        gain_total_heures = sum(c['gain'] for c in erreurs_corrigees)
        print(f"🎯 GAIN TOTAL : +{gain_total_heures}h")
        
        # Calculer le gain financier total
        gain_financier_total = sum(
            c['gain'] * c['montant_defini'] 
            for c in erreurs_corrigees 
            if c['montant_defini'] > 0
        )
        if gain_financier_total > 0:
            print(f"💰 GAIN FINANCIER TOTAL : +{gain_financier_total} GNF")
    else:
        print("✅ Aucune correction nécessaire - Tous les calculs étaient déjà corrects")
    
    return corrections_effectuees > 0

def verifier_coherence_post_correction():
    """
    Vérifie la cohérence des calculs après correction
    """
    print("\n4️⃣ VÉRIFICATION DE COHÉRENCE POST-CORRECTION")
    print("-" * 55)
    
    heures_sup = HeureSupplementaire.objects.all().select_related('employe')
    problemes_detectes = 0
    
    for heure in heures_sup:
        duree_calculee = calculer_duree_heures_correcte(heure.heure_debut, heure.heure_fin)
        duree_stockee = heure.duree
        
        difference = abs(duree_calculee - duree_stockee)
        if difference > Decimal('0.01'):
            print(f"❌ Incohérence détectée pour {heure.employe.matricule} - {heure.date}")
            print(f"   Calculé: {duree_calculee}h, Stocké: {duree_stockee}h")
            problemes_detectes += 1
    
    if problemes_detectes == 0:
        print("✅ Toutes les durées sont cohérentes après correction")
        return True
    else:
        print(f"❌ {problemes_detectes} problème(s) de cohérence détecté(s)")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage de la correction des calculs des heures supplémentaires")
    print("=" * 80)
    
    try:
        # Effectuer les corrections
        corrections_appliquees = corriger_calculs_heures_supplementaires()
        
        # Vérifier la cohérence après correction
        coherence_ok = verifier_coherence_post_correction()
        
        print("\n" + "=" * 80)
        if corrections_appliquees and coherence_ok:
            print("🎉 CORRECTION TERMINÉE AVEC SUCCÈS !")
            print("Les calculs des heures supplémentaires ont été corrigés.")
            print("Tous les montants sont maintenant basés sur les durées correctes.")
        elif not corrections_appliquees:
            print("✅ AUCUNE CORRECTION NÉCESSAIRE")
            print("Tous les calculs étaient déjà corrects.")
        else:
            print("⚠️  CORRECTION PARTIELLE")
            print("Certains problèmes persistent après correction.")
            
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE LA CORRECTION : {e}")
        import traceback
        traceback.print_exc()
