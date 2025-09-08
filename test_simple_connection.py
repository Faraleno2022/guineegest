#!/usr/bin/env python3
"""
Test de connexion PostgreSQL simple sans Django
"""
import os
import psycopg2
from dotenv import load_dotenv
from pathlib import Path

# Charger les variables d'environnement
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')

def test_postgresql_connection():
    """Test direct de la connexion PostgreSQL"""
    print("=== Test de connexion PostgreSQL direct ===")
    print()
    
    # Paramètres de connexion
    db_params = {
        'host': os.getenv('DJANGO_DB_HOST', 'localhost'),
        'port': os.getenv('DJANGO_DB_PORT', '5432'),
        'database': os.getenv('DJANGO_DB_NAME', 'guineegest_db'),
        'user': os.getenv('DJANGO_DB_USER', 'guineegest_user'),
        'password': os.getenv('DJANGO_DB_PASSWORD', 'guineegest2024')
    }
    
    print("Paramètres de connexion:")
    for key, value in db_params.items():
        if key == 'password':
            print(f"  {key}: ***")
        else:
            print(f"  {key}: {value}")
    print()
    
    try:
        # Connexion directe avec psycopg2
        conn = psycopg2.connect(**db_params)
        cursor = conn.cursor()
        
        # Test de base
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✓ Connexion PostgreSQL réussie!")
        print(f"  Version: {version}")
        
        # Vérifier l'encodage de la base
        cursor.execute("SHOW server_encoding;")
        encoding = cursor.fetchone()[0]
        print(f"  Encodage serveur: {encoding}")
        
        cursor.execute("SHOW client_encoding;")
        client_encoding = cursor.fetchone()[0]
        print(f"  Encodage client: {client_encoding}")
        
        # Compter les tables
        cursor.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
        table_count = cursor.fetchone()[0]
        print(f"  Tables dans la base: {table_count}")
        
        cursor.close()
        conn.close()
        
        print()
        print("✅ Test de connexion PostgreSQL réussi!")
        return True
        
    except Exception as e:
        print(f"✗ Erreur de connexion: {e}")
        print(f"  Type d'erreur: {type(e).__name__}")
        print()
        print("❌ Test de connexion PostgreSQL échoué")
        return False

if __name__ == "__main__":
    test_postgresql_connection()
