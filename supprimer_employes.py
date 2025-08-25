#!/usr/bin/env python
"""
Script pour supprimer complètement tous les employés et leurs données liées
de la base de données Django.

ATTENTION: Cette opération est IRRÉVERSIBLE !
Toutes les données des employés, leurs paies, heures supplémentaires,
présences et configurations seront définitivement supprimées.
"""

import os
import sys
import django
from django.db import transaction

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

def supprimer_tous_employes():
    """
    Supprime tous les employés et toutes leurs données liées
    """
    try:
        # Import des modèles
        from fleet_app.models_entreprise import (
            Employe, 
            PaieEmploye, 
            HeureSupplementaire,
            PresenceJournaliere,
            ConfigurationMontantEmploye
        )
        
        print("🔍 Vérification des données existantes...")
        
        # Compter les données avant suppression
        nb_employes = Employe.objects.count()
        nb_paies = PaieEmploye.objects.count()
        nb_heures_supp = HeureSupplementaire.objects.count()
        nb_presences = PresenceJournaliere.objects.count()
        nb_configs = ConfigurationMontantEmploye.objects.count()
        
        print(f"📊 Données trouvées:")
        print(f"   - Employés: {nb_employes}")
        print(f"   - Paies: {nb_paies}")
        print(f"   - Heures supplémentaires: {nb_heures_supp}")
        print(f"   - Présences: {nb_presences}")
        print(f"   - Configurations montants: {nb_configs}")
        
        if nb_employes == 0:
            print("✅ Aucun employé trouvé dans la base de données.")
            return True
        
        print(f"\n⚠️  ATTENTION: Vous êtes sur le point de supprimer DÉFINITIVEMENT:")
        print(f"   - {nb_employes} employé(s)")
        print(f"   - {nb_paies} paie(s)")
        print(f"   - {nb_heures_supp} heure(s) supplémentaire(s)")
        print(f"   - {nb_presences} présence(s)")
        print(f"   - {nb_configs} configuration(s) de montants")
        
        confirmation = input("\n❓ Êtes-vous sûr de vouloir continuer ? (tapez 'OUI' pour confirmer): ")
        
        if confirmation.upper() != 'OUI':
            print("❌ Opération annulée par l'utilisateur.")
            return False
        
        print("\n🗑️  Suppression en cours...")
        
        # Utiliser une transaction pour s'assurer que tout est supprimé ou rien
        with transaction.atomic():
            
            # 1. Supprimer les configurations de montants
            if nb_configs > 0:
                print("   - Suppression des configurations de montants...")
                ConfigurationMontantEmploye.objects.all().delete()
            
            # 2. Supprimer les présences journalières
            if nb_presences > 0:
                print("   - Suppression des présences journalières...")
                PresenceJournaliere.objects.all().delete()
            
            # 3. Supprimer les heures supplémentaires
            if nb_heures_supp > 0:
                print("   - Suppression des heures supplémentaires...")
                HeureSupplementaire.objects.all().delete()
            
            # 4. Supprimer les paies
            if nb_paies > 0:
                print("   - Suppression des paies...")
                PaieEmploye.objects.all().delete()
            
            # 5. Supprimer les employés (en dernier)
            print("   - Suppression des employés...")
            Employe.objects.all().delete()
        
        print("\n✅ Suppression terminée avec succès !")
        
        # Vérification finale
        print("\n🔍 Vérification finale...")
        nb_employes_final = Employe.objects.count()
        nb_paies_final = PaieEmploye.objects.count()
        nb_heures_supp_final = HeureSupplementaire.objects.count()
        nb_presences_final = PresenceJournaliere.objects.count()
        nb_configs_final = ConfigurationMontantEmploye.objects.count()
        
        print(f"📊 Données restantes:")
        print(f"   - Employés: {nb_employes_final}")
        print(f"   - Paies: {nb_paies_final}")
        print(f"   - Heures supplémentaires: {nb_heures_supp_final}")
        print(f"   - Présences: {nb_presences_final}")
        print(f"   - Configurations montants: {nb_configs_final}")
        
        if (nb_employes_final == 0 and nb_paies_final == 0 and 
            nb_heures_supp_final == 0 and nb_presences_final == 0 and 
            nb_configs_final == 0):
            print("\n🎉 Toutes les données des employés ont été supprimées avec succès !")
            print("💡 La base de données est maintenant vide et prête pour de nouvelles données.")
            return True
        else:
            print("\n⚠️  Attention: Il reste encore des données dans la base.")
            return False
            
    except Exception as e:
        print(f"\n❌ Erreur lors de la suppression: {str(e)}")
        print("🔄 La transaction a été annulée, aucune donnée n'a été supprimée.")
        return False

def main():
    """
    Fonction principale
    """
    print("=" * 60)
    print("🗑️  SUPPRESSION COMPLÈTE DES DONNÉES EMPLOYÉS")
    print("=" * 60)
    print()
    
    success = supprimer_tous_employes()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ OPÉRATION TERMINÉE AVEC SUCCÈS")
    else:
        print("❌ OPÉRATION ÉCHOUÉE OU ANNULÉE")
    print("=" * 60)

if __name__ == "__main__":
    main()
