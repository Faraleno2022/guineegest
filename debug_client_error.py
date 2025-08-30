import os
import django
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def debug_client_request():
    try:
        print("🔍 Debugging Django Client request...")
        client = Client()
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        if created:
            user.set_password('testpass')
            user.save()
        
        print(f"✅ User created/found: {user.username}")
        
        # Login
        client.force_login(user)
        print("✅ User logged in")
        
        # Make request with detailed error handling
        print("🔍 Making request to /bulletins-paie/...")
        response = client.get('/bulletins-paie/')
        
        print(f"📊 Response status: {response.status_code}")
        
        if response.status_code == 500:
            print("❌ 500 ERROR DETECTED!")
            
            # Try to get error details
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8', errors='ignore')
                print(f"📋 Response content length: {len(content)}")
                
                # Look for Django error page
                if 'Traceback' in content or 'Exception' in content:
                    print("🔍 Error traceback found in response:")
                    # Extract error section
                    lines = content.split('\n')
                    in_traceback = False
                    for line in lines:
                        if 'Traceback' in line or in_traceback:
                            in_traceback = True
                            print(line)
                            if 'Exception:' in line or 'Error:' in line:
                                break
                
                # Look for specific error patterns
                if 'OperationalError' in content:
                    print("🔍 Database OperationalError detected")
                if 'TemplateDoesNotExist' in content:
                    print("🔍 Template error detected")
                if 'ImportError' in content:
                    print("🔍 Import error detected")
        
        elif response.status_code == 200:
            print("✅ Request successful!")
            
        return response.status_code
        
    except Exception as e:
        print(f"❌ Exception during client test: {type(e).__name__}: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    debug_client_request()
