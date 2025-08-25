from django.core.management.base import BaseCommand
from django.db import transaction
from fleet_app.models_inventaire import MouvementStock, EntreeStock, SortieStock, Produit, LigneCommande, Commande

# Import des modèles de facturation
try:
    from fleet_app.models_facturation import Facture, LigneFacture
    FACTURATION_AVAILABLE = True
except ImportError:
    FACTURATION_AVAILABLE = False

class Command(BaseCommand):
    help = 'Supprime toutes les données des tables d\'inventaire'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Supprimer dans l'ordre pour respecter les contraintes d'intégrité
            self.stdout.write('Suppression des lignes de commande...')
            LigneCommande.objects.all().delete()
            
            self.stdout.write('Suppression des commandes...')
            Commande.objects.all().delete()
            
            # Supprimer les factures et lignes de facture si disponibles
            if FACTURATION_AVAILABLE:
                self.stdout.write('Suppression des lignes de facture...')
                LigneFacture.objects.all().delete()
                
                self.stdout.write('Suppression des factures...')
                Facture.objects.all().delete()
            
            self.stdout.write('Suppression des mouvements de stock...')
            MouvementStock.objects.all().delete()
            
            self.stdout.write('Suppression des sorties de stock...')
            SortieStock.objects.all().delete()
            
            self.stdout.write('Suppression des entrées en stock...')
            EntreeStock.objects.all().delete()
            
            self.stdout.write('Suppression des produits...')
            Produit.objects.all().delete()
            
            self.stdout.write(self.style.SUCCESS('Toutes les données d\'inventaire ont été supprimées avec succès!'))
            self.stdout.write(self.style.SUCCESS('Vous pouvez maintenant ajouter vos propres données.'))
