#!/usr/bin/env python3
"""
Script pour corriger les migrations MySQL sur PythonAnywhere
Utilise ce script dans la console Bash PythonAnywhere
"""

import os
import sys

# Instructions pour PythonAnywhere
print("=== CORRECTION MIGRATIONS MYSQL PYTHONANYWHERE ===")
print()
print("Exécute ces commandes dans l'ordre dans la console Bash:")
print()

print("1. Marquer la migration problématique comme appliquée (fake):")
print("   python3.10 manage.py migrate fleet_app 0002 --fake")
print()

print("2. Marquer toutes les migrations jusqu'à 0009 comme appliquées:")
print("   python3.10 manage.py migrate fleet_app 0009 --fake")
print()

print("3. Appliquer les migrations importantes (user/entreprise):")
print("   python3.10 manage.py migrate fleet_app 0010")
print("   python3.10 manage.py migrate fleet_app 0011")
print("   python3.10 manage.py migrate fleet_app 0012")
print("   python3.10 manage.py migrate fleet_app 0013")
print("   python3.10 manage.py migrate fleet_app 0014")
print("   python3.10 manage.py migrate fleet_app 0015")
print("   python3.10 manage.py migrate fleet_app 0016")
print()

print("4. Appliquer toutes les migrations restantes:")
print("   python3.10 manage.py migrate")
print()

print("5. Vérifier l'état final:")
print("   python3.10 manage.py showmigrations fleet_app")
print()

print("6. Tester la structure de la base:")
print("   python3.10 manage.py shell")
print("   >>> from fleet_app.models import Vehicule, FournisseurVehicule")
print("   >>> print('Vehicule fields:', [f.name for f in Vehicule._meta.fields])")
print("   >>> print('Fournisseur fields:', [f.name for f in FournisseurVehicule._meta.fields])")
print("   >>> exit()")
print()

print("7. Reload l'application Web:")
print("   - Aller dans l'onglet Web")
print("   - Cliquer sur Reload")
print()

print("=== ALTERNATIVE SI PROBLÈME PERSISTE ===")
print()
print("Si les migrations continuent à échouer:")
print("1. Sauvegarder les données importantes")
print("2. Supprimer et recréer la base:")
print("   python3.10 manage.py flush --noinput")
print("   python3.10 manage.py migrate")
print("3. Recréer un superuser:")
print("   python3.10 manage.py createsuperuser")
print()

print("=== COMMANDES RAPIDES ===")
print()
print("# Marquer les migrations problématiques comme fake")
print("python3.10 manage.py migrate fleet_app 0002 --fake")
print("python3.10 manage.py migrate fleet_app 0003 --fake") 
print("python3.10 manage.py migrate fleet_app 0007 --fake")
print("python3.10 manage.py migrate fleet_app 0009 --fake")
print()
print("# Appliquer les migrations importantes")
print("python3.10 manage.py migrate fleet_app 0010")
print("python3.10 manage.py migrate")
print()
print("# Vérifier")
print("python3.10 manage.py showmigrations fleet_app")
