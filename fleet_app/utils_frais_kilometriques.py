"""
Utilitaires pour la gestion des frais kilométriques (Bonus/Km)
et leur intégration avec le système de paie
"""

from decimal import Decimal
from django.db.models import Sum
from .models_entreprise import FraisKilometrique, PaieEmploye, Employe


def calculer_frais_km_mois(employe, mois, annee):
    """
    Calcule le total des frais kilométriques pour un employé sur un mois donné
    
    Args:
        employe: Instance de Employe
        mois: Numéro du mois (1-12)
        annee: Année (ex: 2025)
    
    Returns:
        dict: {
            'total_montant': Decimal,
            'total_km': Decimal,
            'nombre_trajets': int,
            'details': QuerySet
        }
    """
    frais = FraisKilometrique.objects.filter(
        employe=employe,
        date__month=mois,
        date__year=annee
    ).order_by('date')
    
    total_montant = frais.aggregate(total=Sum('total_a_payer'))['total'] or Decimal('0')
    total_km = frais.aggregate(total=Sum('kilometres'))['total'] or Decimal('0')
    
    return {
        'total_montant': total_montant,
        'total_km': total_km,
        'nombre_trajets': frais.count(),
        'details': frais
    }


def synchroniser_frais_km_avec_paie(employe, mois, annee):
    """
    Synchronise les frais kilométriques avec la paie de l'employé
    Met à jour automatiquement le champ montant_frais_kilometriques dans PaieEmploye
    
    Args:
        employe: Instance de Employe
        mois: Numéro du mois (1-12)
        annee: Année (ex: 2025)
    
    Returns:
        tuple: (paie_updated, montant_frais_km)
    """
    # Calculer le total des frais kilométriques
    frais_data = calculer_frais_km_mois(employe, mois, annee)
    montant_frais_km = frais_data['total_montant']
    
    # Récupérer ou créer la paie
    try:
        paie = PaieEmploye.objects.get(
            employe=employe,
            mois=mois,
            annee=annee
        )
        
        # Mettre à jour le montant des frais kilométriques
        paie.montant_frais_kilometriques = montant_frais_km
        
        # Recalculer le salaire brut (ajouter les frais km)
        paie.salaire_brut = (
            paie.montant_jours_travailles +
            paie.montant_heures_supplementaires +
            paie.montant_heures_supplement_dimanches +
            paie.montant_frais_kilometriques +
            paie.indemnite_transport +
            paie.indemnite_logement +
            paie.cherete_vie +
            paie.prime_discipline +
            paie.prime_ferie
        )
        
        # Recalculer le salaire net
        total_deductions = (
            paie.cnss +
            paie.rts +
            paie.vf +
            paie.avance_sur_salaire +
            paie.sanction_vol_carburant
        )
        
        paie.salaire_net = paie.salaire_brut - total_deductions
        paie.salaire_net_a_payer = paie.salaire_net
        
        paie.save()
        
        return (True, montant_frais_km)
        
    except PaieEmploye.DoesNotExist:
        # La paie n'existe pas encore, retourner juste le montant
        return (False, montant_frais_km)


def obtenir_resume_frais_km_employe(employe, mois, annee):
    """
    Obtient un résumé détaillé des frais kilométriques d'un employé
    
    Args:
        employe: Instance de Employe
        mois: Numéro du mois (1-12)
        annee: Année (ex: 2025)
    
    Returns:
        dict: Résumé complet avec statistiques
    """
    frais_data = calculer_frais_km_mois(employe, mois, annee)
    
    # Calculer la moyenne par trajet
    moyenne_km_trajet = 0
    moyenne_montant_trajet = 0
    
    if frais_data['nombre_trajets'] > 0:
        moyenne_km_trajet = float(frais_data['total_km']) / frais_data['nombre_trajets']
        moyenne_montant_trajet = float(frais_data['total_montant']) / frais_data['nombre_trajets']
    
    # Obtenir la valeur par km configurée
    valeur_km_config = employe.valeur_km or 0
    
    return {
        'employe': employe,
        'mois': mois,
        'annee': annee,
        'total_montant': frais_data['total_montant'],
        'total_km': frais_data['total_km'],
        'nombre_trajets': frais_data['nombre_trajets'],
        'moyenne_km_trajet': round(moyenne_km_trajet, 2),
        'moyenne_montant_trajet': round(moyenne_montant_trajet, 2),
        'valeur_km_configuree': valeur_km_config,
        'details': frais_data['details']
    }


def obtenir_statistiques_globales_mois(user, mois, annee):
    """
    Obtient les statistiques globales des frais kilométriques pour tous les employés
    
    Args:
        user: Utilisateur propriétaire
        mois: Numéro du mois (1-12)
        annee: Année (ex: 2025)
    
    Returns:
        dict: Statistiques globales
    """
    # Tous les frais du mois pour cet utilisateur
    frais_mois = FraisKilometrique.objects.filter(
        employe__user=user,
        date__month=mois,
        date__year=annee
    )
    
    total_montant = frais_mois.aggregate(total=Sum('total_a_payer'))['total'] or Decimal('0')
    total_km = frais_mois.aggregate(total=Sum('kilometres'))['total'] or Decimal('0')
    nombre_trajets = frais_mois.count()
    
    # Nombre d'employés ayant des frais ce mois
    employes_avec_frais = frais_mois.values('employe').distinct().count()
    
    # Moyenne par trajet
    moyenne_km_trajet = 0
    moyenne_montant_trajet = 0
    
    if nombre_trajets > 0:
        moyenne_km_trajet = float(total_km) / nombre_trajets
        moyenne_montant_trajet = float(total_montant) / nombre_trajets
    
    return {
        'mois': mois,
        'annee': annee,
        'total_montant': total_montant,
        'total_km': total_km,
        'nombre_trajets': nombre_trajets,
        'nombre_employes': employes_avec_frais,
        'moyenne_km_trajet': round(moyenne_km_trajet, 2),
        'moyenne_montant_trajet': round(moyenne_montant_trajet, 2)
    }


def exporter_frais_km_csv(user, mois, annee):
    """
    Exporte les frais kilométriques au format CSV
    
    Args:
        user: Utilisateur propriétaire
        mois: Numéro du mois (1-12)
        annee: Année (ex: 2025)
    
    Returns:
        list: Liste de dictionnaires pour export CSV
    """
    frais = FraisKilometrique.objects.filter(
        employe__user=user,
        date__month=mois,
        date__year=annee
    ).select_related('employe').order_by('employe__matricule', 'date')
    
    data = []
    for f in frais:
        data.append({
            'Matricule': f.employe.matricule,
            'Prénom': f.employe.prenom,
            'Nom': f.employe.nom,
            'Fonction': f.employe.fonction or '',
            'Date': f.date.strftime('%d/%m/%Y'),
            'Kilomètres': float(f.kilometres),
            'Valeur/Km': float(f.get_valeur_km()),
            'Total': float(f.total_a_payer),
            'Description': f.description or ''
        })
    
    return data
