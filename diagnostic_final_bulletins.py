import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.http import Http404

def test_complete_flow():
    """Test the complete flow with detailed error capture"""
    try:
        print("🔍 Testing complete bulletin flow...")
        
        # Create client without CSRF enforcement
        client = Client(enforce_csrf_checks=False)
        
        # Create and login user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'first_name': 'Test', 'last_name': 'User'}
        )
        
        client.force_login(user)
        print(f"✅ User logged in: {user.username}")
        
        # Test the bulletins page
        print("🔍 Requesting /bulletins-paie/...")
        response = client.get('/bulletins-paie/', follow=True)
        
        print(f"📊 Final status: {response.status_code}")
        print(f"📊 Redirect chain: {response.redirect_chain}")
        
        if response.status_code != 200:
            content = response.content.decode('utf-8', errors='ignore')
            
            # Check for specific error patterns
            if 'DoesNotExist' in content:
                print("❌ Model DoesNotExist error detected")
            if 'IntegrityError' in content:
                print("❌ Database IntegrityError detected")
            if 'TemplateDoesNotExist' in content:
                print("❌ Template missing error detected")
            if 'ImportError' in content:
                print("❌ Import error detected")
            if 'AttributeError' in content:
                print("❌ AttributeError detected")
            
            # Extract error details
            if 'Exception Type:' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'Exception Type:' in line and i+1 < len(lines):
                        print(f"🔍 Exception Type: {lines[i+1].strip()}")
                    if 'Exception Value:' in line and i+1 < len(lines):
                        print(f"🔍 Exception Value: {lines[i+1].strip()}")
            
            # Show first part of content for debugging
            print(f"\n📋 Response content (first 1500 chars):")
            print("-" * 50)
            print(content[:1500])
            print("-" * 50)
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Complete flow test failed: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False

def check_database_integrity():
    """Check database integrity for bulletins"""
    try:
        print("\n🔍 Checking database integrity...")
        
        from fleet_app.models_entreprise import Employe, ParametrePaie, PaieEmploye
        from django.db import connection
        
        cursor = connection.cursor()
        
        # Check tables exist
        tables = ['Employes', 'ParametresPaie', 'PaieEmployes', 'PresenceJournaliere']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} records")
            except Exception as e:
                print(f"❌ {table}: {e}")
        
        # Test model queries
        try:
            employes_count = Employe.objects.count()
            print(f"✅ Employe model query: {employes_count} records")
        except Exception as e:
            print(f"❌ Employe model query failed: {e}")
        
        try:
            params_count = ParametrePaie.objects.count()
            print(f"✅ ParametrePaie model query: {params_count} records")
        except Exception as e:
            print(f"❌ ParametrePaie model query failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database integrity check failed: {e}")
        return False

def create_simple_bulletins_view():
    """Create a simplified bulletins view for testing"""
    try:
        print("\n🔧 Creating simplified bulletins view...")
        
        simple_view_code = '''
@login_required
def bulletin_paie_list_simple(request):
    """Simplified bulletins view for debugging"""
    from datetime import datetime
    from fleet_app.models_entreprise import Employe
    
    try:
        # Get basic parameters
        mois_actuel = int(request.GET.get('mois', datetime.now().month))
        annee_actuelle = int(request.GET.get('annee', datetime.now().year))
        
        # Get employees
        employes = Employe.objects.filter(user=request.user)[:5]  # Limit to 5 for testing
        
        context = {
            'bulletins_data': [],
            'employes': employes,
            'mois_actuel': mois_actuel,
            'annee_actuelle': annee_actuelle,
            'mois_nom': 'Test',
            'entreprise': None,
        }
        
        return render(request, 'fleet_app/entreprise/bulletin_paie_list.html', context)
        
    except Exception as e:
        from django.http import HttpResponse
        return HttpResponse(f"Error in simple view: {e}", status=500)
'''
        
        # Add to views file
        with open('fleet_app/views_management_complete.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'bulletin_paie_list_simple' not in content:
            # Add the simple view
            content += '\n' + simple_view_code
            
            with open('fleet_app/views_management_complete.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ Simple view added to views_management_complete.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create simple view: {e}")
        return False

def test_url_patterns():
    """Test URL patterns and routing"""
    try:
        print("\n🔍 Testing URL patterns...")
        
        from django.urls import reverse, resolve
        
        # Test reverse lookup
        try:
            url = reverse('fleet_app:bulletin_paie_list')
            print(f"✅ Reverse lookup successful: {url}")
        except Exception as e:
            print(f"❌ Reverse lookup failed: {e}")
        
        # Test resolution
        try:
            resolver = resolve('/bulletins-paie/')
            print(f"✅ URL resolves to: {resolver.func.__name__}")
            print(f"✅ View module: {resolver.func.__module__}")
        except Exception as e:
            print(f"❌ URL resolution failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL pattern test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 DIAGNOSTIC FINAL - Bulletins de Paie")
    print("=" * 60)
    
    # Run comprehensive tests
    db_ok = check_database_integrity()
    url_ok = test_url_patterns()
    flow_ok = test_complete_flow()
    
    print(f"\n📊 RÉSULTATS FINAUX:")
    print(f"Base de données: {'✅' if db_ok else '❌'}")
    print(f"URLs: {'✅' if url_ok else '❌'}")
    print(f"Flow complet: {'✅' if flow_ok else '❌'}")
    
    if not flow_ok:
        print("\n🔧 Créer une vue simplifiée pour le debug...")
        create_simple_bulletins_view()
        
        print("\n💡 SOLUTIONS RECOMMANDÉES:")
        print("1. Vérifier les logs du serveur Django en temps réel")
        print("2. Tester avec une vue simplifiée")
        print("3. Vérifier les permissions et middleware")
        print("4. Redémarrer complètement le serveur Django")
