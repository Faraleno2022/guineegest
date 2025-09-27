from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
import random

from fleet_app.models import Vehicule
from fleet_app.models_location import (
    FournisseurVehicule,
    LocationVehicule,
    FeuillePontageLocation,
    FactureLocation
)
from fleet_app.models_accounts import Entreprise


class Command(BaseCommand):
    help = 'Crée des données de test pour le module locations et factures'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user-id',
            type=int,
            help='ID de l\'utilisateur pour lequel créer les données (par défaut: premier utilisateur)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprimer toutes les données existantes avant de créer les nouvelles'
        )

    def handle(self, *args, **options):
        # Récupérer l'utilisateur
        user_id = options.get('user_id')
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Utilisateur avec ID {user_id} non trouvé')
                )
                return
        else:
            user = User.objects.first()
            if not user:
                self.stdout.write(
                    self.style.ERROR('Aucun utilisateur trouvé dans la base de données')
                )
                return

        # Récupérer l'entreprise existante (optionnel)
        entreprise = None
        try:
            if hasattr(user, 'profil') and hasattr(user.profil, 'entreprise') and user.profil.entreprise:
                entreprise = user.profil.entreprise
        except:
            pass
        
        if not entreprise:
            try:
                if hasattr(user, 'entreprise') and user.entreprise:
                    entreprise = user.entreprise
            except:
                pass
        
        if not entreprise:
            # Utiliser la première entreprise disponible ou None
            entreprise = Entreprise.objects.first()
            if entreprise:
                self.stdout.write(f"Utilisation de l'entreprise existante: {entreprise.nom_entreprise}")
            else:
                self.stdout.write("Aucune entreprise trouvée, création sans entreprise")

        # Supprimer les données existantes si demandé
        if options['clear']:
            self.stdout.write("Suppression des données existantes...")
            FactureLocation.objects.filter(user=user).delete()
            FeuillePontageLocation.objects.filter(user=user).delete()
            LocationVehicule.objects.filter(user=user).delete()
            FournisseurVehicule.objects.filter(user=user).delete()
            self.stdout.write(self.style.SUCCESS("Données supprimées"))

        # Créer des fournisseurs de test
        self.stdout.write("Création des fournisseurs...")
        fournisseurs_data = [
            {
                'nom': 'Location Express Guinée',
                'contact': 'Mamadou Diallo',
                'telephone': '224 621 123 456',
                'email': 'contact@locationexpress.gn',
                'adresse': 'Kaloum, Conakry'
            },
            {
                'nom': 'Auto Rent Conakry',
                'contact': 'Fatoumata Camara',
                'telephone': '224 622 789 012',
                'email': 'info@autorent.gn',
                'adresse': 'Matam, Conakry'
            },
            {
                'nom': 'Véhicules Services Plus',
                'contact': 'Ibrahima Sow',
                'telephone': '224 623 345 678',
                'email': 'services@vehiculesplus.gn',
                'adresse': 'Ratoma, Conakry'
            }
        ]

        fournisseurs = []
        for data in fournisseurs_data:
            fournisseur, created = FournisseurVehicule.objects.get_or_create(
                nom=data['nom'],
                user=user,
                defaults={
                    'contact': data['contact'],
                    'telephone': data['telephone'],
                    'email': data['email'],
                    'adresse': data['adresse'],
                    'entreprise': entreprise
                }
            )
            fournisseurs.append(fournisseur)
            if created:
                self.stdout.write(f"  ✓ Fournisseur créé: {fournisseur.nom}")

        # Récupérer ou créer des véhicules de test
        self.stdout.write("Vérification des véhicules...")
        vehicules = list(Vehicule.objects.filter(user=user)[:5])
        
        if len(vehicules) < 3:
            # Créer quelques véhicules de test si nécessaire
            vehicules_data = [
                {
                    'id_vehicule': 'TEST001',
                    'immatriculation': 'GN-001-AA',
                    'marque': 'Toyota',
                    'modele': 'Hilux',
                    'type_moteur': 'Diesel',
                    'categorie': 'Pickup',
                    'statut_actuel': 'Disponible'
                },
                {
                    'id_vehicule': 'TEST002',
                    'immatriculation': 'GN-002-BB',
                    'marque': 'Nissan',
                    'modele': 'Patrol',
                    'type_moteur': 'Essence',
                    'categorie': 'SUV',
                    'statut_actuel': 'Disponible'
                },
                {
                    'id_vehicule': 'TEST003',
                    'immatriculation': 'GN-003-CC',
                    'marque': 'Mercedes',
                    'modele': 'Sprinter',
                    'type_moteur': 'Diesel',
                    'categorie': 'Utilitaire',
                    'statut_actuel': 'Disponible'
                }
            ]
            
            for data in vehicules_data:
                vehicule, created = Vehicule.objects.get_or_create(
                    id_vehicule=data['id_vehicule'],
                    user=user,
                    defaults={
                        'immatriculation': data['immatriculation'],
                        'marque': data['marque'],
                        'modele': data['modele'],
                        'type_moteur': data['type_moteur'],
                        'categorie': data['categorie'],
                        'statut_actuel': data['statut_actuel'],
                        'entreprise': entreprise
                    }
                )
                if created:
                    vehicules.append(vehicule)
                    self.stdout.write(f"  ✓ Véhicule créé: {vehicule.immatriculation}")

        # Créer des locations de test
        self.stdout.write("Création des locations...")
        locations = []
        today = timezone.now().date()
        
        for i, vehicule in enumerate(vehicules[:3]):
            # Location 1: Active depuis 2 mois
            date_debut = today - timedelta(days=60)
            location = LocationVehicule.objects.create(
                vehicule=vehicule,
                type_location=random.choice(['Interne', 'Externe']),
                fournisseur=random.choice(fournisseurs) if random.choice([True, False]) else None,
                date_debut=date_debut,
                date_fin=None,  # Location active
                tarif_journalier=random.randint(50000, 150000),  # 50k à 150k GNF
                statut='Active',
                motif=f'Location véhicule {vehicule.immatriculation} pour missions',
                user=user,
                entreprise=entreprise
            )
            locations.append(location)
            self.stdout.write(f"  ✓ Location créée: {location}")

        # Créer des feuilles de pontage pour les 60 derniers jours
        self.stdout.write("Création des feuilles de pontage...")
        statuts_pontage = ['Travail', 'Entretien', 'Hors service', 'Inactif']
        
        for location in locations:
            date_courante = location.date_debut
            while date_courante <= today:
                # 80% de chance d'avoir une feuille "Travail"
                if random.random() < 0.8:
                    statut = 'Travail'
                else:
                    statut = random.choice(statuts_pontage[1:])  # Autres statuts
                
                commentaires = {
                    'Travail': [
                        'Mission terrain normale',
                        'Transport personnel',
                        'Livraison matériel',
                        'Déplacement administratif'
                    ],
                    'Entretien': [
                        'Vidange moteur',
                        'Révision générale',
                        'Réparation pneus',
                        'Contrôle technique'
                    ],
                    'Hors service': [
                        'Panne moteur',
                        'Accident mineur',
                        'Réparation carrosserie'
                    ],
                    'Inactif': [
                        'Véhicule non utilisé',
                        'Attente mission',
                        'Repos conducteur'
                    ]
                }
                
                feuille, created = FeuillePontageLocation.objects.get_or_create(
                    location=location,
                    date=date_courante,
                    defaults={
                        'statut': statut,
                        'commentaire': random.choice(commentaires[statut]),
                        'user': user,
                        'entreprise': entreprise
                    }
                )
                
                date_courante += timedelta(days=1)

        self.stdout.write(f"  ✓ Feuilles de pontage créées pour {len(locations)} locations")

        # Générer des factures pour les mois précédents
        self.stdout.write("Génération des factures mensuelles...")
        
        # Factures pour les 2 derniers mois
        for mois_offset in [2, 1]:
            date_facture = today - timedelta(days=30 * mois_offset)
            year = date_facture.year
            month = date_facture.month
            
            for location in locations:
                # Calculer les jours de travail du mois
                first_day = datetime(year, month, 1).date()
                if month == 12:
                    last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
                
                jours_travail = location.feuilles.filter(
                    statut="Travail",
                    date__gte=first_day,
                    date__lte=last_day
                ).count()
                
                if jours_travail > 0:
                    montant_ht = jours_travail * location.tarif_journalier
                    tva = montant_ht * 0.18
                    montant_ttc = montant_ht + tva
                    
                    numero = f"LOC-{location.pk}-{year}{month:02d}"
                    
                    facture, created = FactureLocation.objects.get_or_create(
                        location=location,
                        numero=numero,
                        user=user,
                        defaults={
                            'date': last_day,
                            'montant_ht': montant_ht,
                            'tva': tva,
                            'montant_ttc': montant_ttc,
                            'statut': 'Brouillon',
                            'jours_travail_mois': jours_travail,
                            'jours_non_travail_mois': (last_day - first_day).days + 1 - jours_travail,
                            'entreprise': entreprise
                        }
                    )
                    
                    if created:
                        self.stdout.write(f"  ✓ Facture créée: {facture.numero} - {montant_ttc:,.0f} GNF")

        # Statistiques finales
        total_locations = LocationVehicule.objects.filter(user=user).count()
        total_feuilles = FeuillePontageLocation.objects.filter(user=user).count()
        total_factures = FactureLocation.objects.filter(user=user).count()
        from django.db import models
        total_montant = FactureLocation.objects.filter(user=user).aggregate(
            total=models.Sum('montant_ttc')
        )['total'] or 0

        self.stdout.write(
            self.style.SUCCESS(
                f"\n✅ Données de test créées avec succès pour l'utilisateur {user.username}:\n"
                f"   • {len(fournisseurs)} fournisseurs\n"
                f"   • {total_locations} locations\n"
                f"   • {total_feuilles} feuilles de pontage\n"
                f"   • {total_factures} factures ({total_montant:,.0f} GNF)\n"
            )
        )
