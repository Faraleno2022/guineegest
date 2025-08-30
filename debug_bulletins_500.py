import os
import django
import traceback

# Configure Django settings first
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User

def test_bulletins_view():
    try:
        # Import the view
        from fleet_app.views_management_complete import bulletin_paie_list
        
        # Create a test request
        factory = RequestFactory()
        request = factory.get('/bulletins-paie/')
        
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        request.user = user
        
        print("🔍 Testing bulletin_paie_list view...")
        
        # Call the view
        response = bulletin_paie_list(request)
        
        print(f"✅ View executed successfully - Status: {response.status_code}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR in bulletin_paie_list view:")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return False

def check_database_tables():
    try:
        from django.db import connection
        cursor = connection.cursor()
        
        # Check critical tables
        tables_to_check = [
            'ParametresPaie',
            'Employes', 
            'PresenceJournaliere',
            'PaieEmployes'
        ]
        
        print("\n🔍 Checking database tables...")
        for table in tables_to_check:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} records")
            except Exception as e:
                print(f"❌ {table}: ERROR - {e}")
        
        # Check ParametresPaie schema specifically
        cursor.execute("PRAGMA table_info('ParametresPaie')")
        columns = cursor.fetchall()
        print(f"\n📋 ParametresPaie columns: {[col[1] for col in columns]}")
        
    except Exception as e:
        print(f"❌ Database check failed: {e}")

def check_models_import():
    try:
        print("\n🔍 Testing model imports...")
        from fleet_app.models_entreprise import ParametrePaie, Employe, PresenceJournaliere, PaieEmploye
        print("✅ All models imported successfully")
        
        # Test basic queries
        print(f"✅ ParametrePaie count: {ParametrePaie.objects.count()}")
        print(f"✅ Employe count: {Employe.objects.count()}")
        
    except Exception as e:
        print(f"❌ Model import/query failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Starting comprehensive bulletins debug...")
    
    check_database_tables()
    check_models_import()
    test_bulletins_view()
    
    print("\n🎉 Debug completed!")
