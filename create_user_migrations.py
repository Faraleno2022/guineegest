#!/usr/bin/env python
"""
Script pour créer les migrations nécessaires pour ajouter les champs user aux modèles
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth.models import User
from fleet_app.models import *

def create_migrations():
    """Créer les migrations pour ajouter les champs user"""
    print("Création des migrations...")
    try:
        call_command('makemigrations', 'fleet_app', verbosity=2)
        print("✓ Migrations créées avec succès")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de la création des migrations: {e}")
        return False

def apply_migrations():
    """Appliquer les migrations"""
    print("Application des migrations...")
    try:
        call_command('migrate', verbosity=2)
        print("✓ Migrations appliquées avec succès")
        return True
    except Exception as e:
        print(f"✗ Erreur lors de l'application des migrations: {e}")
        return False

def create_test_user():
    """Créer un utilisateur de test si nécessaire"""
    print("Vérification de l'utilisateur de test...")
    try:
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@guineegest.com',
                'first_name': 'Admin',
                'last_name': 'GuinéeGest',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            user.set_password('admin123')
            user.save()
            print("✓ Utilisateur admin créé")
        else:
            print("✓ Utilisateur admin existe déjà")
        return user
    except Exception as e:
        print(f"✗ Erreur lors de la création de l'utilisateur: {e}")
        return None

def associate_existing_data(user):
    """Associer les données existantes à l'utilisateur"""
    print("Association des données existantes à l'utilisateur...")
    try:
        # Associer les véhicules
        vehicules_updated = Vehicule.objects.filter(user__isnull=True).update(user=user)
        print(f"✓ {vehicules_updated} véhicules associés")
        
        # Associer les chauffeurs
        chauffeurs_updated = Chauffeur.objects.filter(user__isnull=True).update(user=user)
        print(f"✓ {chauffeurs_updated} chauffeurs associés")
        
        # Associer les employés
        employes_updated = Employe.objects.filter(user__isnull=True).update(user=user)
        print(f"✓ {employes_updated} employés associés")
        
        # Associer les produits
        produits_updated = Produit.objects.filter(user__isnull=True).update(user=user)
        print(f"✓ {produits_updated} produits associés")
        
        return True
    except Exception as e:
        print(f"✗ Erreur lors de l'association des données: {e}")
        return False

if __name__ == '__main__':
    print("=== Script de migration pour l'isolation des données ===")
    
    # Étape 1: Créer les migrations
    if not create_migrations():
        sys.exit(1)
    
    # Étape 2: Appliquer les migrations
    if not apply_migrations():
        sys.exit(1)
    
    # Étape 3: Créer un utilisateur de test
    user = create_test_user()
    if not user:
        sys.exit(1)
    
    # Étape 4: Associer les données existantes
    if not associate_existing_data(user):
        sys.exit(1)
    
    print("\n✓ Migration terminée avec succès!")
    print("Vous pouvez maintenant démarrer le serveur avec: python manage.py runserver")
