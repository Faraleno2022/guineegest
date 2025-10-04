# 🔧 Fix - Erreur de Connexion Base de Données PythonAnywhere

## ❌ Erreur Rencontrée

```
MySQLdb.OperationalError: (1045, "Access denied for user 'gestionnairedepa$default'@'10.0.5.186' (using password: YES)")
```

**Traduction** : Accès refusé pour l'utilisateur de la base de données.

---

## 🔍 Causes Possibles

1. **Mot de passe incorrect** dans le fichier de configuration
2. **Nom d'utilisateur incorrect** (devrait être `gestionnairedeparc$default` et non `gestionnairedepa$default`)
3. **Base de données non créée** sur PythonAnywhere
4. **Permissions insuffisantes** pour l'utilisateur

---

## ✅ Solution : Vérifier et Corriger la Configuration

### Étape 1 : Vérifier le Nom d'Utilisateur

Le nom d'utilisateur MySQL sur PythonAnywhere suit le format :
```
<username>$<database_name>
```

Pour vous, ça devrait être :
```
gestionnairedeparc$default
```

**⚠️ Attention** : L'erreur montre `gestionnairedepa$default` (tronqué), ce qui peut être un problème d'affichage ou une vraie erreur.

### Étape 2 : Vérifier le Fichier de Configuration

Sur PythonAnywhere, éditez le fichier de configuration :

```bash
nano ~/guineegest/gestion_parc/settings.py
```

Cherchez la section `DATABASES` et vérifiez :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'gestionnairedeparc$default',  # Nom de la base
        'USER': 'gestionnairedeparc',           # Nom d'utilisateur (SANS $default)
        'PASSWORD': 'VOTRE_MOT_DE_PASSE',      # Mot de passe MySQL
        'HOST': 'gestionnairedeparc.mysql.pythonanywhere-services.com',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

**Points importants** :
- `NAME` : Nom complet avec `$` → `gestionnairedeparc$default`
- `USER` : Nom d'utilisateur SANS `$default` → `gestionnairedeparc`
- `HOST` : Doit être le hostname MySQL de PythonAnywhere

### Étape 3 : Récupérer les Bonnes Informations

1. **Connectez-vous à PythonAnywhere** : https://www.pythonanywhere.com
2. Allez dans l'onglet **"Databases"**
3. Notez les informations :
   - **Database name** : `gestionnairedeparc$default`
   - **Username** : `gestionnairedeparc`
   - **MySQL hostname** : `gestionnairedeparc.mysql.pythonanywhere-services.com`

### Étape 4 : Réinitialiser le Mot de Passe (si nécessaire)

Si vous avez oublié le mot de passe :

1. Dans l'onglet **"Databases"** sur PythonAnywhere
2. Trouvez votre base de données `gestionnairedeparc$default`
3. Cliquez sur **"Reset password"**
4. Notez le nouveau mot de passe
5. Mettez-le à jour dans `settings.py`

---

## 🔧 Commandes de Correction

### Sur PythonAnywhere (via Bash Console)

```bash
# 1. Aller dans le répertoire du projet
cd ~/guineegest

# 2. Activer l'environnement virtuel
source .venv/bin/activate

# 3. Éditer le fichier settings.py
nano gestion_parc/settings.py

# 4. Modifier la section DATABASES avec les bonnes informations

# 5. Sauvegarder (Ctrl+O, Enter, Ctrl+X)

# 6. Tester la connexion
python manage.py check

# 7. Si OK, appliquer les migrations
python manage.py migrate

# 8. Recharger l'application web
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

---

## 📝 Exemple de Configuration Correcte

```python
# gestion_parc/settings.py

import os
from pathlib import Path

# ... autres configurations ...

# Configuration pour PythonAnywhere
if 'PYTHONANYWHERE_DOMAIN' in os.environ or 'gestionnairedeparc.pythonanywhere.com' in os.environ.get('ALLOWED_HOSTS', ''):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'gestionnairedeparc$default',
            'USER': 'gestionnairedeparc',
            'PASSWORD': os.environ.get('DB_PASSWORD', 'VOTRE_MOT_DE_PASSE_ICI'),
            'HOST': 'gestionnairedeparc.mysql.pythonanywhere-services.com',
            'PORT': '3306',
            'OPTIONS': {
                'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
                'charset': 'utf8mb4',
            },
        }
    }
else:
    # Configuration locale (SQLite)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
```

---

## 🔐 Sécurité : Utiliser des Variables d'Environnement

Pour plus de sécurité, utilisez un fichier `.env` :

### 1. Créer un fichier `.env` sur PythonAnywhere

```bash
cd ~/guineegest
nano .env
```

Contenu :
```
DB_NAME=gestionnairedeparc$default
DB_USER=gestionnairedeparc
DB_PASSWORD=votre_mot_de_passe_mysql
DB_HOST=gestionnairedeparc.mysql.pythonanywhere-services.com
DB_PORT=3306
```

### 2. Installer python-decouple

```bash
pip install python-decouple
```

### 3. Modifier settings.py

```python
from decouple import config

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

---

## ✅ Vérification Finale

Après avoir corrigé la configuration :

```bash
# 1. Tester la connexion
python manage.py check

# 2. Vérifier les migrations
python manage.py showmigrations

# 3. Appliquer les migrations
python manage.py migrate

# 4. Créer un superutilisateur (si nécessaire)
python manage.py createsuperuser

# 5. Collecter les fichiers statiques
python manage.py collectstatic --noinput

# 6. Recharger l'application
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

---

## 🆘 Si le Problème Persiste

### Option 1 : Recréer la Base de Données

1. Sur PythonAnywhere, onglet **"Databases"**
2. Supprimer la base `gestionnairedeparc$default`
3. Créer une nouvelle base avec le même nom
4. Noter le nouveau mot de passe
5. Mettre à jour `settings.py`
6. Relancer les migrations

### Option 2 : Vérifier les Logs

```bash
# Voir les logs d'erreur
tail -f /var/log/gestionnairedeparc.pythonanywhere.com.error.log

# Voir les logs d'accès
tail -f /var/log/gestionnairedeparc.pythonanywhere.com.access.log
```

### Option 3 : Contacter le Support PythonAnywhere

Si rien ne fonctionne, ouvrez un ticket de support sur PythonAnywhere avec :
- Le message d'erreur complet
- Votre nom d'utilisateur
- Le nom de votre base de données

---

## 📋 Checklist de Résolution

- [ ] Vérifier le nom d'utilisateur dans settings.py
- [ ] Vérifier le mot de passe MySQL
- [ ] Vérifier le hostname MySQL
- [ ] Vérifier que la base de données existe
- [ ] Tester avec `python manage.py check`
- [ ] Appliquer les migrations
- [ ] Recharger l'application web
- [ ] Tester l'accès au site

---

## 🎯 Résumé Rapide

**Le problème** : Mauvaise configuration de connexion MySQL

**La solution** :
1. Vérifier `USER` = `gestionnairedeparc` (SANS $default)
2. Vérifier `NAME` = `gestionnairedeparc$default` (AVEC $default)
3. Vérifier le mot de passe
4. Vérifier le hostname
5. Relancer `python manage.py migrate`

---

**Date** : 04 Octobre 2025  
**Priorité** : 🔴 URGENTE  
**Statut** : Guide de résolution fourni
