"""
Utilitaires pour calculer automatiquement les informations de présence 
depuis pointage/ vers paies/

Formules de calcul :
- Jours de présence = nombre de P(Am_&_Pm) + P(Pm) + P(Am)
- Sundays = P(dim_Am) + P(dim_Pm) + P(dim_Am_&_Pm)
- Absent = nombre A
- Maladies = nombre de M
- M.Payer = nombre M(Payer)
- J Repos = nombre de OFF
"""

from django.db.models import Count, Q
from datetime import datetime
from .models_entreprise import PresenceJournaliere, PaieEmploye, Employe


def calculer_statistiques_presence(employe, mois, annee):
    """
    Calcule les statistiques de présence pour un employé sur un mois donné
    selon les formules spécifiées par l'utilisateur
    
    Args:
        employe: Instance de l'employé
        mois: Mois (1-12)
        annee: Année
        
    Returns:
        dict: Dictionnaire avec toutes les statistiques calculées
    """
    
    # Récupérer toutes les présences du mois
    presences = PresenceJournaliere.objects.filter(
        employe=employe,
        date__month=mois,
        date__year=annee
    )
    
    # Calculer selon les formules spécifiées
    statistiques = {
        # Jours de présence = P(Am_&_Pm) + P(Pm) + P(Am)
        'jours_presence': presences.filter(
            Q(statut='P(Am_&_Pm)') | Q(statut='P(Pm)') | Q(statut='P(Am)')
        ).count(),
        
        # Sundays = P(dim_Am) + P(dim_Pm) + P(dim_Am_&_Pm)
        'sundays': presences.filter(
            Q(statut='P(dim_Am)') | Q(statut='P(dim_Pm)') | Q(statut='P(dim_Am_&_Pm)')
        ).count(),
        
        # Absent = nombre A
        'absent': presences.filter(statut='A').count(),
        
        # Maladies = nombre de M
        'maladies': presences.filter(statut='M').count(),
        
        # M.Payer = nombre M(Payer)
        'm_payer': presences.filter(statut='M(Payer)').count(),
        
        # J Repos = nombre de OFF
        'j_repos': presences.filter(statut='OFF').count(),
        
        # Total des jours du mois (pour référence)
        'total_jours_mois': get_jours_dans_mois(mois, annee),
        
        # Détail par statut pour debug
        'detail_statuts': {}
    }
    
    # Ajouter le détail par statut pour vérification
    for statut_code, statut_label in PresenceJournaliere.STATUT_CHOICES:
        count = presences.filter(statut=statut_code).count()
        if count > 0:
            statistiques['detail_statuts'][statut_code] = {
                'label': statut_label,
                'count': count
            }
    
    return statistiques


def get_jours_dans_mois(mois, annee):
    """
    Retourne le nombre de jours dans un mois donné
    """
    import calendar
    return calendar.monthrange(annee, mois)[1]


def synchroniser_presence_vers_paie(employe, mois, annee):
    """
    Synchronise automatiquement les données de présence vers la paie
    Crée ou met à jour l'enregistrement de paie avec les données calculées
    
    Args:
        employe: Instance de l'employé
        mois: Mois (1-12)
        annee: Année
        
    Returns:
        tuple: (paie_employe, created, statistiques)
    """
    
    # Calculer les statistiques de présence
    stats = calculer_statistiques_presence(employe, mois, annee)
    
    # Récupérer ou créer l'enregistrement de paie
    paie_employe, created = PaieEmploye.objects.get_or_create(
        employe=employe,
        mois=mois,
        annee=annee,
        defaults={
            'salaire_base': employe.salaire_base if hasattr(employe, 'salaire_base') else 0,
            'jours_mois': stats['total_jours_mois']
        }
    )
    
    # Mettre à jour les champs calculés selon les formules
    paie_employe.jours_presence = stats['jours_presence']
    paie_employe.dimanches = stats['sundays']  # Sundays dans le modèle
    paie_employe.absences = stats['absent']
    paie_employe.jours_repos = stats['j_repos']
    
    # Note: Les maladies sont calculées dynamiquement via les méthodes du modèle
    # car les champs dédiés n'existent pas encore en base de données
    
    # Sauvegarder
    paie_employe.save()
    
    return paie_employe, created, stats


