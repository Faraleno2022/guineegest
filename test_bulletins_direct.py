#!/usr/bin/env python
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fleet_management.settings")
    django.setup()
    
    try:
        from fleet_app.views_management_complete import bulletin_paie_list
        from django.test import RequestFactory
        from django.contrib.auth.models import User
        
        # Create test request
        factory = RequestFactory()
        request = factory.get('/bulletins-paie/')
        
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        request.user = user
        
        print("🔍 Testing bulletin_paie_list view...")
        response = bulletin_paie_list(request)
        print(f"✅ View executed successfully - Status: {response.status_code}")
        
    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
