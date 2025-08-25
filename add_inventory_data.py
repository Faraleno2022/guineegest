import os
import sys
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Configurer l'environnement Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

# Importer les modèles après la configuration de Django
from fleet_app.models_inventaire import Produit, EntreeStock, SortieStock, MouvementStock
from django.contrib.auth.models import User
from django.db import transaction

# Fonction pour générer un ID unique avec préfixe
def generate_id(prefix, count):
    return f"{prefix}{count:04d}"

# Fonction pour générer une date aléatoire dans les 3 derniers mois
def random_date(start_date=None):
    if not start_date:
        start_date = datetime.now() - timedelta(days=90)
    days_to_add = random.randint(0, 90)
    return start_date + timedelta(days=days_to_add)

# Catégories de produits selon le modèle
CATEGORIES = [
    'Alimentaire', 'Hygiène', 'Fourniture', 'Équipement', 'Pièce', 'Autre'
]

# Unités de mesure selon le modèle
UNITES = [
    'Pièce', 'Carton', 'Sac', 'Kg', 'Litre', 'Mètre', 'Autre'
]

# Fournisseurs fictifs
FOURNISSEURS = [
    "Auto Parts Plus", "Mécanique Générale", "Pièces Express", 
    "Garage Central", "Équipements Pro", "Conakry Auto", 
    "Pièces Importées", "Fournitures Techniques"
]

# Destinataires fictifs pour les sorties
DESTINATAIRES = [
    "Atelier Mécanique", "Service Entretien", "Garage Central", 
    "Équipe Maintenance", "Chauffeurs", "Service Technique",
    "Réparations Externes", "Véhicules de Service"
]

# Motifs de sortie
MOTIFS = [
    "Entretien régulier", "Réparation", "Remplacement préventif", 
    "Panne", "Accident", "Mise à niveau", "Stock externe", "Prêt"
]

@transaction.atomic
def create_products(num_products=20):
    """Crée un nombre spécifié de produits"""
    products = []
    print(f"Création de {num_products} produits...")
    
    for i in range(1, num_products + 1):
        id_produit = generate_id("P", i)
        nom = f"Produit Test {i}"
        categorie = random.choice(CATEGORIES)
        unite = random.choice(UNITES)
        prix_unitaire = Decimal(str(random.uniform(10000, 1000000))).quantize(Decimal('0'))
        seuil_minimum = random.randint(5, 20)
        fournisseur = random.choice(FOURNISSEURS)
        date_ajout = random_date()
        
        product = Produit(
            id_produit=id_produit,
            nom=nom,
            categorie=categorie,
            unite=unite,
            prix_unitaire=prix_unitaire,
            seuil_minimum=seuil_minimum,
            fournisseur=fournisseur,
            date_ajout=date_ajout
        )
        product.save()
        products.append(product)
        print(f"  - Produit créé: {id_produit} - {nom}")
    
    return products

@transaction.atomic
def create_stock_entries(products, num_entries=50):
    """Crée des entrées en stock pour les produits"""
    print(f"Création de {num_entries} entrées en stock...")
    
    for i in range(1, num_entries + 1):
        id_entree = generate_id("E", i)
        date = random_date()
        produit = random.choice(products)
        quantite = random.randint(5, 50)
        prix_unitaire = Decimal(str(random.uniform(5000, 500000))).quantize(Decimal('0'))
        fournisseur = random.choice(FOURNISSEURS)
        reference_facture = f"FAC-{random.randint(1000, 9999)}"
        
        entree = EntreeStock(
            id_entree=id_entree,
            date=date,
            produit=produit,
            quantite=quantite,
            prix_unitaire=prix_unitaire,
            fournisseur=fournisseur,
            reference_facture=reference_facture
        )
        entree.save()
        print(f"  - Entrée créée: {id_entree} - {produit.nom} ({quantite} {produit.unite})")
    
    return True

@transaction.atomic
def create_stock_exits(products, num_exits=30):
    """Crée des sorties en stock pour les produits"""
    print(f"Création de {num_exits} sorties de stock...")
    
    for i in range(1, num_exits + 1):
        id_sortie = generate_id("S", i)
        date = random_date()
        produit = random.choice(products)
        
        # Vérifier le stock disponible
        stock_disponible = produit.get_stock_actuel()
        if stock_disponible <= 0:
            print(f"  - Sortie ignorée pour {produit.nom}: stock insuffisant ({stock_disponible})")
            continue
            
        # Limiter la quantité sortie au stock disponible
        quantite = min(random.randint(1, 10), stock_disponible)
        destinataire = random.choice(DESTINATAIRES)
        motif = random.choice(MOTIFS)
        reference_bon = f"BON-{random.randint(1000, 9999)}"
        
        try:
            sortie = SortieStock(
                id_sortie=id_sortie,
                date=date,
                produit=produit,
                quantite=quantite,
                destinataire=destinataire,
                motif=motif,
                reference_bon=reference_bon
            )
            sortie.save()
            print(f"  - Sortie créée: {id_sortie} - {produit.nom} ({quantite} {produit.unite})")
        except Exception as e:
            print(f"  - Erreur lors de la création de la sortie pour {produit.nom}: {e}")
    
    return True

def main():
    """Fonction principale pour créer les données de test"""
    print("Début de la création des données de test pour l'inventaire...")
    
    # Vérifier si des données existent déjà
    existing_products = Produit.objects.count()
    if existing_products > 0:
        print(f"Attention: {existing_products} produits existent déjà dans la base de données.")
        confirmation = input("Voulez-vous continuer et ajouter plus de données? (o/n): ")
        if confirmation.lower() != 'o':
            print("Opération annulée.")
            return
    
    # Créer les données
    products = create_products(20)
    create_stock_entries(products, 50)
    create_stock_exits(products, 30)
    
    # Afficher un résumé
    print("\nRésumé des données créées:")
    print(f"- Produits: {Produit.objects.count()}")
    print(f"- Entrées en stock: {EntreeStock.objects.count()}")
    print(f"- Sorties de stock: {SortieStock.objects.count()}")
    print(f"- Mouvements de stock: {MouvementStock.objects.count()}")
    
    print("\nCréation des données terminée avec succès!")

if __name__ == "__main__":
    main()
