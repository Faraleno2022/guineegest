# Configuration PostgreSQL pour GuinéeGest

## 1. Installation de PostgreSQL

### Sur Windows:
1. Téléchargez PostgreSQL depuis https://www.postgresql.org/download/windows/
2. Installez avec les paramètres par défaut
3. Notez le mot de passe du superutilisateur `postgres`

### Sur Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

### Sur macOS:
```bash
brew install postgresql
brew services start postgresql
```

## 2. Création de la base de données

Connectez-vous à PostgreSQL:
```bash
# Windows (depuis le menu Démarrer > PostgreSQL > SQL Shell)
# Ou depuis PowerShell:
psql -U postgres

# Linux/macOS:
sudo -u postgres psql
```

Créez la base de données et l'utilisateur:
```sql
-- Créer la base de données
CREATE DATABASE guineegest_db;

-- Créer l'utilisateur
CREATE USER guineegest_user WITH PASSWORD 'votre_mot_de_passe_ici';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE guineegest_db TO guineegest_user;

-- Accorder les privilèges sur le schéma public (PostgreSQL 15+)
\c guineegest_db
GRANT ALL ON SCHEMA public TO guineegest_user;
GRANT CREATE ON SCHEMA public TO guineegest_user;

-- Quitter
\q
```

## 3. Configuration Django

1. Copiez le fichier `.env.local` vers `.env`:
```bash
copy .env.local .env
```

2. Modifiez le fichier `.env` avec vos paramètres:
```env
DJANGO_SECRET_KEY=votre-clé-secrète-de-50-caractères-aléatoires
DJANGO_DB_PASSWORD=votre_mot_de_passe_postgresql
```

## 4. Installation des dépendances

```bash
# Activez votre environnement virtuel
.venv\Scripts\activate

# Installez les dépendances
pip install -r requirements.txt
```

## 5. Migration de la base de données

```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

## 6. Test de la configuration

```bash
# Démarrer le serveur de développement
python manage.py runserver 8002
```

Visitez http://127.0.0.1:8002 pour vérifier que tout fonctionne.

## 7. Commandes utiles PostgreSQL

```bash
# Vérifier la connexion
python manage.py dbshell

# Sauvegarder la base de données
pg_dump -U guineegest_user -h localhost guineegest_db > backup.sql

# Restaurer la base de données
psql -U guineegest_user -h localhost guineegest_db < backup.sql
```

## Dépannage

### Erreur de connexion:
- Vérifiez que PostgreSQL est démarré
- Vérifiez les paramètres dans `.env`
- Vérifiez que l'utilisateur a les bonnes permissions

### Erreur de migration:
```bash
# Réinitialiser les migrations si nécessaire
python manage.py migrate --fake-initial
```
