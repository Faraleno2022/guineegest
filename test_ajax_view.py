#!/usr/bin/env python
"""
Script de test pour vérifier la vue AJAX configuration_montant_statut
"""
import os
import sys
import django
from django.conf import settings
from django.test import RequestFactory
from django.contrib.auth.models import User

# Ajouter le répertoire du projet au path
sys.path.append('c:/Users/faral/Desktop/Gestion_parck')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.views_management import configuration_montant_statut

def test_ajax_view():
    """Test de la vue AJAX configuration_montant_statut"""
    print("🧪 TEST DE LA VUE AJAX")
    print("=" * 50)
    
    try:
        # Créer une factory de requêtes
        factory = RequestFactory()
        
        # Récupérer le premier utilisateur
        user = User.objects.first()
        if not user:
            print("❌ Aucun utilisateur trouvé")
            return
            
        print(f"👤 Utilisateur de test: {user.username}")
        
        # Créer une requête POST simulée
        post_data = {
            'montant_absent': '30000',
            'csrfmiddlewaretoken': 'test-token'
        }
        
        request = factory.post('/management/configuration-montants-statuts/', post_data)
        request.user = user
        
        print(f"📤 Envoi de la requête POST avec: {post_data}")
        
        # Appeler la vue
        response = configuration_montant_statut(request)
        
        print(f"📥 Status code: {response.status_code}")
        print(f"📥 Content-Type: {response.get('Content-Type', 'Non défini')}")
        
        if hasattr(response, 'content'):
            import json
            try:
                content = json.loads(response.content.decode('utf-8'))
                print(f"📥 Réponse JSON: {content}")
                
                if content.get('success'):
                    print("✅ VUE AJAX FONCTIONNE CORRECTEMENT!")
                else:
                    print(f"❌ Erreur dans la vue: {content.get('error', 'Erreur inconnue')}")
            except json.JSONDecodeError as e:
                print(f"❌ Erreur de décodage JSON: {e}")
                print(f"📥 Contenu brut: {response.content}")
        
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ajax_view()
