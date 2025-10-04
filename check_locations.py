#!/usr/bin/env python
"""Script pour vérifier les locations et l'entreprise de l'utilisateur"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models_location import LocationVehicule
from django.contrib.auth.models import User

# Récupérer le premier utilisateur
user = User.objects.first()
print(f"User: {user.username}")
print(f"Has profil: {hasattr(user, 'profil')}")

if hasattr(user, 'profil'):
    profil = user.profil
    print(f"Profil exists: {profil}")
    print(f"Has entreprise: {hasattr(profil, 'entreprise')}")
    if hasattr(profil, 'entreprise'):
        print(f"Entreprise: {profil.entreprise}")
else:
    print("No profil attribute")

# Vérifier les locations
locations = LocationVehicule.objects.filter(user=user)
print(f"\nTotal locations for user: {locations.count()}")

for loc in locations[:5]:
    print(f"Location {loc.id}: vehicule={loc.vehicule}, entreprise={loc.entreprise}, user={loc.user}")
