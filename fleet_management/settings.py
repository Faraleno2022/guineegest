from pathlib import Path
import os
from dotenv import load_dotenv

# =====================================
# Chemins de base
# =====================================
BASE_DIR = Path(__file__).resolve().parent.parent

# Charger les variables d'environnement depuis .env si présent
load_dotenv(BASE_DIR / '.env')

# =====================================
# Clé secrète et Debug
# =====================================
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'insecure-dev-key-change-me')
DEBUG = os.getenv('DJANGO_DEBUG', 'False').lower() == 'true'

# =====================================
# ALLOWED_HOSTS
# =====================================
ALLOWED_HOSTS = os.getenv(
    'DJANGO_ALLOWED_HOSTS', 
    'gestionnairedeparc.pythonanywhere.com,localhost,127.0.0.1'
).split(',')

# =====================================
# Applications installées
# =====================================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'fleet_app',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_bootstrap5',
    'widget_tweaks',
    'sslserver',
]

# =====================================
# Middleware
# =====================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fleet_management.urls'

# =====================================
# Templates
# =====================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'fleet_app.context_processors.alerts_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'fleet_management.wsgi.application'

# =====================================
# Base de données
# =====================================
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.getenv('DJANGO_DB_NAME', str(BASE_DIR / 'django_fleet.db')),
        'USER': os.getenv('DJANGO_DB_USER', ''),
        'PASSWORD': os.getenv('DJANGO_DB_PASSWORD', ''),
        'HOST': os.getenv('DJANGO_DB_HOST', ''),
        'PORT': os.getenv('DJANGO_DB_PORT', ''),
    }
}

# =====================================
# Validation des mots de passe
# =====================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# =====================================
# Internationalisation
# =====================================
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True

# =====================================
# Fichiers statiques et médias
# =====================================
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# =====================================
# Clé primaire par défaut
# =====================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# =====================================
# Authentification
# =====================================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# =====================================
# Crispy Forms
# =====================================
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_BOOTSTRAP5_TEMPLATE_PACK = 'bootstrap5'

# =====================================
# Sécurité HTTPS
# =====================================
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
else:
    SECURE_SSL_REDIRECT = False
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
