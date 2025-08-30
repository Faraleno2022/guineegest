import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.template import Context, Template

def test_template_rendering():
    """Test if the template can be rendered"""
    try:
        print("🔍 Testing template rendering...")
        
        # Create minimal context
        context = {
            'bulletins_data': [],
            'mois_actuel': 12,
            'annee_actuelle': 2024,
            'mois_nom': 'Décembre',
            'cnss_activer': False,
            'cnss_taux': 5.0,
            'rts_type': 'PROGRESSIF',
            'rts_taux_fixe': 10.0,
            'entreprise': None,
            'page_obj': None,
            'is_paginated': False,
        }
        
        # Try to render the template
        rendered = render_to_string('fleet_app/entreprise/bulletin_paie_list.html', context)
        
        print(f"✅ Template rendered successfully - Length: {len(rendered)}")
        return True
        
    except Exception as e:
        print(f"❌ Template rendering failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_view_context():
    """Test the view context generation"""
    try:
        print("\n🔍 Testing view context generation...")
        
        from fleet_app.views_management_complete import bulletin_paie_list
        from django.test import RequestFactory
        
        factory = RequestFactory()
        request = factory.get('/bulletins-paie/')
        
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com'}
        )
        request.user = user
        
        # Patch the render function to capture context
        original_render = None
        captured_context = None
        
        def capture_render(request, template_name, context=None):
            nonlocal captured_context
            captured_context = context
            from django.http import HttpResponse
            return HttpResponse("OK")
        
        # Monkey patch render
        import django.shortcuts
        original_render = django.shortcuts.render
        django.shortcuts.render = capture_render
        
        try:
            response = bulletin_paie_list(request)
            print(f"✅ View executed - Status: {response.status_code}")
            
            if captured_context:
                print(f"✅ Context keys: {list(captured_context.keys())}")
                
                # Check for problematic context values
                for key, value in captured_context.items():
                    if value is None:
                        print(f"⚠️ None value for key: {key}")
                    elif hasattr(value, '__len__') and len(value) == 0:
                        print(f"📊 Empty collection for key: {key}")
            
            return True
            
        finally:
            # Restore original render
            django.shortcuts.render = original_render
        
    except Exception as e:
        print(f"❌ View context test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_minimal_template():
    """Create a minimal template for testing"""
    try:
        print("\n🔧 Creating minimal template for testing...")
        
        minimal_template = '''{% extends 'fleet_app/base.html' %}
{% block title %}Bulletins de Paie - Test{% endblock %}
{% block content %}
<div class="container">
    <h1>Bulletins de Paie - Version Minimale</h1>
    <p>Mois: {{ mois_nom }} {{ annee_actuelle }}</p>
    <p>Nombre de bulletins: {{ bulletins_data|length }}</p>
    
    {% if bulletins_data %}
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Matricule</th>
                        <th>Nom</th>
                        <th>Salaire Net</th>
                    </tr>
                </thead>
                <tbody>
                    {% for bulletin in bulletins_data %}
                    <tr>
                        <td>{{ bulletin.employe.matricule }}</td>
                        <td>{{ bulletin.employe.nom }}</td>
                        <td>{{ bulletin.net_a_payer|floatformat:2 }} GNF</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    {% else %}
        <div class="alert alert-info">
            Aucun bulletin de paie trouvé pour cette période.
        </div>
    {% endif %}
</div>
{% endblock %}'''
        
        # Save minimal template
        template_path = 'fleet_app/templates/fleet_app/entreprise/bulletin_paie_list_minimal.html'
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(minimal_template)
        
        print(f"✅ Minimal template created: {template_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create minimal template: {e}")
        return False

def test_with_minimal_template():
    """Test view with minimal template"""
    try:
        print("\n🔍 Testing with minimal template...")
        
        # Temporarily modify the view to use minimal template
        from fleet_app import views_management_complete
        
        # Read the view file
        view_file = 'fleet_app/views_management_complete.py'
        with open(view_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace template name
        modified_content = content.replace(
            "'fleet_app/entreprise/bulletin_paie_list.html'",
            "'fleet_app/entreprise/bulletin_paie_list_minimal.html'"
        )
        
        # Write modified version
        with open(view_file + '.minimal', 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print("✅ Created minimal version of view")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create minimal view: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing template rendering issues")
    print("=" * 60)
    
    # Run tests
    template_ok = test_template_rendering()
    context_ok = test_view_context()
    
    if not template_ok:
        print("\n🔧 Template has issues - creating minimal version...")
        create_minimal_template()
        test_with_minimal_template()
    
    print(f"\n📊 RESULTS:")
    print(f"Template rendering: {'✅' if template_ok else '❌'}")
    print(f"View context: {'✅' if context_ok else '❌'}")
