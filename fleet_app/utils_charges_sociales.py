"""
Utilitaires pour le calcul des charges sociales guinéennes.

Ce module contient les fonctions de calcul pour :
- CNSS (Caisse Nationale de Sécurité Sociale) : 5% salarié + 18% employeur
- RTS (Retenue sur Traitement et Salaire) : barème progressif par tranches
- VF (Versement Forfaitaire) : 7-10% du chiffre d'affaires

Conforme à la réglementation guinéenne en vigueur.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Tuple


# === CONSTANTES OFFICIELLES ===

# Taux CNSS standards (en pourcentage)
TAUX_CNSS_SALARIE = Decimal('5.00')  # 5% du salaire brut
TAUX_CNSS_EMPLOYEUR = Decimal('18.00')  # 18% du salaire brut

# Barème RTS progressif (montants en GNF, taux en pourcentage)
BAREME_RTS = [
    {'min': 0, 'max': 1000000, 'taux': Decimal('0.00')},      # 0 à 1M : 0%
    {'min': 1000001, 'max': 1500000, 'taux': Decimal('10.00')},  # 1M à 1.5M : 10%
    {'min': 1500001, 'max': 2000000, 'taux': Decimal('15.00')},  # 1.5M à 2M : 15%
    {'min': 2000001, 'max': 4000000, 'taux': Decimal('20.00')},  # 2M à 4M : 20%
    {'min': 4000001, 'max': 6000000, 'taux': Decimal('25.00')},  # 4M à 6M : 25%
    {'min': 6000001, 'max': float('inf'), 'taux': Decimal('35.00')},  # Plus de 6M : 35%
]

# Taux VF standards (en pourcentage)
TAUX_VF_MIN = Decimal('7.00')   # 7% minimum
TAUX_VF_MAX = Decimal('10.00')  # 10% maximum


def calculer_cnss_salarie(salaire_brut: Decimal, taux_custom: Decimal = None) -> Decimal:
    """
    Calcule la cotisation CNSS à la charge du salarié.
    
    Args:
        salaire_brut: Salaire brut mensuel en GNF
        taux_custom: Taux personnalisé (optionnel, sinon 5%)
    
    Returns:
        Montant CNSS salarié en GNF
    """
    taux = taux_custom if taux_custom is not None else TAUX_CNSS_SALARIE
    montant = salaire_brut * taux / Decimal('100')
    return montant.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculer_cnss_employeur(salaire_brut: Decimal, taux_custom: Decimal = None) -> Decimal:
    """
    Calcule la cotisation CNSS à la charge de l'employeur.
    
    Args:
        salaire_brut: Salaire brut mensuel en GNF
        taux_custom: Taux personnalisé (optionnel, sinon 18%)
    
    Returns:
        Montant CNSS employeur en GNF
    """
    taux = taux_custom if taux_custom is not None else TAUX_CNSS_EMPLOYEUR
    montant = salaire_brut * taux / Decimal('100')
    return montant.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculer_rts_par_tranche(salaire_net_imposable: Decimal) -> Dict:
    """
    Calcule la RTS selon le barème progressif par tranches.
    
    Args:
        salaire_net_imposable: Salaire après déduction CNSS salarié
    
    Returns:
        Dict avec détail par tranche et total RTS
    """
    if salaire_net_imposable <= 0:
        return {
            'total_rts': Decimal('0.00'),
            'detail_tranches': [],
            'salaire_net_imposable': salaire_net_imposable
        }
    
    total_rts = Decimal('0.00')
    detail_tranches = []
    
    for tranche in BAREME_RTS:
        tranche_min = Decimal(str(tranche['min']))
        tranche_max = Decimal(str(tranche['max'])) if tranche['max'] != float('inf') else None
        taux = tranche['taux']
        
        # Déterminer la portion du salaire dans cette tranche
        if salaire_net_imposable <= tranche_min:
            continue  # Salaire trop bas pour cette tranche
        
        if tranche_max is None:  # Tranche illimitée (plus de 6M)
            montant_tranche = salaire_net_imposable - tranche_min + 1
        else:
            montant_tranche = min(salaire_net_imposable, tranche_max) - tranche_min + 1
        
        if montant_tranche > 0:
            rts_tranche = montant_tranche * taux / Decimal('100')
            total_rts += rts_tranche
            
            detail_tranches.append({
                'tranche': f"{tranche_min:,.0f} - {tranche_max:,.0f}" if tranche_max else f"Plus de {tranche_min:,.0f}",
                'montant_tranche': montant_tranche,
                'taux': taux,
                'rts_tranche': rts_tranche.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            })
    
    return {
        'total_rts': total_rts.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        'detail_tranches': detail_tranches,
        'salaire_net_imposable': salaire_net_imposable
    }


def calculer_vf(chiffre_affaires: Decimal, taux_custom: Decimal = None) -> Decimal:
    """
    Calcule le Versement Forfaitaire.
    
    Args:
        chiffre_affaires: Chiffre d'affaires mensuel/trimestriel en GNF
        taux_custom: Taux personnalisé (optionnel, entre 7% et 10%)
    
    Returns:
        Montant VF en GNF
    """
    if taux_custom is not None:
        taux = max(TAUX_VF_MIN, min(taux_custom, TAUX_VF_MAX))  # Borner entre 7% et 10%
    else:
        taux = TAUX_VF_MIN  # Utiliser 7% par défaut
    
    montant = chiffre_affaires * taux / Decimal('100')
    return montant.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculer_salaire_complet(salaire_brut: Decimal, employe_config: Dict) -> Dict:
    """
    Calcule un salaire complet avec toutes les charges sociales.
    
    Args:
        salaire_brut: Salaire brut mensuel en GNF
        employe_config: Configuration de l'employé (CNSS, RTS, VF, taux custom)
    
    Returns:
        Dict avec tous les calculs détaillés
    """
    resultat = {
        'salaire_brut': salaire_brut,
        'cnss_salarie': Decimal('0.00'),
        'cnss_employeur': Decimal('0.00'),
        'salaire_net_imposable': salaire_brut,
        'rts_detail': {},
        'rts_total': Decimal('0.00'),
        'vf': Decimal('0.00'),
        'total_deductions': Decimal('0.00'),
        'salaire_net_a_payer': salaire_brut,
        'cout_total_employeur': salaire_brut
    }
    
    # 1. CALCUL CNSS
    if employe_config.get('appliquer_cnss', True):
        taux_cnss_salarie = employe_config.get('taux_cnss_salarie_custom')
        taux_cnss_employeur = employe_config.get('taux_cnss_employeur_custom')
        
        resultat['cnss_salarie'] = calculer_cnss_salarie(salaire_brut, taux_cnss_salarie)
        resultat['cnss_employeur'] = calculer_cnss_employeur(salaire_brut, taux_cnss_employeur)
        
        # Salaire net imposable = Salaire brut - CNSS salarié
        resultat['salaire_net_imposable'] = salaire_brut - resultat['cnss_salarie']
    
    # 2. CALCUL RTS
    if employe_config.get('appliquer_rts', True):
        rts_calcul = calculer_rts_par_tranche(resultat['salaire_net_imposable'])
        resultat['rts_detail'] = rts_calcul
        resultat['rts_total'] = rts_calcul['total_rts']
    
    # 3. CALCUL VF (si applicable)
    if employe_config.get('appliquer_vf', False):
        # Pour VF, on utilise le salaire brut comme base de calcul
        taux_vf = employe_config.get('taux_vf_custom')
        resultat['vf'] = calculer_vf(salaire_brut, taux_vf)
    
    # 4. TOTAUX
    resultat['total_deductions'] = (
        resultat['cnss_salarie'] + 
        resultat['rts_total'] + 
        resultat['vf']
    )
    
    resultat['salaire_net_a_payer'] = salaire_brut - resultat['total_deductions']
    resultat['cout_total_employeur'] = salaire_brut + resultat['cnss_employeur']
    
    return resultat


def calculer_salaire_base_depuis_presences(employe, mois, annee) -> Decimal:
    """
    Calcule le salaire de base d'un employé à partir de ses présences du mois.
    
    Args:
        employe: Instance du modèle Employe
        mois: Mois (1-12)
        annee: Année
    
    Returns:
        Salaire de base calculé en GNF
    """
    from .models import PresenceJournaliere
    from .models_entreprise import ConfigurationMontantEmploye
    
    # Récupérer les présences du mois
    presences = PresenceJournaliere.objects.filter(
        employe=employe,
        date__month=mois,
        date__year=annee
    )
    
    # Récupérer la configuration des montants pour cet employé
    config_montant = ConfigurationMontantEmploye.objects.filter(employe=employe).first()
    
    if not config_montant:
        # Si pas de configuration, utiliser le salaire journalier par défaut
        return employe.salaire_journalier * presences.count()
    
    # Calculer selon les statuts de présence
    salaire_total = Decimal('0.00')
    
    for presence in presences:
        if presence.statut == 'P(Am)':  # Présent matin
            salaire_total += config_montant.montant_am
        elif presence.statut == 'P(Pm)':  # Présent après-midi
            salaire_total += config_montant.montant_pm
        elif presence.statut == 'P(Am&Pm)':  # Présent journée complète
            salaire_total += config_montant.montant_journee
        elif presence.statut == 'Dimanche':  # Dimanche travaillé
            salaire_total += config_montant.montant_dim_journee
        # Les autres statuts (Absent, Maladie, etc.) peuvent avoir des montants différents
        # mais ne contribuent généralement pas au salaire de base
    
    return salaire_total.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def generer_fiche_paie_complete(employe, mois, annee) -> Dict:
    """
    Génère une fiche de paie complète avec tous les calculs.
    
    Args:
        employe: Instance du modèle Employe
        mois: Mois (1-12)
        annee: Année
    
    Returns:
        Dict avec tous les éléments de la fiche de paie
    """
    # 1. Calculer le salaire de base depuis les présences
    if employe.calcul_salaire_auto:
        salaire_base = calculer_salaire_base_depuis_presences(employe, mois, annee)
    else:
        salaire_base = employe.salaire_journalier
    
    # 2. Configuration des charges sociales
    config_charges = {
        'appliquer_cnss': employe.appliquer_cnss,
        'appliquer_rts': employe.appliquer_rts,
        'appliquer_vf': employe.appliquer_vf,
        'taux_cnss_salarie_custom': employe.taux_cnss_salarie_custom,
        'taux_cnss_employeur_custom': employe.taux_cnss_employeur_custom,
        'taux_vf_custom': employe.taux_vf_custom,
    }
    
    # 3. Calculer tous les éléments de paie
    calculs = calculer_salaire_complet(salaire_base, config_charges)
    
    # 4. Ajouter les informations de l'employé
    fiche_paie = {
        'employe': {
            'matricule': employe.matricule,
            'nom': employe.nom,
            'prenom': employe.prenom,
            'fonction': employe.fonction,
        },
        'periode': {
            'mois': mois,
            'annee': annee,
        },
        'calculs': calculs,
        'config_charges': config_charges,
        'salaire_base_auto': employe.calcul_salaire_auto,
    }
    
    return fiche_paie


def obtenir_resume_charges_sociales() -> Dict:
    """
    Retourne un résumé des taux et barèmes des charges sociales guinéennes.
    
    Returns:
        Dict avec tous les taux et barèmes
    """
    return {
        'cnss': {
            'taux_salarie': float(TAUX_CNSS_SALARIE),
            'taux_employeur': float(TAUX_CNSS_EMPLOYEUR),
            'description': 'Caisse Nationale de Sécurité Sociale'
        },
        'rts': {
            'bareme': [
                {
                    'tranche': f"{b['min']:,} - {b['max']:,}" if b['max'] != float('inf') else f"Plus de {b['min']:,}",
                    'taux': float(b['taux'])
                }
                for b in BAREME_RTS
            ],
            'description': 'Retenue sur Traitement et Salaire (progressif par tranches)'
        },
        'vf': {
            'taux_min': float(TAUX_VF_MIN),
            'taux_max': float(TAUX_VF_MAX),
            'description': 'Versement Forfaitaire (7-10% du chiffre d\'affaires)'
        }
    }
