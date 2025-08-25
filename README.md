# GuinéeGest - Gestion de Parc Automobile (Django)

Application Django de gestion de parc auto (flotte), présence, paies et KPI.

## Prérequis
- Python 3.11+
- pip

## Installation
1. Cloner le dépôt
2. Créer un environnement virtuel et installer les dépendances
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

3. Configurer les variables d'environnement
- Copier `.env.example` en `.env` et adapter les valeurs
- Les paramètres sensibles sont chargés depuis `.env`

4. Initialiser la base
```bash
python manage.py migrate
python manage.py createsuperuser
```

5. Lancer le serveur
```bash
python manage.py runserver
```

## Variables d'environnement (.env)
- `DJANGO_SECRET_KEY` (obligatoire en production)
- `DJANGO_DEBUG` (True/False)
- `DJANGO_ALLOWED_HOSTS` (ex: 127.0.0.1,localhost)

## Notes
- Les fichiers sensibles (base SQLite, media, .env) sont exclus du dépôt via `.gitignore`
- Dépendances listées dans `requirements.txt`

## Stack
- Django 5
- django-crispy-forms + crispy-bootstrap5
- django-bootstrap5, widget-tweaks
- python-dotenv
