#!/usr/bin/env python
"""Script pour tester la génération de factures mensuelles"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.contrib.auth.models import User
from django.test import RequestFactory
from fleet_app.views_location import generer_factures_mensuelles
from django.utils import timezone

# Créer une fausse requête POST
factory = RequestFactory()
user = User.objects.first()

if not user:
    print("❌ Aucun utilisateur trouvé dans la base de données")
    sys.exit(1)

print(f"✅ Utilisateur: {user.username}")

# Créer une requête POST avec les paramètres
now = timezone.now()
request = factory.post('/locations/factures/generation-mensuelle/', {
    'month': str(now.month),
    'year': str(now.year)
})
request.user = user

# Ajouter le header AJAX
request.META['HTTP_X_REQUESTED_WITH'] = 'XMLHttpRequest'

print(f"📅 Génération pour: {now.month}/{now.year}")

try:
    response = generer_factures_mensuelles(request)
    print(f"✅ Réponse HTTP: {response.status_code}")
    
    if response.status_code == 200:
        import json
        data = json.loads(response.content)
        print(f"✅ Succès: {data.get('success')}")
        print(f"📝 Message: {data.get('message')}")
        print(f"💰 Total: {data.get('total_mois', 0)} GNF")
        
        if 'details' in data:
            print(f"\n📊 Détails ({len(data['details'])} factures):")
            for detail in data['details']:
                print(f"  - {detail['vehicule']}: {detail['jours_travail']} jours → {detail['montant_ttc']} GNF")
    else:
        print(f"❌ Erreur: {response.content.decode('utf-8')}")
        
except Exception as e:
    print(f"❌ Exception: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
