"""
Utilitaires pour la gestion de l'archivage mensuel et la transition entre les mois.

Ce module contient les fonctions nécessaires pour :
- Préparer les données pour le nouveau mois après archivage
- Vérifier la cohérence des données de référence
- Initialiser les structures nécessaires pour le nouveau mois
"""

from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from decimal import Decimal


def preparer_nouveau_mois(user, nouveau_mois, nouvelle_annee):
    """
    Prépare les structures de données pour le nouveau mois après archivage.
    
    DONNÉES CONSERVÉES (référence) :
    - employes/ : Matricule, Employé, Fonction, Salaire de base, Statut
    - Configuration des montants par employé
    - Légende des statuts et montants
    - Paramètres de paie : Matricule, Prénom, Nom, Fonction, Salaire Base
    
    DONNÉES RÉINITIALISÉES (transactionnelles) :
    - presences/ : toutes les données de pointage
    - paies/ : toutes les paies calculées
    - heures-supplementaires/ : toutes les heures supplémentaires
    - bulletins/ : tous les bulletins générés
    """
    from .models import Employe, ParametrePaie
    from .models_entreprise import ConfigurationMontantEmploye, ConfigurationMontantStatut
    
    print(f"🆕 NOUVEAU MOIS: Préparation pour {nouveau_mois:02d}/{nouvelle_annee}")
    
    # Récupérer tous les employés actifs (données de référence conservées)
    employes_actifs = Employe.objects.filter(user=user, statut='Actif')
    employes_inactifs = Employe.objects.filter(user=user, statut='Inactif')
    
    # Vérifier que les configurations de montants existent pour tous les employés
    employes_sans_config = []
    for employe in employes_actifs:
        config = ConfigurationMontantEmploye.objects.filter(employe=employe).first()
        if not config:
            employes_sans_config.append(employe)
    
    # Statistiques des données de référence conservées
    stats_reference = {
        'employes_actifs': employes_actifs.count(),
        'employes_inactifs': employes_inactifs.count(),
        'employes_sans_config': len(employes_sans_config),
        'parametres_paie': ParametrePaie.objects.filter(user=user).count(),
        'configurations_statuts': ConfigurationMontantStatut.objects.filter(user=user).count()
    }
    
    # Calculer le nombre de jours du nouveau mois
    nb_jours_mois = calendar.monthrange(nouvelle_annee, nouveau_mois)[1]
    
    # Informations sur le nouveau mois
    info_nouveau_mois = {
        'mois': nouveau_mois,
        'annee': nouvelle_annee,
        'nb_jours': nb_jours_mois,
        'nom_mois': calendar.month_name[nouveau_mois],
        'premier_jour': datetime(nouvelle_annee, nouveau_mois, 1).date(),
        'dernier_jour': datetime(nouvelle_annee, nouveau_mois, nb_jours_mois).date()
    }
    
    print(f"✅ NOUVEAU MOIS: Données de référence conservées:")
    print(f"   👥 Employés actifs: {stats_reference['employes_actifs']}")
    print(f"   💤 Employés inactifs: {stats_reference['employes_inactifs']}")
    print(f"   ⚙️ Paramètres de paie: {stats_reference['parametres_paie']}")
    print(f"   💰 Configurations montants: {stats_reference['configurations_statuts']}")
    print(f"   📅 Nouveau mois: {info_nouveau_mois['nom_mois']} {nouvelle_annee} ({nb_jours_mois} jours)")
    
    if employes_sans_config:
        print(f"   ⚠️ Employés sans configuration de montants: {len(employes_sans_config)}")
        for emp in employes_sans_config:
            print(f"      - {emp.matricule} {emp.prenom} {emp.nom}")
    
    return {
        'stats_reference': stats_reference,
        'info_nouveau_mois': info_nouveau_mois,
        'employes_sans_config': employes_sans_config,
        'success': True
    }


