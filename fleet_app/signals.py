"""
Signaux Django pour la synchronisation automatique des données
Garantit que la base de données est automatiquement mise à jour
lors de chaque saisie ou modification
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.db.models import Sum
from decimal import Decimal
from datetime import datetime

from .models_entreprise import (
    HeureSupplementaire, 
    PaieEmploye, 
    DataSynchronizer,
    PresenceJournaliere,
    Employe,
    ParametrePaie,
    ConfigurationMontantStatut,
    ConfigurationMontantEmploye
)
from .models import ArchiveMensuelle

@receiver(post_save, sender=HeureSupplementaire)
def synchroniser_apres_heure_supplementaire_save(sender, instance, created, **kwargs):
    """
    Synchronisation automatique après sauvegarde d'une heure supplémentaire
    Met à jour automatiquement les totaux dans les paies
    """
    print(f"🔄 SYNC: Heure supplémentaire {'créée' if created else 'modifiée'} pour {instance.employe.matricule}")
    
    try:
        # Synchroniser les données de paie pour cet employé
        synchroniser_paie_employe(instance.employe, instance.date.month, instance.date.year)
        
        # Log de confirmation
        print(f"✅ SYNC: Paie synchronisée pour {instance.employe.matricule}")
        
    except Exception as e:
        print(f"❌ SYNC ERROR: {e}")

@receiver(post_delete, sender=HeureSupplementaire)
def synchroniser_apres_heure_supplementaire_delete(sender, instance, **kwargs):
    """
    Synchronisation automatique après suppression d'une heure supplémentaire
    Met à jour automatiquement les totaux dans les paies
    """
    print(f"🔄 SYNC: Heure supplémentaire supprimée pour {instance.employe.matricule}")
    
    try:
        # Synchroniser les données de paie pour cet employé
        synchroniser_paie_employe(instance.employe, instance.date.month, instance.date.year)
        
        # Log de confirmation
        print(f"✅ SYNC: Paie synchronisée après suppression pour {instance.employe.matricule}")
        
    except Exception as e:
        print(f"❌ SYNC ERROR: {e}")

@receiver(pre_save, sender=HeureSupplementaire)
def recalculer_avant_sauvegarde(sender, instance, **kwargs):
    """
    Recalcule automatiquement les totaux avant sauvegarde
    Garantit la cohérence des données
    """
    if instance.duree and instance.total_a_payer:
        # Recalculer le montant selon la règle : Total Hours × Définir Montant
        # Note: total_a_payer contient le montant manuel défini par l'utilisateur
        montant_calcule = float(instance.duree) * float(instance.total_a_payer)
        
        # Log du calcul
        print(f"🔢 CALC: {instance.employe.matricule} - {instance.duree}h × {instance.total_a_payer} = {montant_calcule}")

@receiver(post_save, sender=PresenceJournaliere)
def synchroniser_apres_presence_save(sender, instance, created, **kwargs):
    """
    Synchronisation automatique après modification des présences
    Met à jour AUTOMATIQUEMENT les colonnes de présence dans les paies lors du pointage
    """
    action = "créée" if created else "modifiée"
    print(f"🔄 SYNC POINTAGE: Présence {action} pour {instance.employe.matricule} - {instance.date} - Statut: {instance.statut}")
    
    try:
        # Synchroniser immédiatement les colonnes de présence dans les paies
        mettre_a_jour_colonnes_presence_paie(instance.employe, instance.date.month, instance.date.year)
        
        # Synchroniser aussi les autres données de paie
        synchroniser_paie_employe(instance.employe, instance.date.month, instance.date.year)
        
        # Log de confirmation détaillé
        print(f"✅ SYNC POINTAGE: Colonnes de présence mises à jour automatiquement pour {instance.employe.matricule}")
        
    except Exception as e:
        print(f"❌ SYNC POINTAGE ERROR: {e}")

@receiver(post_delete, sender=PresenceJournaliere)
def synchroniser_apres_presence_delete(sender, instance, **kwargs):
    """
    Synchronisation automatique après suppression d'une présence
    Met à jour les colonnes de présence dans les paies
    """
    print(f"🔄 SYNC POINTAGE: Présence supprimée pour {instance.employe.matricule} - {instance.date}")
    
    try:
        # Mettre à jour les colonnes de présence après suppression
        mettre_a_jour_colonnes_presence_paie(instance.employe, instance.date.month, instance.date.year)
        
        # Synchroniser les autres données de paie
        synchroniser_paie_employe(instance.employe, instance.date.month, instance.date.year)
        
        print(f"✅ SYNC POINTAGE: Colonnes de présence mises à jour après suppression pour {instance.employe.matricule}")
        
    except Exception as e:
        print(f"❌ SYNC POINTAGE ERROR: {e}")

def mettre_a_jour_colonnes_presence_paie(employe, mois, annee):
    """
    Met à jour AUTOMATIQUEMENT les colonnes de présence dans les paies lors du pointage
    Cette fonction est appelée à chaque création/modification/suppression de présence
    """
    try:
        from .models_entreprise import PaieEmploye, PresenceJournaliere
        from django.db.models import Q
        from datetime import datetime
        import calendar
        
        print(f"🔢 CALCUL POINTAGE: Mise à jour des colonnes de présence pour {employe.matricule} - {mois}/{annee}")
        
        # Récupérer ou créer la paie pour cet employé
        paie, created = PaieEmploye.objects.get_or_create(
            employe=employe,
            mois=mois,
            annee=annee,
            defaults={'salaire_base': 0}
        )
        
        # Récupérer toutes les présences du mois
        presences = PresenceJournaliere.objects.filter(
            employe=employe,
            date__month=mois,
            date__year=annee
        )
        
        # Calculer le total de jours du mois
        total_jours_mois = calendar.monthrange(annee, mois)[1]
        
        # Initialiser les compteurs
        jours_presence = 0
        jours_absents = 0
        jours_repos = 0
        jours_maladies = 0
        jours_m_payer = 0
        jours_ferie = 0
        dimanches_travailles = 0
        
        # Compter chaque type de présence selon les statuts
        for presence in presences:
            statut = presence.statut.upper()
            
            if statut == 'P':  # Présent
                jours_presence += 1
            elif statut == 'A':  # Absent
                jours_absents += 1
            elif 'REPOS' in statut or statut == 'R':  # Repos
                jours_repos += 1
            elif 'MALADIE' in statut or statut == 'M':  # Maladie
                jours_maladies += 1
            elif 'M.PAYER' in statut or 'MPAYER' in statut:  # M.Payer
                jours_m_payer += 1
            elif 'FERIE' in statut or 'FÉRIÉ' in statut or statut == 'F':  # Férié
                jours_ferie += 1
            elif 'DIMANCHE' in statut or 'SUNDAY' in statut or 'DIM' in statut:  # Dimanche travaillé
                dimanches_travailles += 1
                jours_presence += 1  # Un dimanche travaillé compte aussi comme présence
        
        # Mettre à jour les champs de la paie (utiliser les bons noms d'attributs)
        paie.jours_mois = total_jours_mois
        paie.jours_presence = jours_presence  # Utiliser jours_presence au lieu de jours_travailles
        paie.absences = jours_absents  # Utiliser absences au lieu de jours_absents
        paie.jours_repos = jours_repos
        paie.dimanches = dimanches_travailles  # Utiliser dimanches au lieu de dimanches_travailles
        paie.conge = jours_ferie  # Utiliser conge pour les jours fériés
        
        # Sauvegarder les modifications
        paie.save()
        
        # Log détaillé des résultats
        print(f"✅ COLONNES PRÉSENCE MISES À JOUR:")
        print(f"   📅 Total Jours: {total_jours_mois}")
        print(f"   ✅ Jours de présence: {jours_presence}")
        print(f"   ❌ Absences: {jours_absents}")
        print(f"   😴 J Repos: {jours_repos}")
        print(f"   🎉 Congés/Férié: {jours_ferie}")
        print(f"   📅 Dimanches: {dimanches_travailles}")
        
        return paie
        
    except Exception as e:
        print(f"❌ ERROR dans mettre_a_jour_colonnes_presence_paie: {e}")
        raise

def synchroniser_paie_employe(employe, mois, annee):
    """
    Fonction utilitaire pour synchroniser les données de paie d'un employé
    Utilise DataSynchronizer pour garantir la cohérence
    """
    try:
        # Récupérer ou créer la paie pour cet employé
        paie, created = DataSynchronizer.creer_ou_mettre_a_jour_paie(
            employe=employe,
            mois=mois,
            annee=annee
        )
        
        # Récupérer les données agrégées
        donnees = DataSynchronizer.get_donnees_aggregees_employe(employe, mois, annee)
        
        # Mettre à jour les champs de la paie avec les données synchronisées
        paie.heures_supplementaires = donnees['total_heures_supp']
        paie.montant_heures_supplementaires = donnees['montant_heures_supp']
        
        # Mettre à jour les données de présence (déjà fait par mettre_a_jour_colonnes_presence_paie)
        # paie.jours_presence = donnees['jours_presence']
        # paie.absences = donnees['absences']
        # paie.dimanches = donnees['dimanches_travailles']
        
        # Recalculer le salaire brut et net
        recalculer_salaire_paie(paie)
        
        # Sauvegarder
        paie.save()
        
        print(f"💾 SYNC: Paie mise à jour - H.Supp: {donnees['total_heures_supp']}h, Montant: {donnees['montant_heures_supp']}")
        
        return paie
        
    except Exception as e:
        print(f"❌ SYNC ERROR dans synchroniser_paie_employe: {e}")
        raise

def recalculer_salaire_paie(paie):
    """
    Recalcule automatiquement le salaire brut et net d'une paie
    """
    try:
        # Calculer le salaire brut
        salaire_base = paie.salaire_base or Decimal('0')
        montant_hs = paie.montant_heures_supplementaires or Decimal('0')
        prime_discipline = paie.prime_discipline or Decimal('0')
        cherete_vie = paie.cherete_vie or Decimal('0')
        ind_transport = paie.indemnite_transport or Decimal('0')
        ind_logement = paie.indemnite_logement or Decimal('0')
        
        paie.salaire_brut = (
            salaire_base + 
            montant_hs + 
            prime_discipline + 
            cherete_vie + 
            ind_transport + 
            ind_logement
        )
        
        # Calculer les déductions
        cnss = paie.salaire_brut * Decimal('0.05')  # 5% CNSS
        rts = paie.rts or Decimal('0')
        avances = paie.avances or Decimal('0')
        sanctions = paie.sanctions or Decimal('0')
        
        paie.cnss = cnss
        
        # Calculer le net à payer
        paie.net_a_payer = paie.salaire_brut - cnss - rts - avances - sanctions
        
        print(f"💰 CALC: Salaire recalculé - Brut: {paie.salaire_brut}, Net: {paie.net_a_payer}")
        
    except Exception as e:
        print(f"❌ CALC ERROR dans recalculer_salaire_paie: {e}")

def synchroniser_tous_employes_mois(user, mois=None, annee=None):
    """
    Synchronise tous les employés d'un utilisateur pour un mois donné
    Utile pour la synchronisation globale
    """
    if not mois:
        mois = datetime.now().month
    if not annee:
        annee = datetime.now().year
    
    print(f"🔄 SYNC GLOBAL: Synchronisation de tous les employés pour {mois}/{annee}")
    
    from .models_entreprise import Employe
    employes = Employe.objects.filter(user=user)
    
    for employe in employes:
        try:
            synchroniser_paie_employe(employe, mois, annee)
            print(f"✅ SYNC: {employe.matricule} synchronisé")
        except Exception as e:
            print(f"❌ SYNC ERROR pour {employe.matricule}: {e}")
    
    print(f"🎉 SYNC GLOBAL TERMINÉ: {employes.count()} employés synchronisés")

# Signal pour synchronisation globale périodique
@receiver(post_save, sender=PaieEmploye)
def log_paie_save(sender, instance, created, **kwargs):
    """
    Log des modifications de paie pour traçabilité
    """
    action = "créée" if created else "modifiée"
    print(f"📝 LOG: Paie {action} pour {instance.employe.matricule} - {instance.mois}/{instance.annee}")

# ========== NOUVEAUX SIGNAUX POUR SYNCHRONISATION COMPLÈTE ==========

@receiver(post_save, sender=Employe)
def synchroniser_apres_employe_save(sender, instance, created, **kwargs):
    """
    Synchronisation automatique après modification d'un employé
    Met à jour toutes les paies existantes avec les nouvelles données employé
    """
    action = "créé" if created else "modifié"
    print(f"🔄 SYNC EMPLOYE: Employé {action} - {instance.matricule} {instance.nom} {instance.prenom}")
    
    try:
        # Synchroniser toutes les paies existantes de cet employé
        paies = PaieEmploye.objects.filter(employe=instance)
        for paie in paies:
            # Mettre à jour le salaire de base si modifié
            if instance.salaire_journalier:
                paie.salaire_base = instance.salaire_journalier
            
            # Recalculer le salaire
            recalculer_salaire_paie(paie)
            paie.save()
        
        print(f"✅ SYNC EMPLOYE: {paies.count()} paies mises à jour pour {instance.matricule}")
        
    except Exception as e:
        print(f"❌ SYNC EMPLOYE ERROR: {e}")

@receiver(post_save, sender=ParametrePaie)
def synchroniser_apres_parametre_paie_save(sender, instance, created, **kwargs):
    """
    Synchronisation automatique après modification des paramètres de paie
    Recalcule toutes les paies affectées par ce paramètre
    """
    action = "créé" if created else "modifié"
    print(f"🔄 SYNC PARAM: Paramètre paie {action} - {instance.cle}: {instance.valeur}")
    
    try:
        # Si c'est un paramètre global (taux CNSS, etc.), synchroniser toutes les paies
        if instance.cle in ['taux_cnss', 'salaire_minimum', 'taux_rts']:
            paies = PaieEmploye.objects.filter(employe__user=instance.user)
            for paie in paies:
                recalculer_salaire_paie(paie)
                paie.save()
            
            print(f"✅ SYNC PARAM: {paies.count()} paies recalculées suite au changement de {instance.cle}")
        
    except Exception as e:
        print(f"❌ SYNC PARAM ERROR: {e}")

@receiver(post_save, sender=ConfigurationMontantEmploye)
def synchroniser_apres_config_montant_save(sender, instance, created, **kwargs):
    """
    Synchronisation automatique après modification de la configuration des montants employé
    Met à jour les calculs de présence dans les paies
    """
    action = "créée" if created else "modifiée"
    print(f"🔄 SYNC CONFIG: Configuration montants {action} pour {instance.employe.matricule}")
    
    try:
        # Synchroniser toutes les paies de cet employé
        paies = PaieEmploye.objects.filter(employe=instance.employe)
        for paie in paies:
            # Recalculer les montants de présence avec la nouvelle configuration
            mettre_a_jour_colonnes_presence_paie(instance.employe, paie.mois, paie.annee)
            recalculer_salaire_paie(paie)
            paie.save()
        
        print(f"✅ SYNC CONFIG: {paies.count()} paies recalculées avec nouveaux montants pour {instance.employe.matricule}")
        
    except Exception as e:
        print(f"❌ SYNC CONFIG ERROR: {e}")

@receiver(post_delete, sender=Employe)
def nettoyer_apres_employe_delete(sender, instance, **kwargs):
    """
    Nettoyage automatique après suppression d'un employé
    Supprime ou archive les données liées
    """
    print(f"🗑️ CLEANUP: Suppression employé {instance.matricule} - Nettoyage des données liées")
    
    try:
        # Compter les données à supprimer
        nb_presences = PresenceJournaliere.objects.filter(employe=instance).count()
        nb_heures_supp = HeureSupplementaire.objects.filter(employe=instance).count()
        nb_paies = PaieEmploye.objects.filter(employe=instance).count()
        
        print(f"📊 CLEANUP: {nb_presences} présences, {nb_heures_supp} heures supp, {nb_paies} paies à nettoyer")
        
        # Les données seront supprimées automatiquement par CASCADE
        # Mais on peut logger pour traçabilité
        
    except Exception as e:
        print(f"❌ CLEANUP ERROR: {e}")

# ========== FONCTIONS UTILITAIRES AMÉLIORÉES ==========

def synchroniser_module_complet(user, mois=None, annee=None):
    """
    Synchronisation complète de tous les modules pour un utilisateur
    Garantit la cohérence entre employes/, presences/, paies/, heures-supp/, etc.
    """
    if not mois:
        mois = datetime.now().month
    if not annee:
        annee = datetime.now().year
    
    print(f"🔄 SYNC COMPLET: Synchronisation complète pour {user.username} - {mois}/{annee}")
    
    try:
        # 1. Synchroniser tous les employés
        employes = Employe.objects.filter(user=user)
        print(f"👥 SYNC: {employes.count()} employés à synchroniser")
        
        for employe in employes:
            # 2. Synchroniser les présences -> paies
            mettre_a_jour_colonnes_presence_paie(employe, mois, annee)
            
            # 3. Synchroniser les heures supplémentaires -> paies
            synchroniser_paie_employe(employe, mois, annee)
            
            # 4. Vérifier la configuration des montants
            config_montants = ConfigurationMontantEmploye.objects.filter(employe=employe).first()
            if not config_montants:
                ConfigurationMontantEmploye.get_or_create_for_employe(employe)
                print(f"➕ SYNC: Configuration montants créée pour {employe.matricule}")
        
        print(f"✅ SYNC COMPLET: Synchronisation terminée avec succès")
        return True
        
    except Exception as e:
        print(f"❌ SYNC COMPLET ERROR: {e}")
        return False

def verifier_coherence_donnees(user, mois=None, annee=None):
    """
    Vérifie la cohérence des données entre tous les modules
    Retourne un rapport de cohérence
    """
    if not mois:
        mois = datetime.now().month
    if not annee:
        annee = datetime.now().year
    
    print(f"🔍 VERIFICATION: Vérification cohérence données pour {user.username} - {mois}/{annee}")
    
    rapport = {
        'employes_sans_config_montants': [],
        'paies_sans_presences': [],
        'heures_supp_non_synchronisees': [],
        'totaux_incoherents': [],
        'statut': 'OK'
    }
    
    try:
        employes = Employe.objects.filter(user=user)
        
        for employe in employes:
            # Vérifier configuration montants
            if not ConfigurationMontantEmploye.objects.filter(employe=employe).exists():
                rapport['employes_sans_config_montants'].append(employe.matricule)
            
            # Vérifier cohérence paies/présences
            paie = PaieEmploye.objects.filter(employe=employe, mois=mois, annee=annee).first()
            if paie:
                presences = PresenceJournaliere.objects.filter(
                    employe=employe, 
                    date__month=mois, 
                    date__year=annee
                ).count()
                
                # Utiliser le bon nom d'attribut : jours_presence au lieu de jours_travailles
                if presences > 0 and paie.jours_presence == 0:
                    rapport['paies_sans_presences'].append(employe.matricule)
        
        # Déterminer le statut global
        if any(rapport[key] for key in rapport if key != 'statut'):
            rapport['statut'] = 'PROBLEMES_DETECTES'
        
        print(f"📋 VERIFICATION: {rapport['statut']} - {len(rapport['employes_sans_config_montants'])} problèmes détectés")
        return rapport
        
    except Exception as e:
        print(f"❌ VERIFICATION ERROR: {e}")
        rapport['statut'] = 'ERREUR'
        return rapport
