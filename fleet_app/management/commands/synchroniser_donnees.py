"""
Commande Django pour synchroniser manuellement toutes les données
Usage: python manage.py synchroniser_donnees [--user=username] [--mois=7] [--annee=2025]
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from datetime import datetime
from fleet_app.signals import synchroniser_tous_employes_mois, synchroniser_paie_employe
from fleet_app.models_entreprise import Employe

class Command(BaseCommand):
    help = 'Synchronise automatiquement toutes les données de paie et heures supplémentaires'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Nom d\'utilisateur spécifique à synchroniser (optionnel)',
        )
        parser.add_argument(
            '--mois',
            type=int,
            help='Mois à synchroniser (1-12, défaut: mois actuel)',
        )
        parser.add_argument(
            '--annee',
            type=int,
            help='Année à synchroniser (défaut: année actuelle)',
        )
        parser.add_argument(
            '--employe',
            type=str,
            help='Matricule d\'employé spécifique à synchroniser (optionnel)',
        )

    def handle(self, *args, **options):
        # Paramètres par défaut
        mois = options['mois'] or datetime.now().month
        annee = options['annee'] or datetime.now().year
        
        self.stdout.write(
            self.style.SUCCESS(f'🔄 DÉMARRAGE SYNCHRONISATION - Mois: {mois}/{annee}')
        )
        
        try:
            if options['employe']:
                # Synchronisation d'un employé spécifique
                self.synchroniser_employe_specifique(options['employe'], mois, annee)
                
            elif options['user']:
                # Synchronisation d'un utilisateur spécifique
                self.synchroniser_utilisateur_specifique(options['user'], mois, annee)
                
            else:
                # Synchronisation globale de tous les utilisateurs
                self.synchroniser_tous_utilisateurs(mois, annee)
                
        except Exception as e:
            raise CommandError(f'Erreur lors de la synchronisation: {e}')
        
        self.stdout.write(
            self.style.SUCCESS('🎉 SYNCHRONISATION TERMINÉE AVEC SUCCÈS')
        )

    def synchroniser_employe_specifique(self, matricule, mois, annee):
        """Synchronise un employé spécifique"""
        self.stdout.write(f'🔍 Recherche de l\'employé {matricule}...')
        
        try:
            employe = Employe.objects.get(matricule=matricule)
            self.stdout.write(f'✅ Employé trouvé: {employe.prenom} {employe.nom}')
            
            synchroniser_paie_employe(employe, mois, annee)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Synchronisation terminée pour {matricule}')
            )
            
        except Employe.DoesNotExist:
            raise CommandError(f'Employé avec matricule {matricule} introuvable')

    def synchroniser_utilisateur_specifique(self, username, mois, annee):
        """Synchronise tous les employés d'un utilisateur spécifique"""
        self.stdout.write(f'🔍 Recherche de l\'utilisateur {username}...')
        
        try:
            user = User.objects.get(username=username)
            self.stdout.write(f'✅ Utilisateur trouvé: {user.get_full_name() or username}')
            
            employes = Employe.objects.filter(user=user)
            self.stdout.write(f'📊 {employes.count()} employé(s) à synchroniser')
            
            synchroniser_tous_employes_mois(user, mois, annee)
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Synchronisation terminée pour {username}')
            )
            
        except User.DoesNotExist:
            raise CommandError(f'Utilisateur {username} introuvable')

    def synchroniser_tous_utilisateurs(self, mois, annee):
        """Synchronise tous les utilisateurs du système"""
        self.stdout.write('🌍 Synchronisation globale de tous les utilisateurs...')
        
        users = User.objects.all()
        total_users = users.count()
        
        self.stdout.write(f'📊 {total_users} utilisateur(s) à synchroniser')
        
        for i, user in enumerate(users, 1):
            self.stdout.write(f'🔄 [{i}/{total_users}] Synchronisation de {user.username}...')
            
            try:
                employes = Employe.objects.filter(user=user)
                if employes.exists():
                    synchroniser_tous_employes_mois(user, mois, annee)
                    self.stdout.write(f'  ✅ {employes.count()} employé(s) synchronisé(s)')
                else:
                    self.stdout.write(f'  ⚠️  Aucun employé trouvé')
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  ❌ Erreur pour {user.username}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Synchronisation globale terminée - {total_users} utilisateur(s) traité(s)')
        )
