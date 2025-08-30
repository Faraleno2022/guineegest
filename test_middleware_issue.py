import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.middleware.csrf import get_token
from django.conf import settings

def test_csrf_and_middleware():
    """Test CSRF and middleware issues"""
    try:
        print("🔍 Testing CSRF and middleware...")
        
        client = Client(enforce_csrf_checks=True)
        
        # Create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        # First, get CSRF token
        response = client.get('/login/')
        csrf_token = None
        if hasattr(response, 'cookies') and 'csrftoken' in response.cookies:
            csrf_token = response.cookies['csrftoken'].value
        
        print(f"✅ CSRF token obtained: {csrf_token is not None}")
        
        # Login with CSRF
        client.force_login(user)
        
        # Test bulletins page with proper headers
        headers = {}
        if csrf_token:
            headers['HTTP_X_CSRFTOKEN'] = csrf_token
        
        response = client.get('/bulletins-paie/', **headers)
        
        print(f"📊 Response status with CSRF: {response.status_code}")
        
        if response.status_code == 400:
            content = response.content.decode('utf-8', errors='ignore')
            if 'CSRF' in content:
                print("❌ CSRF verification failed")
            elif 'Bad Request' in content:
                print("❌ Bad Request - checking content...")
                print(content[:500])
        
        return response.status_code
        
    except Exception as e:
        print(f"❌ CSRF test failed: {e}")
        return None

def test_without_csrf():
    """Test without CSRF enforcement"""
    try:
        print("\n🔍 Testing without CSRF enforcement...")
        
        client = Client(enforce_csrf_checks=False)
        
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        
        client.force_login(user)
        
        response = client.get('/bulletins-paie/')
        
        print(f"📊 Response status without CSRF: {response.status_code}")
        
        if response.status_code != 200:
            content = response.content.decode('utf-8', errors='ignore')
            print(f"📋 Error content (first 1000 chars):")
            print(content[:1000])
        
        return response.status_code
        
    except Exception as e:
        print(f"❌ Non-CSRF test failed: {e}")
        return None

def check_middleware_config():
    """Check middleware configuration"""
    try:
        print("\n🔍 Checking middleware configuration...")
        
        middleware = settings.MIDDLEWARE
        print(f"✅ Middleware count: {len(middleware)}")
        
        for i, mw in enumerate(middleware):
            print(f"  {i+1}. {mw}")
        
        # Check for problematic middleware
        csrf_middleware = 'django.middleware.csrf.CsrfViewMiddleware' in middleware
        auth_middleware = 'django.contrib.auth.middleware.AuthenticationMiddleware' in middleware
        
        print(f"✅ CSRF middleware: {csrf_middleware}")
        print(f"✅ Auth middleware: {auth_middleware}")
        
        return True
        
    except Exception as e:
        print(f"❌ Middleware check failed: {e}")
        return False

def test_url_resolution():
    """Test URL resolution"""
    try:
        print("\n🔍 Testing URL resolution...")
        
        from django.urls import resolve, reverse
        
        # Test reverse lookup
        url = reverse('fleet_app:bulletin_paie_list')
        print(f"✅ Reverse URL: {url}")
        
        # Test resolution
        resolver = resolve('/bulletins-paie/')
        print(f"✅ Resolves to: {resolver.func.__name__}")
        print(f"✅ Module: {resolver.func.__module__}")
        
        return True
        
    except Exception as e:
        print(f"❌ URL resolution failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing middleware and CSRF issues")
    print("=" * 60)
    
    # Run all tests
    check_middleware_config()
    test_url_resolution()
    
    status_with_csrf = test_csrf_and_middleware()
    status_without_csrf = test_without_csrf()
    
    print(f"\n📊 SUMMARY:")
    print(f"With CSRF enforcement: {status_with_csrf}")
    print(f"Without CSRF enforcement: {status_without_csrf}")
    
    if status_without_csrf == 200:
        print("✅ Issue is likely CSRF-related")
    elif status_without_csrf != 200:
        print("❌ Issue is deeper than CSRF - likely view or template problem")