def verifier_coherence_donnees_reference(user):
    """
    Vérifie la cohérence des données de référence avant/après archivage.
    
    Contrôle que toutes les données de référence sont bien présentes et cohérentes.
    """
    from .models import Employe, ParametrePaie
    from .models_entreprise import ConfigurationMontantEmploye, ConfigurationMontantStatut
    
    print(f"🔍 VÉRIFICATION: Cohérence des données de référence")
    
    incohérences = []
    
    # Vérifier les employés
    employes = Employe.objects.filter(user=user)
    for employe in employes:
        # Vérifier que chaque employé a une configuration de montants
        config = ConfigurationMontantEmploye.objects.filter(employe=employe).first()
        if not config:
            incohérences.append(f"Employé {employe.matricule} sans configuration de montants")
        
        # Vérifier les champs obligatoires
        if not employe.matricule:
            incohérences.append(f"Employé {employe.id} sans matricule")
        if not employe.fonction:
            incohérences.append(f"Employé {employe.matricule} sans fonction")
        if not employe.salaire_journalier:
            incohérences.append(f"Employé {employe.matricule} sans salaire de base")
    
    # Vérifier les paramètres de paie
    parametres_requis = ['taux_cnss', 'taux_rts', 'salaire_minimum']
    for param_requis in parametres_requis:
        param = ParametrePaie.objects.filter(user=user, cle=param_requis).first()
        if not param:
            incohérences.append(f"Paramètre de paie manquant: {param_requis}")
    
    # Vérifier les configurations de statuts
    statuts_requis = ['P(Am)', 'P(Pm)', 'P(Am&Pm)', 'Dimanche', 'Absent', 'Maladie', 'M.Payer', 'J Repos', 'Congé', 'Formation', 'Mt Férié']
    for statut in statuts_requis:
        config = ConfigurationMontantStatut.objects.filter(user=user, statut=statut).first()
        if not config:
            incohérences.append(f"Configuration de statut manquante: {statut}")
    
    if incohérences:
        print(f"❌ VÉRIFICATION: {len(incohérences)} incohérence(s) détectée(s):")
        for incohérence in incohérences:
            print(f"   - {incohérence}")
    else:
        print(f"✅ VÉRIFICATION: Toutes les données de référence sont cohérentes")
    
    return {
        'coherent': len(incohérences) == 0,
        'incoherences': incohérences,
        'nb_employes': employes.count(),
        'nb_parametres': ParametrePaie.objects.filter(user=user).count(),
        'nb_configs_statuts': ConfigurationMontantStatut.objects.filter(user=user).count()
    }


def nettoyer_donnees_transactionnelles_orphelines(user):
    """
    Nettoie les données transactionnelles qui pourraient être orphelines
    après un archivage incomplet.
    """
    from .models import PresenceJournaliere, PaieEmploye, HeureSupplementaire
    
    print(f"🧹 NETTOYAGE: Suppression des données transactionnelles orphelines")
    
    # Compter les données avant nettoyage
    presences_avant = PresenceJournaliere.objects.filter(employe__user=user).count()
    paies_avant = PaieEmploye.objects.filter(employe__user=user).count()
    heures_avant = HeureSupplementaire.objects.filter(employe__user=user).count()
    
    # Supprimer les données orphelines (employés supprimés)
    employes_existants = Employe.objects.filter(user=user).values_list('id', flat=True)
    
    presences_orphelines = PresenceJournaliere.objects.exclude(employe_id__in=employes_existants).delete()
    paies_orphelines = PaieEmploye.objects.exclude(employe_id__in=employes_existants).delete()
    heures_orphelines = HeureSupplementaire.objects.exclude(employe_id__in=employes_existants).delete()
    
    # Compter les données après nettoyage
    presences_apres = PresenceJournaliere.objects.filter(employe__user=user).count()
    paies_apres = PaieEmploye.objects.filter(employe__user=user).count()
    heures_apres = HeureSupplementaire.objects.filter(employe__user=user).count()
    
    print(f"🧹 NETTOYAGE TERMINÉ:")
    print(f"   📊 Présences: {presences_avant} → {presences_apres} (supprimées: {presences_orphelines[0] if presences_orphelines else 0})")
    print(f"   💰 Paies: {paies_avant} → {paies_apres} (supprimées: {paies_orphelines[0] if paies_orphelines else 0})")
    print(f"   ⏰ Heures supp: {heures_avant} → {heures_apres} (supprimées: {heures_orphelines[0] if heures_orphelines else 0})")
    
    return {
        'presences_supprimees': presences_orphelines[0] if presences_orphelines else 0,
        'paies_supprimees': paies_orphelines[0] if paies_orphelines else 0,
        'heures_supprimees': heures_orphelines[0] if heures_orphelines else 0,
        'success': True
    }


def calculer_mois_suivant(mois, annee):
    """
    Calcule le mois et l'année suivants.
    """
    if mois == 12:
        return 1, annee + 1
    else:
        return mois + 1, annee


def calculer_mois_precedent(mois, annee):
    """
    Calcule le mois et l'année précédents.
    """
    if mois == 1:
        return 12, annee - 1
    else:
        return mois - 1, annee


def obtenir_info_mois(mois, annee):
    """
    Obtient les informations détaillées sur un mois donné.
    """
    nb_jours = calendar.monthrange(annee, mois)[1]
    nom_mois = calendar.month_name[mois]
    
    return {
        'mois': mois,
        'annee': annee,
        'nb_jours': nb_jours,
        'nom_mois': nom_mois,
        'nom_complet': f"{nom_mois} {annee}",
        'premier_jour': datetime(annee, mois, 1).date(),
        'dernier_jour': datetime(annee, mois, nb_jours).date()
    }
