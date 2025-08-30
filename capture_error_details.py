import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import traceback

def capture_full_error():
    """Capture complete error details from the bulletins page"""
    try:
        print("🔍 Capturing full error details...")
        client = Client()
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        # Login
        client.force_login(user)
        
        # Make request and capture full response
        response = client.get('/bulletins-paie/', follow=True)
        
        print(f"📊 Final status: {response.status_code}")
        print(f"📊 Redirect chain: {response.redirect_chain}")
        
        # Get response content
        content = response.content.decode('utf-8', errors='ignore')
        
        print(f"📊 Content length: {len(content)} characters")
        
        # Look for specific error indicators
        if 'CSRF' in content:
            print("🔍 CSRF token issue detected")
        
        if 'Bad Request' in content:
            print("🔍 Bad Request error detected")
        
        if 'form' in content.lower() and 'error' in content.lower():
            print("🔍 Form validation error detected")
        
        # Extract first 2000 characters to see the error
        print("\n📋 Response content (first 2000 chars):")
        print("-" * 50)
        print(content[:2000])
        print("-" * 50)
        
        # Look for Django error patterns
        if '<title>' in content:
            title_start = content.find('<title>') + 7
            title_end = content.find('</title>')
            if title_end > title_start:
                title = content[title_start:title_end]
                print(f"📋 Page title: {title}")
        
        return response.status_code
        
    except Exception as e:
        print(f"❌ Exception: {type(e).__name__}: {e}")
        traceback.print_exc()
        return None

def test_direct_view_call():
    """Test calling the view function directly"""
    try:
        print("\n🔍 Testing direct view call...")
        from fleet_app.views_management_complete import bulletin_paie_list
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/bulletins-paie/')
        
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        request.user = user
        
        response = bulletin_paie_list(request)
        print(f"✅ Direct call status: {response.status_code}")
        
        return response.status_code
        
    except Exception as e:
        print(f"❌ Direct call failed: {type(e).__name__}: {e}")
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("🚀 Capturing complete error details for bulletins-paie")
    print("=" * 60)
    
    # Test both methods
    client_status = capture_full_error()
    direct_status = test_direct_view_call()
    
    print(f"\n📊 SUMMARY:")
    print(f"Client test: {client_status}")
    print(f"Direct call: {direct_status}")
    
    if client_status != direct_status:
        print("⚠️ Different results - likely middleware or URL routing issue")
