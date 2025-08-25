"""
Utilitaires pour la navigation mensuelle dans les présences.

Ce module gère la navigation entre les mois dans la page des présences,
en préservant les données de référence et en gérant correctement les transitions.
"""

from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from django.contrib import messages


def gerer_navigation_mois(request, mois_actuel, annee_actuelle):
    """
    Gère la navigation mensuelle dans les présences.
    
    Retourne les informations nécessaires pour afficher le bon mois
    et gérer les transitions entre les mois.
    """
    # Récupérer le mois demandé depuis les paramètres GET
    mois_demande = request.GET.get('mois')
    annee_demandee = request.GET.get('annee')
    
    # Si des paramètres sont fournis, les utiliser
    if mois_demande and annee_demandee:
        try:
            mois_actuel = int(mois_demande)
            annee_actuelle = int(annee_demandee)
        except (ValueError, TypeError):
            # En cas d'erreur, utiliser le mois actuel
            pass
    
    # Calculer les mois précédent et suivant
    mois_precedent, annee_precedente = calculer_mois_precedent(mois_actuel, annee_actuelle)
    mois_suivant, annee_suivante = calculer_mois_suivant(mois_actuel, annee_actuelle)
    
    # Informations sur le mois actuel
    nb_jours_mois = calendar.monthrange(annee_actuelle, mois_actuel)[1]
    nom_mois = calendar.month_name[mois_actuel]
    
    # Vérifier s'il y a une archive pour le mois actuel
    from .models import ArchiveMensuelle
    archive_mois = ArchiveMensuelle.objects.filter(
        user=request.user,
        mois=mois_actuel,
        annee=annee_actuelle
    ).first()
    
    return {
        'mois_actuel': mois_actuel,
        'annee_actuelle': annee_actuelle,
        'nom_mois_actuel': nom_mois,
        'nb_jours_mois': nb_jours_mois,
        'mois_precedent': mois_precedent,
        'annee_precedente': annee_precedente,
        'mois_suivant': mois_suivant,
        'annee_suivante': annee_suivante,
        'archive_existante': archive_mois is not None,
        'archive': archive_mois,
        'urls_navigation': {
            'precedent': f"?mois={mois_precedent}&annee={annee_precedente}",
            'suivant': f"?mois={mois_suivant}&annee={annee_suivante}",
            'actuel': f"?mois={timezone.now().month}&annee={timezone.now().year}"
        }
    }


def verifier_fin_de_mois(mois, annee):
    """
    Vérifie si nous sommes à la fin du mois et si un archivage est nécessaire.
    
    Retourne des informations sur l'état du mois et les actions recommandées.
    """
    aujourd_hui = timezone.now().date()
    nb_jours_mois = calendar.monthrange(annee, mois)[1]
    dernier_jour_mois = datetime(annee, mois, nb_jours_mois).date()
    
    # Calculer le nombre de jours restants
    jours_restants = (dernier_jour_mois - aujourd_hui).days
    
    # Déterminer l'état du mois
    if jours_restants < 0:
        etat = "mois_termine"
        message = f"Le mois de {calendar.month_name[mois]} {annee} est terminé. Archivage recommandé."
        urgence = "haute"
    elif jours_restants <= 3:
        etat = "fin_proche"
        message = f"Fin du mois dans {jours_restants} jour(s). Préparez l'archivage."
        urgence = "moyenne"
    elif jours_restants <= 7:
        etat = "fin_approche"
        message = f"Fin du mois dans {jours_restants} jours."
        urgence = "faible"
    else:
        etat = "en_cours"
        message = f"Mois en cours. {jours_restants} jours restants."
        urgence = "aucune"
    
    return {
        'etat': etat,
        'message': message,
        'urgence': urgence,
        'jours_restants': jours_restants,
        'dernier_jour': dernier_jour_mois,
        'archivage_recommande': etat in ['mois_termine', 'fin_proche']
    }


