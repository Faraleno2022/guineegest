#!/usr/bin/env python
"""
Script pour créer un utilisateur admin et associer les données
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.contrib.auth.models import User
from fleet_app.models import *
from fleet_app.models_inventaire import *
from fleet_app.models_entreprise import *

# Import des modèles spécifiques qui pourraient manquer
try:
    from fleet_app.models import Alerte
except ImportError:
    print("⚠ Modèle Alerte non trouvé, création d'une classe vide")
    class Alerte:
        objects = None

try:
    from fleet_app.models import CoutFonctionnement
except ImportError:
    print("⚠ Modèle CoutFonctionnement non trouvé")
    class CoutFonctionnement:
        objects = None

try:
    from fleet_app.models import CoutFinancier
except ImportError:
    print("⚠ Modèle CoutFinancier non trouvé")
    class CoutFinancier:
        objects = None

try:
    from fleet_app.models import UtilisationVehicule
except ImportError:
    print("⚠ Modèle UtilisationVehicule non trouvé")
    class UtilisationVehicule:
        objects = None

def create_admin_and_associate_data():
    """Créer l'admin et associer les données"""
    try:
        # Créer ou récupérer l'utilisateur admin
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@guineegest.com',
                'first_name': 'Admin',
                'last_name': 'GuinéeGest',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            print(f"✓ Utilisateur admin créé avec ID {user.id}")
        else:
            print(f"✓ Utilisateur admin existe avec ID {user.id}")
        
        # Associer les données existantes - seulement les modèles qui existent
        models_to_update = []
        
        # Vérifier et ajouter les modèles qui existent
        if hasattr(Vehicule, 'objects') and Vehicule.objects is not None:
            models_to_update.append((Vehicule, 'véhicules'))
        if hasattr(Chauffeur, 'objects') and Chauffeur.objects is not None:
            models_to_update.append((Chauffeur, 'chauffeurs'))
        if hasattr(FeuilleDeRoute, 'objects') and FeuilleDeRoute.objects is not None:
            models_to_update.append((FeuilleDeRoute, 'feuilles de route'))
        
        # Modèles inventaire
        try:
            if Produit.objects:
                models_to_update.append((Produit, 'produits'))
        except:
            pass
            
        try:
            if EntreeStock.objects:
                models_to_update.append((EntreeStock, 'entrées de stock'))
        except:
            pass
            
        try:
            if SortieStock.objects:
                models_to_update.append((SortieStock, 'sorties de stock'))
        except:
            pass
            
        # Modèles entreprise
        try:
            if Employe.objects:
                models_to_update.append((Employe, 'employés'))
        except:
            pass
        
        for model_class, name in models_to_update:
            try:
                updated = model_class.objects.filter(user__isnull=True).update(user=user)
                if updated > 0:
                    print(f"✓ {updated} {name} associés à l'admin")
            except Exception as e:
                print(f"⚠ Erreur avec {name}: {e}")
        
        print(f"\n✓ Toutes les données ont été associées à l'utilisateur admin")
        print(f"Login: admin")
        print(f"Password: admin123")
        
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        return False

if __name__ == '__main__':
    print("=== Création de l'utilisateur admin ===")
    if create_admin_and_associate_data():
        print("\n✓ Configuration terminée avec succès!")
    else:
        sys.exit(1)
