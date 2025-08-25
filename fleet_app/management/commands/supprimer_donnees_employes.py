"""
Commande Django pour supprimer toutes les données des employés d'un utilisateur
Usage: python manage.py supprimer_donnees_employes --user_id=<ID_UTILISATEUR> --confirm
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from fleet_app.models import (
    Employe, PresenceJournaliere, HeureSupplementaire, PaieEmploye,
    ArchiveMensuelle, ParametrePaie
)
from fleet_app.models_entreprise import (
    ConfigurationMontantEmploye, ConfigurationMontantStatut
)


class Command(BaseCommand):
    help = 'Supprime toutes les données des employés pour un utilisateur donné'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user_id',
            type=int,
            help='ID de l\'utilisateur dont supprimer les données',
            required=True
        )
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirmer la suppression (obligatoire pour éviter les suppressions accidentelles)',
        )

    def handle(self, *args, **options):
        user_id = options['user_id']
        confirm = options['confirm']

        if not confirm:
            self.stdout.write(
                self.style.ERROR(
                    'ATTENTION: Cette commande va supprimer TOUTES les données des employés!\n'
                    'Utilisez --confirm pour confirmer la suppression.'
                )
            )
            return

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Utilisateur avec l\'ID {user_id} non trouvé')
            )
            return

        self.stdout.write(f'Suppression des données pour l\'utilisateur: {user.username} (ID: {user.id})')

        # Compter les données avant suppression
        employes_count = Employe.objects.filter(user=user).count()
        presences_count = PresenceJournaliere.objects.filter(employe__user=user).count()
        heures_supp_count = HeureSupplementaire.objects.filter(employe__user=user).count()
        paies_count = PaieEmploye.objects.filter(employe__user=user).count()
        archives_count = ArchiveMensuelle.objects.filter(user=user).count()
        config_employe_count = ConfigurationMontantEmploye.objects.filter(employe__user=user).count()
        config_statut_count = ConfigurationMontantStatut.objects.filter(user=user).count()
        parametres_count = ParametrePaie.objects.filter(user=user).count()

        self.stdout.write('\n=== DONNÉES À SUPPRIMER ===')
        self.stdout.write(f'Employés: {employes_count}')
        self.stdout.write(f'Présences: {presences_count}')
        self.stdout.write(f'Heures supplémentaires: {heures_supp_count}')
        self.stdout.write(f'Paies: {paies_count}')
        self.stdout.write(f'Archives mensuelles: {archives_count}')
        self.stdout.write(f'Configurations montants employés: {config_employe_count}')
        self.stdout.write(f'Configurations montants statuts: {config_statut_count}')
        self.stdout.write(f'Paramètres de paie: {parametres_count}')

        if employes_count == 0:
            self.stdout.write(self.style.WARNING('Aucune donnée à supprimer pour cet utilisateur.'))
            return

        # Demander confirmation finale
        confirmation = input('\nÊtes-vous sûr de vouloir supprimer toutes ces données? (tapez "OUI" pour confirmer): ')
        if confirmation != 'OUI':
            self.stdout.write(self.style.ERROR('Suppression annulée.'))
            return

        try:
            with transaction.atomic():
                # Supprimer dans l'ordre pour respecter les contraintes de clés étrangères
                
                # 1. Supprimer les présences
                deleted_presences = PresenceJournaliere.objects.filter(employe__user=user).delete()
                self.stdout.write(f'✅ Présences supprimées: {deleted_presences[0]}')

                # 2. Supprimer les heures supplémentaires
                deleted_heures = HeureSupplementaire.objects.filter(employe__user=user).delete()
                self.stdout.write(f'✅ Heures supplémentaires supprimées: {deleted_heures[0]}')

                # 3. Supprimer les paies
                deleted_paies = PaieEmploye.objects.filter(employe__user=user).delete()
                self.stdout.write(f'✅ Paies supprimées: {deleted_paies[0]}')

                # 4. Supprimer les configurations de montants employés
                deleted_config_emp = ConfigurationMontantEmploye.objects.filter(employe__user=user).delete()
                self.stdout.write(f'✅ Configurations montants employés supprimées: {deleted_config_emp[0]}')

                # 5. Supprimer les employés (cela supprimera automatiquement les relations)
                deleted_employes = Employe.objects.filter(user=user).delete()
                self.stdout.write(f'✅ Employés supprimés: {deleted_employes[0]}')

                # 6. Supprimer les archives mensuelles
                deleted_archives = ArchiveMensuelle.objects.filter(user=user).delete()
                self.stdout.write(f'✅ Archives mensuelles supprimées: {deleted_archives[0]}')

                # 7. Supprimer les configurations de montants statuts
                deleted_config_stat = ConfigurationMontantStatut.objects.filter(user=user).delete()
                self.stdout.write(f'✅ Configurations montants statuts supprimées: {deleted_config_stat[0]}')

                # 8. Supprimer les paramètres de paie
                deleted_params = ParametrePaie.objects.filter(user=user).delete()
                self.stdout.write(f'✅ Paramètres de paie supprimés: {deleted_params[0]}')

                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n🎉 SUPPRESSION TERMINÉE AVEC SUCCÈS!\n'
                        f'Toutes les données des employés pour l\'utilisateur {user.username} ont été supprimées.'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Erreur lors de la suppression: {str(e)}')
            )
            raise