def synchroniser_tous_employes_mois(user, mois, annee):
    """
    Synchronise les données de présence vers paie pour tous les employés d'un utilisateur
    pour un mois donné
    
    Args:
        user: Utilisateur
        mois: Mois (1-12)
        annee: Année
        
    Returns:
        dict: Rapport de synchronisation
    """
    
    employes = Employe.objects.filter(user=user, statut='Actif')
    
    rapport = {
        'mois': mois,
        'annee': annee,
        'total_employes': employes.count(),
        'employes_synchronises': 0,
        'employes_crees': 0,
        'employes_mis_a_jour': 0,
        'erreurs': [],
        'details': []
    }
    
    for employe in employes:
        try:
            paie_employe, created, stats = synchroniser_presence_vers_paie(employe, mois, annee)
            
            rapport['employes_synchronises'] += 1
            if created:
                rapport['employes_crees'] += 1
            else:
                rapport['employes_mis_a_jour'] += 1
            
            rapport['details'].append({
                'employe': {
                    'matricule': employe.matricule,
                    'nom': f"{employe.prenom} {employe.nom}"
                },
                'created': created,
                'statistiques': stats
            })
            
        except Exception as e:
            rapport['erreurs'].append({
                'employe': {
                    'matricule': employe.matricule,
                    'nom': f"{employe.prenom} {employe.nom}"
                },
                'erreur': str(e)
            })
    
    return rapport


def generer_rapport_presence_mois(user, mois, annee):
    """
    Génère un rapport détaillé des présences pour un mois donné
    
    Args:
        user: Utilisateur
        mois: Mois (1-12)
        annee: Année
        
    Returns:
        dict: Rapport détaillé
    """
    
    employes = Employe.objects.filter(user=user, statut='Actif')
    
    rapport = {
        'periode': f"{mois:02d}/{annee}",
        'total_employes': employes.count(),
        'employes': [],
        'resume_global': {
            'total_jours_presence': 0,
            'total_sundays': 0,
            'total_absences': 0,
            'total_maladies': 0,
            'total_maladies_payees': 0,
            'total_jours_repos': 0
        }
    }
    
    for employe in employes:
        stats = calculer_statistiques_presence(employe, mois, annee)
        
        employe_data = {
            'employe': {
                'id': employe.id,
                'matricule': employe.matricule,
                'nom': f"{employe.prenom} {employe.nom}",
                'profession': employe.profession
            },
            'statistiques': stats
        }
        
        rapport['employes'].append(employe_data)
        
        # Mettre à jour le résumé global
        rapport['resume_global']['total_jours_presence'] += stats['jours_presence']
        rapport['resume_global']['total_sundays'] += stats['sundays']
        rapport['resume_global']['total_absences'] += stats['absent']
        rapport['resume_global']['total_maladies'] += stats['maladies']
        rapport['resume_global']['total_maladies_payees'] += stats['m_payer']
        rapport['resume_global']['total_jours_repos'] += stats['j_repos']
    
    return rapport


def verifier_coherence_presence_paie(user, mois, annee):
    """
    Vérifie la cohérence entre les données de présence et de paie
    
    Args:
        user: Utilisateur
        mois: Mois (1-12)
        annee: Année
        
    Returns:
        dict: Rapport de vérification
    """
    
    employes = Employe.objects.filter(user=user, statut='Actif')
    
    rapport = {
        'periode': f"{mois:02d}/{annee}",
        'employes_verifies': 0,
        'employes_coherents': 0,
        'employes_incoherents': 0,
        'problemes': []
    }
    
    for employe in employes:
        rapport['employes_verifies'] += 1
        
        # Calculer les stats depuis les présences
        stats_presence = calculer_statistiques_presence(employe, mois, annee)
        
        # Récupérer les données de paie
        try:
            paie = PaieEmploye.objects.get(employe=employe, mois=mois, annee=annee)
            
            # Vérifier la cohérence
            problemes_employe = []
            
            if paie.jours_presence != stats_presence['jours_presence']:
                problemes_employe.append(f"Jours présence: paie={paie.jours_presence}, présence={stats_presence['jours_presence']}")
            
            if paie.dimanches != stats_presence['sundays']:
                problemes_employe.append(f"Sundays: paie={paie.dimanches}, présence={stats_presence['sundays']}")
            
            if paie.absences != stats_presence['absent']:
                problemes_employe.append(f"Absences: paie={paie.absences}, présence={stats_presence['absent']}")
            
            if paie.jours_repos != stats_presence['j_repos']:
                problemes_employe.append(f"Jours repos: paie={paie.jours_repos}, présence={stats_presence['j_repos']}")
            
            if problemes_employe:
                rapport['employes_incoherents'] += 1
                rapport['problemes'].append({
                    'employe': {
                        'matricule': employe.matricule,
                        'nom': f"{employe.prenom} {employe.nom}"
                    },
                    'problemes': problemes_employe
                })
            else:
                rapport['employes_coherents'] += 1
                
        except PaieEmploye.DoesNotExist:
            rapport['employes_incoherents'] += 1
            rapport['problemes'].append({
                'employe': {
                    'matricule': employe.matricule,
                    'nom': f"{employe.prenom} {employe.nom}"
                },
                'problemes': ['Aucune paie trouvée pour cette période']
            })
    
    return rapport
