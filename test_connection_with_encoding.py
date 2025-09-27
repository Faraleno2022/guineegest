#!/usr/bin/env python3
"""
Test de connexion PostgreSQL avec paramètres d'encodage explicites
"""
import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

def test_postgresql_with_encoding():
    """Test avec paramètres d'encodage explicites"""
    print("=== Test PostgreSQL avec encodage explicite ===")
    print()
    
    # Forcer l'encodage système
    os.environ['PGCLIENTENCODING'] = 'UTF8'
    os.environ['LC_ALL'] = 'C'
    os.environ['LANG'] = 'C'
    
    # Paramètres de connexion avec encodage explicite
    db_params = {
        'host': os.getenv('DJANGO_DB_HOST', 'localhost'),
        'port': int(os.getenv('DJANGO_DB_PORT', '5432')),
        'database': os.getenv('DJANGO_DB_NAME', 'guineegest_db'),
        'user': os.getenv('DJANGO_DB_USER', 'guineegest_user'),
        'password': os.getenv('DJANGO_DB_PASSWORD', 'guineegest2024'),
        'client_encoding': 'UTF8'
    }
    
    print("Paramètres de connexion:")
    for key, value in db_params.items():
        if key == 'password':
            print(f"  {key}: ***")
        else:
            print(f"  {key}: {value}")
    print()
    
    try:
        # Test 1: Connexion avec paramètres d'encodage
        print("Test 1: Connexion avec client_encoding=UTF8")
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ Connexion réussie!")
        print(f"  Version: {version[:50]}...")
        
        cursor.close()
        conn.close()
        print()
        
        # Test 2: Connexion sans paramètre d'encodage
        print("Test 2: Connexion sans client_encoding")
        db_params_no_encoding = db_params.copy()
        del db_params_no_encoding['client_encoding']
        
        conn2 = psycopg2.connect(**db_params_no_encoding)
        cursor2 = conn2.cursor()
        
        cursor2.execute("SHOW client_encoding;")
        encoding = cursor2.fetchone()[0]
        print(f"✓ Encodage client détecté: {encoding}")
        
        cursor2.close()
        conn2.close()
        print()
        
        print("✅ Tests de connexion PostgreSQL réussis!")
        return True
        
    except Exception as e:
        print(f"✗ Erreur: {e}")
        print(f"  Type: {type(e).__name__}")
        
        # Test alternatif avec IP au lieu de localhost
        try:
            print()
            print("Test alternatif avec 127.0.0.1 au lieu de localhost...")
            alt_params = db_params.copy()
            alt_params['host'] = '127.0.0.1'
            
            conn3 = psycopg2.connect(**alt_params)
            cursor3 = conn3.cursor()
            
            cursor3.execute("SELECT 1;")
            result = cursor3.fetchone()[0]
            print(f"✓ Connexion alternative réussie: {result}")
            
            cursor3.close()
            conn3.close()
            return True
            
        except Exception as e2:
            print(f"✗ Erreur alternative: {e2}")
            print()
            print("❌ Tous les tests de connexion ont échoué")
            return False

if __name__ == "__main__":
    test_postgresql_with_encoding()
