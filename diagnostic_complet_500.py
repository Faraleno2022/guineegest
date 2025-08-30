import os
import django
import traceback
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import RequestFactory, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.loader import get_template
from django.db import connection

def test_url_routing():
    """Test URL routing for bulletins-paie"""
    try:
        print("🔍 Testing URL routing...")
        from django.urls import resolve
        
        # Test URL resolution
        resolver = resolve('/bulletins-paie/')
        print(f"✅ URL resolves to: {resolver.func.__name__}")
        print(f"✅ View module: {resolver.func.__module__}")
        
        return True
    except Exception as e:
        print(f"❌ URL routing error: {e}")
        traceback.print_exc()
        return False

def test_template_exists():
    """Test if template exists and can be loaded"""
    try:
        print("\n🔍 Testing template loading...")
        template = get_template('fleet_app/entreprise/bulletin_paie_list.html')
        print("✅ Template loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Template error: {e}")
        traceback.print_exc()
        return False

def test_database_connection():
    """Test database connection and critical queries"""
    try:
        print("\n🔍 Testing database connection...")
        cursor = connection.cursor()
        
        # Test ParametresPaie table
        cursor.execute("SELECT COUNT(*) FROM ParametresPaie")
        param_count = cursor.fetchone()[0]
        print(f"✅ ParametresPaie records: {param_count}")
        
        # Test Employes table
        cursor.execute("SELECT COUNT(*) FROM Employes")
        emp_count = cursor.fetchone()[0]
        print(f"✅ Employes records: {emp_count}")
        
        # Test specific query that might fail
        cursor.execute("SELECT nom, valeur, cle FROM ParametresPaie LIMIT 1")
        result = cursor.fetchone()
        if result:
            print(f"✅ Sample ParametresPaie: nom='{result[0]}', valeur='{result[1]}', cle='{result[2]}'")
        else:
            print("⚠️ No ParametresPaie records found")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        traceback.print_exc()
        return False

def test_view_with_client():
    """Test view using Django test client (more realistic)"""
    try:
        print("\n🔍 Testing with Django test client...")
        client = Client()
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'password': 'testpass'}
        )
        
        # Login
        client.force_login(user)
        
        # Make request
        response = client.get('/bulletins-paie/')
        
        print(f"✅ Response status: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ 500 Error detected!")
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                if 'Traceback' in content:
                    print("📋 Error details from response:")
                    print(content[:1000])
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Client test error: {e}")
        traceback.print_exc()
        return False

def test_imports():
    """Test all necessary imports"""
    try:
        print("\n🔍 Testing imports...")
        
        from fleet_app.views_management_complete import bulletin_paie_list
        print("✅ bulletin_paie_list imported")
        
        from fleet_app.models_entreprise import ParametrePaie, Employe, PresenceJournaliere, PaieEmploye
        print("✅ Models imported")
        
        from decimal import Decimal
        from datetime import datetime
        print("✅ Standard libraries imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        traceback.print_exc()
        return False

def test_middleware_and_context():
    """Test middleware and context processors"""
    try:
        print("\n🔍 Testing middleware and context...")
        
        from django.conf import settings
        print(f"✅ Middleware: {len(settings.MIDDLEWARE)} configured")
        
        # Test context processors
        template_settings = settings.TEMPLATES[0]['OPTIONS']['context_processors']
        print(f"✅ Context processors: {len(template_settings)} configured")
        
        return True
    except Exception as e:
        print(f"❌ Middleware/context error: {e}")
        return False

def main():
    print("🚀 DIAGNOSTIC COMPLET - Erreur 500 bulletins-paie")
    print("=" * 60)
    
    results = []
    
    results.append(("URL Routing", test_url_routing()))
    results.append(("Template Loading", test_template_exists()))
    results.append(("Database Connection", test_database_connection()))
    results.append(("Imports", test_imports()))
    results.append(("Middleware/Context", test_middleware_and_context()))
    results.append(("Django Client Test", test_view_with_client()))
    
    print("\n" + "=" * 60)
    print("📊 RÉSULTATS DU DIAGNOSTIC:")
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} : {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 Tous les tests passent - L'erreur pourrait être liée au contexte du serveur web")
        print("💡 Suggestions:")
        print("   - Redémarrer le serveur Django")
        print("   - Vider le cache du navigateur")
        print("   - Vérifier les logs du serveur en temps réel")
    else:
        print("\n❌ Des problèmes ont été détectés - voir les détails ci-dessus")

if __name__ == "__main__":
    main()
