# 🔧 Fix Migration PythonAnywhere

## 🐛 Problème

```
django.db.migrations.exceptions.NodeNotFoundError: 
Migration fleet_app.0019_add_frais_km_to_paie dependencies reference 
nonexistent parent node ('fleet_app', '0018_add_frais_kilometrique')
```

**Cause** : La migration `0018_add_frais_kilometrique` n'existe pas sur PythonAnywhere

---

## 🔍 Diagnostic

### Étape 1 : Vérifier les migrations sur PythonAnywhere

```bash
cd ~/guineegest
source .venv/bin/activate
python manage.py showmigrations fleet_app
```

Cela affichera toutes les migrations et leur statut (appliquées ou non).

---

## ✅ Solutions

### Solution 1 : Fusionner les Migrations (RECOMMANDÉ)

Si `0018` n'existe pas sur le serveur, fusionnons `0018` et `0019` en une seule migration.

#### Étape 1 : Sur votre machine locale

```bash
# Supprimer les migrations 0018 et 0019
rm fleet_app/migrations/0018_add_frais_kilometrique.py
rm fleet_app/migrations/0019_add_frais_km_to_paie.py

# Recréer une migration unique
python manage.py makemigrations fleet_app --name add_frais_kilometrique_complete
```

#### Étape 2 : Vérifier la nouvelle migration

La nouvelle migration devrait inclure :
- Modèle `FraisKilometrique`
- Champ `valeur_km` dans `Employe`
- Champ `montant_frais_kilometriques` dans `PaieEmploye`

#### Étape 3 : Commiter et pousser

```bash
git add fleet_app/migrations/
git commit -m "Fix: Fusion migrations 0018 et 0019 en une seule"
git push origin main
```

#### Étape 4 : Sur PythonAnywhere

```bash
cd ~/guineegest
git pull origin main
python manage.py migrate fleet_app
```

---

### Solution 2 : Modifier la Dépendance de 0019

Si vous voulez garder les migrations séparées, modifiez la dépendance de `0019`.

#### Sur votre machine locale

Ouvrir `fleet_app/migrations/0019_add_frais_km_to_paie.py` et modifier :

**Avant** :
```python
dependencies = [
    ('fleet_app', '0018_add_frais_kilometrique'),
]
```

**Après** (remplacer par la dernière migration existante sur le serveur) :
```python
dependencies = [
    ('fleet_app', '0017_vehicule_fournisseur'),  # ou la dernière migration du serveur
]
```

Puis :
```bash
git add fleet_app/migrations/0019_add_frais_km_to_paie.py
git commit -m "Fix: Correction dépendance migration 0019"
git push origin main
```

---

### Solution 3 : Fake Migration 0018 sur PythonAnywhere

Si `0018` existe localement mais pas sur le serveur :

#### Sur PythonAnywhere

```bash
cd ~/guineegest
source .venv/bin/activate

# Copier la migration 0018 depuis GitHub
git pull origin main

# Appliquer 0018 en mode fake si le modèle existe déjà
python manage.py migrate fleet_app 0018 --fake

# Puis appliquer 0019 normalement
python manage.py migrate fleet_app
```

---

## 🔍 Vérifier la Dernière Migration sur PythonAnywhere

### Commande

```bash
cd ~/guineegest
source .venv/bin/activate
python manage.py showmigrations fleet_app | grep '\[X\]' | tail -1
```

Cela affichera la dernière migration appliquée.

### Exemple de sortie

```
[X] 0017_vehicule_fournisseur
```

---

## 📝 Commandes Complètes

### Diagnostic Complet

```bash
cd ~/guineegest
source .venv/bin/activate

# Voir toutes les migrations
python manage.py showmigrations fleet_app

# Voir la dernière migration appliquée
python manage.py showmigrations fleet_app | grep '\[X\]' | tail -1

# Voir les migrations non appliquées
python manage.py showmigrations fleet_app | grep '\[ \]'
```

---

## 🎯 Recommandation

**Je recommande la Solution 1 (Fusion des migrations)** car :

1. ✅ Plus propre et plus simple
2. ✅ Évite les problèmes de dépendances
3. ✅ Une seule migration à appliquer
4. ✅ Pas de risque de conflit

---

## 📋 Checklist

### Sur votre machine locale

- [ ] Vérifier la dernière migration sur PythonAnywhere
- [ ] Choisir une solution (1, 2 ou 3)
- [ ] Appliquer la solution
- [ ] Tester localement : `python manage.py migrate`
- [ ] Commiter et pousser

### Sur PythonAnywhere

- [ ] `git pull origin main`
- [ ] `python manage.py migrate fleet_app`
- [ ] Vérifier : `python manage.py showmigrations fleet_app`
- [ ] Redémarrer l'application web

---

## 🆘 Si le Problème Persiste

### Option 1 : Réinitialiser les migrations (ATTENTION : Perte de données)

```bash
# Sur PythonAnywhere
python manage.py migrate fleet_app zero
python manage.py migrate fleet_app
```

### Option 2 : Appliquer manuellement le SQL

```bash
# Voir le SQL de la migration
python manage.py sqlmigrate fleet_app 0019

# Appliquer manuellement dans MySQL
# Puis marquer comme appliquée
python manage.py migrate fleet_app 0019 --fake
```

---

## 📞 Support

**Fichier** : `FIX_MIGRATION_PYTHONANYWHERE.md`  
**Date** : 07 Octobre 2025  
**Statut** : Guide de résolution complet
