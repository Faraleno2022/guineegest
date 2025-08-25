#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de vérification des calculs des heures supplémentaires
Vérifie que :
1. Total Hours = Fin - Début (par ligne)
2. Total mensuel = somme des Total Hours individuels pour chaque travailleur
3. Montant supp. = total mensuel * Définir Montant
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

def calculer_duree_heures(heure_debut, heure_fin):
    """
    Calcule la durée entre deux heures (gère le passage de minuit)
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

def verifier_calculs_heures_supplementaires():
    """
    Vérifie tous les calculs des heures supplémentaires
    """
    print("🔍 VÉRIFICATION DES CALCULS DES HEURES SUPPLÉMENTAIRES")
    print("=" * 80)
    
    # Récupérer toutes les heures supplémentaires
    heures_sup = HeureSupplementaire.objects.all().select_related('employe').order_by('employe', 'date')
    
    if not heures_sup.exists():
        print("❌ Aucune heure supplémentaire trouvée dans la base de données")
        return
    
    print(f"📊 Total des heures supplémentaires à vérifier : {heures_sup.count()}")
    print()
    
    # Dictionnaire pour stocker les totaux par employé et par mois
    totaux_employes = {}
    erreurs_calcul = []
    
    # 1. Vérification ligne par ligne : Total Hours = Fin - Début
    print("1️⃣ VÉRIFICATION : Total Hours = Fin - Début")
    print("-" * 50)
    
    for heure in heures_sup:
        # Calculer la durée attendue
        duree_calculee = calculer_duree_heures(heure.heure_debut, heure.heure_fin)
        duree_stockee = heure.duree
        
        # Clé pour grouper par employé et mois
        cle_employe_mois = f"{heure.employe.id}_{heure.date.year}_{heure.date.month}"
        
        if cle_employe_mois not in totaux_employes:
            totaux_employes[cle_employe_mois] = {
                'employe': heure.employe,
                'mois': heure.date.month,
                'annee': heure.date.year,
                'heures_individuelles': [],
                'total_heures': Decimal('0.00'),
                'montant_defini': heure.total_a_payer or Decimal('0.00')
            }
        
        # Ajouter les heures individuelles
        totaux_employes[cle_employe_mois]['heures_individuelles'].append({
            'date': heure.date,
            'debut': heure.heure_debut,
            'fin': heure.heure_fin,
            'duree_calculee': duree_calculee,
            'duree_stockee': duree_stockee,
            'montant_defini': heure.total_a_payer or Decimal('0.00')
        })
        
        # Vérifier si le calcul est correct (tolérance de 0.01h)
        difference = abs(duree_calculee - duree_stockee)
        if difference > Decimal('0.01'):
            erreurs_calcul.append({
                'type': 'duree',
                'employe': heure.employe,
                'date': heure.date,
                'debut': heure.heure_debut,
                'fin': heure.heure_fin,
                'duree_calculee': duree_calculee,
                'duree_stockee': duree_stockee,
                'difference': difference
            })
            print(f"❌ {heure.employe.matricule} - {heure.date} : {heure.heure_debut}-{heure.heure_fin}")
            print(f"   Calculé: {duree_calculee}h, Stocké: {duree_stockee}h, Différence: {difference}h")
        else:
            print(f"✅ {heure.employe.matricule} - {heure.date} : {heure.heure_debut}-{heure.heure_fin} = {duree_calculee}h")
    
    print()
    
    # 2. Calcul des totaux mensuels par employé
    print("2️⃣ VÉRIFICATION : Total mensuel = somme des Total Hours individuels")
    print("-" * 60)
    
    for cle, data in totaux_employes.items():
        # Calculer le total des heures pour cet employé ce mois-ci
        total_heures_calcule = sum(h['duree_calculee'] for h in data['heures_individuelles'])
        data['total_heures'] = total_heures_calcule
        
        employe = data['employe']
        mois = data['mois']
        annee = data['annee']
        
        print(f"👤 {employe.matricule} - {employe.prenom} {employe.nom}")
        print(f"   📅 Période : {mois:02d}/{annee}")
        print(f"   📊 Nombre d'entrées : {len(data['heures_individuelles'])}")
        
        # Détail des heures individuelles
        for h in data['heures_individuelles']:
            print(f"   • {h['date']} : {h['debut']}-{h['fin']} = {h['duree_calculee']}h")
        
        print(f"   🔢 Total mensuel : {total_heures_calcule}h")
        print()
    
    # 3. Vérification : Montant supp. = total mensuel * Définir Montant
    print("3️⃣ VÉRIFICATION : Montant supp. = Total Hours × Définir Montant")
    print("-" * 65)
    
    for cle, data in totaux_employes.items():
        employe = data['employe']
        total_heures = data['total_heures']
        
        # Récupérer le montant défini (utiliser le dernier montant défini pour cet employé)
        heures_employe = [h for h in heures_sup if h.employe == employe]
        montant_defini = Decimal('0.00')
        
        if heures_employe:
            # Prendre le montant le plus récent non nul
            for h in sorted(heures_employe, key=lambda x: x.date, reverse=True):
                if h.total_a_payer and h.total_a_payer > 0:
                    montant_defini = h.total_a_payer
                    break
        
        print(f"👤 {employe.matricule} - {employe.prenom} {employe.nom}")
        print(f"   📊 Total heures mensuelles : {total_heures}h")
        print(f"   💰 Montant défini : {montant_defini} GNF")
        
        if montant_defini > 0:
            montant_supp_calcule = total_heures * montant_defini
            print(f"   🧮 Calcul : {total_heures}h × {montant_defini} = {montant_supp_calcule} GNF")
            
            # Vérifier avec la méthode du modèle
            for h in heures_employe:
                if h.total_a_payer and h.total_a_payer > 0:
                    montant_modele = h.calculer_montant_supplementaire_simple()
                    duree_utilisee = getattr(h, 'duree_calculee', None) or h.duree
                    montant_attendu = float(duree_utilisee) * float(h.total_a_payer)
                    
                    print(f"   🔍 Ligne {h.date} : {duree_utilisee}h × {h.total_a_payer} = {montant_modele} GNF")
                    
                    if abs(montant_modele - montant_attendu) > 0.01:
                        erreurs_calcul.append({
                            'type': 'montant',
                            'employe': employe,
                            'date': h.date,
                            'montant_calcule': montant_modele,
                            'montant_attendu': montant_attendu,
                            'difference': abs(montant_modele - montant_attendu)
                        })
                        print(f"   ❌ Erreur de calcul détectée !")
                    break
        else:
            print(f"   ⚠️  Aucun montant défini")
        
        print()
    
    # 4. Résumé des erreurs
    print("4️⃣ RÉSUMÉ DES VÉRIFICATIONS")
    print("-" * 40)
    
    if erreurs_calcul:
        print(f"❌ {len(erreurs_calcul)} erreur(s) détectée(s) :")
        
        erreurs_duree = [e for e in erreurs_calcul if e['type'] == 'duree']
        erreurs_montant = [e for e in erreurs_calcul if e['type'] == 'montant']
        
        if erreurs_duree:
            print(f"   • {len(erreurs_duree)} erreur(s) de calcul de durée")
        
        if erreurs_montant:
            print(f"   • {len(erreurs_montant)} erreur(s) de calcul de montant")
    else:
        print("✅ Tous les calculs sont corrects !")
    
    print()
    print("📈 STATISTIQUES GLOBALES")
    print("-" * 30)
    print(f"• Nombre total d'employés : {len(set(h.employe for h in heures_sup))}")
    print(f"• Nombre total d'heures sup : {heures_sup.count()}")
    print(f"• Nombre de mois différents : {len(totaux_employes)}")
    
    # Total général des heures
    total_heures_global = sum(data['total_heures'] for data in totaux_employes.values())
    print(f"• Total heures supplémentaires : {total_heures_global}h")
    
    return len(erreurs_calcul) == 0

if __name__ == "__main__":
    print("🚀 Démarrage de la vérification des calculs des heures supplémentaires")
    print("=" * 80)
    
    try:
        succes = verifier_calculs_heures_supplementaires()
        
        if succes:
            print("\n🎉 VÉRIFICATION TERMINÉE AVEC SUCCÈS !")
            print("Tous les calculs des heures supplémentaires sont corrects.")
        else:
            print("\n⚠️  VÉRIFICATION TERMINÉE AVEC DES ERREURS !")
            print("Certains calculs nécessitent une correction.")
            
    except Exception as e:
        print(f"\n❌ ERREUR LORS DE LA VÉRIFICATION : {e}")
        import traceback
        traceback.print_exc()
