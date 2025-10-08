# 🔧 Fix Migration 0003 - Duplicate Column

## 🐛 Problème

```
MySQLdb.OperationalError: (1060, "Duplicate column name 'date_naissance'")
```

La migration `0003_auto_20251008_0609` essaie d'ajouter une colonne qui existe déjà.

---

## ✅ Solution Immédiate

### Sur PythonAnywhere

```bash
cd ~/guineegest
source .venv/bin/activate

# Fake la migration problématique
python manage.py migrate fleet_app 0003 --fake

# Continuer avec les autres migrations
python manage.py migrate fleet_app

# Redémarrer
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

---

## 🔍 Vérification

```bash
# Voir les migrations appliquées
python manage.py showmigrations fleet_app

# Vérifier la structure de la table Chauffeur
python manage.py dbshell
```

```sql
DESCRIBE Chauffeurs;
```

---

## 📋 Commandes Complètes

```bash
cd ~/guineegest
source .venv/bin/activate

# 1. Fake la migration 0003
python manage.py migrate fleet_app 0003 --fake

# 2. Appliquer le reste
python manage.py migrate fleet_app

# 3. Vérifier
python manage.py showmigrations fleet_app | tail -10

# 4. Collecter statiques
python manage.py collectstatic --noinput

# 5. Redémarrer
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

---

## 🎯 Résultat Attendu

```
[X] 0003_auto_20251008_0609
[X] 0018_placeholder
[X] 0019_add_frais_km_to_paie
[X] 0020_add_frais_kilometrique
```

---

**Date** : 08 Octobre 2025  
**Priorité** : 🔴 URGENT