def obtenir_donnees_reference_mois(user, mois, annee):
    """
    Obtient les données de référence pour un mois donné.
    
    Ces données restent constantes d'un mois à l'autre :
    - Employés (matricule, nom, fonction, salaire, statut)
    - Configuration des montants
    - Paramètres de paie
    """
    from .models import Employe, ParametrePaie
    from .models_entreprise import ConfigurationMontantEmploye, ConfigurationMontantStatut
    
    # Employés avec leurs informations de référence
    employes = Employe.objects.filter(user=user).select_related().order_by('matricule')
    
    # Configuration des montants par statut (référence globale)
    config_statuts = {}
    for config in ConfigurationMontantStatut.objects.filter(user=user):
        config_statuts[config.statut] = {
            'montant': float(config.montant),
            'description': config.description
        }
    
    # Configuration des montants par employé (référence individuelle)
    config_employes = {}
    for config in ConfigurationMontantEmploye.objects.select_related('employe'):
        if config.employe.user == user:
            config_employes[config.employe.id] = {
                'montant_am': float(config.montant_am),
                'montant_pm': float(config.montant_pm),
                'montant_journee': float(config.montant_journee),
                'montant_dim_journee': float(config.montant_dim_journee),
                'montant_absent': float(config.montant_absent),
                'montant_maladie': float(config.montant_maladie),
                'montant_maladie_payee': float(config.montant_maladie_payee),
                'montant_repos': float(config.montant_repos),
                'montant_conge': float(config.montant_conge),
                'montant_formation': float(config.montant_formation),
                'montant_ferie': float(config.montant_ferie)
            }
    
    # Paramètres de paie (référence système)
    parametres = {}
    for param in ParametrePaie.objects.filter(user=user):
        parametres[param.cle] = param.valeur
    
    return {
        'employes': employes,
        'config_statuts': config_statuts,
        'config_employes': config_employes,
        'parametres': parametres,
        'nb_employes_actifs': employes.filter(statut='Actif').count(),
        'nb_employes_inactifs': employes.filter(statut='Inactif').count()
    }


def calculer_mois_precedent(mois, annee):
    """Calcule le mois précédent."""
    if mois == 1:
        return 12, annee - 1
    else:
        return mois - 1, annee


def calculer_mois_suivant(mois, annee):
    """Calcule le mois suivant."""
    if mois == 12:
        return 1, annee + 1
    else:
        return mois + 1, annee


def generer_alerte_archivage(request, info_fin_mois):
    """
    Génère les alertes appropriées pour l'archivage selon l'état du mois.
    """
    if info_fin_mois['urgence'] == 'haute':
        messages.warning(request, f"🗂️ {info_fin_mois['message']} Cliquez sur 'Archiver le mois' pour passer au mois suivant.")
    elif info_fin_mois['urgence'] == 'moyenne':
        messages.info(request, f"📅 {info_fin_mois['message']}")
    
    return info_fin_mois


def obtenir_statistiques_mois(user, mois, annee):
    """
    Calcule les statistiques pour un mois donné.
    
    Inclut les données transactionnelles (présences, paies, heures supp)
    et les données de référence.
    """
    from .models import PresenceJournaliere, PaieEmploye, HeureSupplementaire
    from django.db.models import Count, Sum
    
    # Statistiques des présences
    presences_stats = PresenceJournaliere.objects.filter(
        employe__user=user,
        date__month=mois,
        date__year=annee
    ).values('statut').annotate(count=Count('id'))
    
    presences_par_statut = {}
    for stat in presences_stats:
        presences_par_statut[stat['statut']] = stat['count']
    
    # Statistiques des paies
    paies_stats = PaieEmploye.objects.filter(
        employe__user=user,
        mois=mois,
        annee=annee
    ).aggregate(
        total_brut=Sum('salaire_brut'),
        total_net=Sum('salaire_net_a_payer'),
        nb_paies=Count('id')
    )
    
    # Statistiques des heures supplémentaires
    heures_stats = HeureSupplementaire.objects.filter(
        employe__user=user,
        date__month=mois,
        date__year=annee
    ).aggregate(
        total_heures=Sum('duree'),
        total_montant=Sum('total_a_payer'),
        nb_heures_supp=Count('id')
    )
    
    return {
        'presences': presences_par_statut,
        'paies': {
            'total_brut': float(paies_stats['total_brut'] or 0),
            'total_net': float(paies_stats['total_net'] or 0),
            'nb_paies': paies_stats['nb_paies'] or 0
        },
        'heures_supplementaires': {
            'total_heures': float(heures_stats['total_heures'] or 0),
            'total_montant': float(heures_stats['total_montant'] or 0),
            'nb_heures_supp': heures_stats['nb_heures_supp'] or 0
        }
    }
