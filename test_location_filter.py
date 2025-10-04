#!/usr/bin/env python
"""Script pour tester le filtrage des locations après correction"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models_location import LocationVehicule
from fleet_app.utils.decorators import queryset_filter_by_tenant
from django.contrib.auth.models import User
from django.test import RequestFactory

# Créer une fausse requête
factory = RequestFactory()
request = factory.get('/locations/')
request.user = User.objects.first()

print(f"User: {request.user.username}")

# Tester le filtrage
qs = LocationVehicule.objects.all()
print(f"Total locations in DB: {qs.count()}")

filtered_qs = queryset_filter_by_tenant(qs, request)
print(f"Filtered locations for user: {filtered_qs.count()}")

for loc in filtered_qs:
    print(f"  - Location {loc.id}: {loc.vehicule} ({loc.type_location})")
