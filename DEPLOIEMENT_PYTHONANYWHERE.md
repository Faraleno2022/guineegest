# Configuration PostgreSQL sur PythonAnywhere

## Guide complet pour déployer GuinéeGest avec PostgreSQL sur PythonAnywhere

### 🔧 Prérequis

1. **Compte PythonAnywhere payant** - PostgreSQL n'est disponible que sur les comptes payants
2. **Projet Django** - Votre application GuinéeGest prête au déploiement

### 📋 Étapes de Configuration

#### 1. Activation du Service PostgreSQL

**Si vous avez un compte gratuit :**
- Allez sur la page **Account**
- Cliquez sur un bouton d'upgrade vers un compte payant
- Dans la boîte de dialogue, activez l'option **Postgres**
- Choisissez l'espace disque pour vos bases PostgreSQL
- Cliquez sur "Upgrade to this custom plan"

**Si vous avez déjà un compte payant :**
- Allez sur la page **Account**
- Cliquez sur "Customize your plan"
- Activez l'option **Postgres**
- Choisissez l'espace disque désiré
- Cliquez sur "Switch to this custom plan"

#### 2. Création du Serveur PostgreSQL

1. Allez dans l'onglet **Databases**
2. Cliquez sur le bouton **Postgres**
3. Créez votre serveur PostgreSQL
4. Définissez le mot de passe administrateur

#### 3. Configuration du Mot de Passe Superuser

1. Dans l'onglet **Databases**
2. Trouvez le formulaire "Postgres Superuser password"
3. Entrez un mot de passe sécurisé
4. ⚠️ **Important :** Ce mot de passe est stocké en texte clair et doit être différent de votre mot de passe de compte

#### 4. Création de la Base de Données et Utilisateur

Ouvrez une console Postgres depuis l'onglet Databases et exécutez :

```sql
-- Créer la base de données
CREATE DATABASE guineegest_db;

-- Créer l'utilisateur
CREATE USER guineegest_user WITH PASSWORD 'votre-mot-de-passe-securise';

-- Configuration de l'utilisateur
ALTER ROLE guineegest_user SET client_encoding TO 'utf8';
ALTER ROLE guineegest_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE guineegest_user SET timezone TO 'UTC';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE guineegest_db TO guineegest_user;
```

#### 5. Configuration Django

**Notez vos paramètres de connexion :**
- **Hostname :** `votrenom-667.postgres.pythonanywhere-services.com`
- **Port :** `10667` (exemple)
- **Database :** `guineegest_db`
- **User :** `guineegest_user`
- **Password :** `votre-mot-de-passe-securise`

**Configuration dans settings.py :**

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'guineegest_db',
        'USER': 'guineegest_user',
        'PASSWORD': 'votre-mot-de-passe-securise',
        'HOST': 'votrenom-667.postgres.pythonanywhere-services.com',
        'PORT': 10667,
    }
}
```

**Ou avec variables d'environnement :**

```python
import os
from dotenv import load_dotenv

load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DJANGO_DB_NAME', 'guineegest_db'),
        'USER': os.getenv('DJANGO_DB_USER', 'guineegest_user'),
        'PASSWORD': os.getenv('DJANGO_DB_PASSWORD'),
        'HOST': os.getenv('DJANGO_DB_HOST', 'votrenom-667.postgres.pythonanywhere-services.com'),
        'PORT': os.getenv('DJANGO_DB_PORT', '10667'),
    }
}
```

#### 6. Fichier .env sur PythonAnywhere

Créez un fichier `.env` dans votre répertoire de projet :

```env
DJANGO_SECRET_KEY=votre-cle-secrete-django
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=votrenom.pythonanywhere.com
DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_NAME=guineegest_db
DJANGO_DB_USER=guineegest_user
DJANGO_DB_PASSWORD=votre-mot-de-passe-securise
DJANGO_DB_HOST=votrenom-667.postgres.pythonanywhere-services.com
DJANGO_DB_PORT=10667
```

#### 7. Installation des Dépendances

Dans une console Bash sur PythonAnywhere :

```bash
# Installer psycopg2
pip3.10 install --user psycopg2-binary

# Installer python-dotenv si nécessaire
pip3.10 install --user python-dotenv

# Installer toutes les dépendances
pip3.10 install --user -r requirements.txt
```

#### 8. Migration de la Base de Données

```bash
# Appliquer les migrations
python3.10 manage.py migrate

# Créer un superuser (optionnel)
python3.10 manage.py createsuperuser

# Collecter les fichiers statiques
python3.10 manage.py collectstatic --noinput
```

#### 9. Configuration de l'Application Web

1. Allez dans l'onglet **Web**
2. Créez une nouvelle application web
3. Choisissez **Manual configuration** et **Python 3.10**
4. Configurez le fichier WSGI :

```python
import os
import sys

# Ajouter le chemin de votre projet
path = '/home/votrenom/Gestion_parck'
if path not in sys.path:
    sys.path.insert(0, path)

# Charger les variables d'environnement
from dotenv import load_dotenv
load_dotenv(os.path.join(path, '.env'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'fleet_management.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 🔒 Sécurité et Bonnes Pratiques

1. **Mots de passe sécurisés :** Utilisez des mots de passe forts et uniques
2. **Variables d'environnement :** Ne jamais committer les mots de passe dans Git
3. **DEBUG=False :** Toujours désactiver le debug en production
4. **ALLOWED_HOSTS :** Configurer correctement les hôtes autorisés
5. **Sauvegardes régulières :** Configurez des sauvegardes automatiques de votre base PostgreSQL

### 🔧 Dépannage

**Erreur de connexion :**
- Vérifiez les paramètres de connexion (host, port, user, password)
- Assurez-vous que psycopg2-binary est installé
- Vérifiez que les variables d'environnement sont correctement chargées

**Erreur de migration :**
- Vérifiez que l'utilisateur a les privilèges nécessaires
- Assurez-vous que la base de données existe

**Erreur 500 :**
- Vérifiez les logs d'erreur dans l'onglet Web
- Assurez-vous que DEBUG=True temporairement pour voir les erreurs détaillées

### 📚 Ressources Utiles

- [Documentation PythonAnywhere PostgreSQL](https://help.pythonanywhere.com/pages/PostgresGettingStarted)
- [Déploiement Django sur PythonAnywhere](https://help.pythonanywhere.com/pages/DeployExistingDjangoProject)
- [Accès PostgreSQL depuis l'extérieur](https://help.pythonanywhere.com/pages/AccessingPostgresFromOutsidePythonAnywhere)

### 💡 Conseils Supplémentaires

1. **Test local :** Testez votre configuration PostgreSQL localement avant le déploiement
2. **Migrations :** Créez et testez vos migrations avant de les appliquer en production
3. **Monitoring :** Surveillez les performances et l'utilisation de votre base de données
4. **Backup :** Configurez des sauvegardes régulières dès le début
