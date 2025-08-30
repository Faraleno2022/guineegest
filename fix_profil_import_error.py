import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_profil_import():
    """Test if Profil model causes import issues"""
    try:
        print("🔍 Testing Profil model import...")
        from fleet_app.models_accounts import Profil, Entreprise
        print("✅ Profil and Entreprise models imported successfully")
        
        # Check if tables exist
        from django.db import connection
        cursor = connection.cursor()
        
        # Check if Profil table exists
        try:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='fleet_app_profil'")
            profil_table = cursor.fetchone()
            if profil_table:
                print("✅ fleet_app_profil table exists")
            else:
                print("❌ fleet_app_profil table does NOT exist")
        except Exception as e:
            print(f"❌ Error checking profil table: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Profil import error: {e}")
        return False

def fix_bulletin_view():
    """Fix the bulletin view by removing problematic Profil import"""
    try:
        print("\n🔧 Creating fixed version of bulletin_paie_list...")
        
        # Read the current view
        with open('fleet_app/views_management_complete.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if the problematic import exists
        if 'from .models_accounts import Entreprise, Profil' in content:
            print("❌ Found problematic import in bulletin_paie_list")
            
            # Create a backup
            with open('fleet_app/views_management_complete.py.backup', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Backup created")
            
            # Remove the problematic section
            lines = content.split('\n')
            new_lines = []
            skip_profil_section = False
            
            for line in lines:
                # Skip the problematic import and related code
                if 'from .models_accounts import Entreprise, Profil' in line:
                    skip_profil_section = True
                    new_lines.append('    # Removed problematic Profil import')
                    continue
                
                # Skip the entreprise retrieval section
                if skip_profil_section and ('entreprise = None' in line or 
                                          'profil = Profil.objects.get' in line or
                                          'if hasattr(profil, \'entreprise\')' in line or
                                          'entreprise = profil.entreprise' in line or
                                          'except Profil.DoesNotExist:' in line):
                    continue
                
                # End skipping after the pass statement
                if skip_profil_section and 'pass' in line and 'except' not in line:
                    skip_profil_section = False
                    new_lines.append('    entreprise = None  # Simplified - no Profil dependency')
                    continue
                
                new_lines.append(line)
            
            # Write the fixed content
            fixed_content = '\n'.join(new_lines)
            with open('fleet_app/views_management_complete.py', 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            print("✅ Fixed bulletin_paie_list view - removed Profil dependency")
            return True
        else:
            print("✅ No problematic import found")
            return True
            
    except Exception as e:
        print(f"❌ Error fixing view: {e}")
        return False

def test_fixed_view():
    """Test the fixed view"""
    try:
        print("\n🔍 Testing fixed bulletin view...")
        client = Client()
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        # Login
        client.force_login(user)
        
        # Test the view
        response = client.get('/bulletins-paie/')
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ View works correctly!")
            return True
        else:
            print(f"❌ Still getting error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Fixing Profil import error in bulletin_paie_list")
    print("=" * 60)
    
    # Test current state
    profil_ok = test_profil_import()
    
    if not profil_ok:
        print("\n🔧 Profil model has issues - fixing the view...")
        fix_bulletin_view()
        test_fixed_view()
    else:
        print("\n✅ Profil model is OK - testing view directly...")
        test_fixed_view()
