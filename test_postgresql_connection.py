#!/usr/bin/env python
"""
Script pour tester la connexion PostgreSQL avec Django
"""
import os
import sys
import django
from pathlib import Path

# Ajouter le répertoire du projet au path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Configurer Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db import connection
from django.core.management.color import make_style

style = make_style()

def test_database_connection():
    """Test la connexion à la base de données"""
    try:
        # Test de connexion basique
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
        print(style.SUCCESS("✓ Connexion PostgreSQL réussie!"))
        print(f"Version PostgreSQL: {version}")
        
        # Test des tables Django
        from django.db import models
        from fleet_app.models import Vehicule
        
        # Compter les véhicules
        count = Vehicule.objects.count()
        print(f"✓ Tables Django accessibles - {count} véhicules trouvés")
        
        # Informations sur la base de données
        db_settings = connection.settings_dict
        print(f"\nConfiguration de la base de données:")
        print(f"  - Engine: {db_settings['ENGINE']}")
        print(f"  - Name: {db_settings['NAME']}")
        print(f"  - User: {db_settings['USER']}")
        print(f"  - Host: {db_settings['HOST']}")
        print(f"  - Port: {db_settings['PORT']}")
        
        return True
        
    except Exception as e:
        print(style.ERROR(f"✗ Erreur de connexion: {e}"))
        print("\nVérifiez:")
        print("1. PostgreSQL est démarré")
        print("2. Les paramètres dans le fichier .env")
        print("3. L'utilisateur et la base de données existent")
        print("4. Les migrations ont été appliquées")
        return False

def check_environment():
    """Vérifie les variables d'environnement"""
    required_vars = [
        'DJANGO_DB_ENGINE',
        'DJANGO_DB_NAME', 
        'DJANGO_DB_USER',
        'DJANGO_DB_PASSWORD',
        'DJANGO_DB_HOST',
        'DJANGO_DB_PORT'
    ]
    
    print("Variables d'environnement:")
    missing = []
    for var in required_vars:
        value = os.getenv(var, 'NON DÉFINIE')
        if value == 'NON DÉFINIE':
            missing.append(var)
            print(f"  ✗ {var}: {style.ERROR(value)}")
        else:
            # Masquer le mot de passe
            display_value = '***' if 'PASSWORD' in var else value
            print(f"  ✓ {var}: {display_value}")
    
    if missing:
        print(f"\n{style.ERROR('Variables manquantes:')} {', '.join(missing)}")
        print("Créez un fichier .env avec ces variables.")
        return False
    
    return True

if __name__ == '__main__':
    print("=== Test de connexion PostgreSQL pour GuinéeGest ===\n")
    
    # Vérifier les variables d'environnement
    if not check_environment():
        sys.exit(1)
    
    print()
    
    # Tester la connexion
    if test_database_connection():
        print(f"\n{style.SUCCESS('🎉 Configuration PostgreSQL OK!')}")
        sys.exit(0)
    else:
        print(f"\n{style.ERROR('❌ Configuration PostgreSQL échouée')}")
        sys.exit(1)
