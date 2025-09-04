from pathlib import Path
import os
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env if present
load_dotenv(BASE_DIR / '.env')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'insecure-dev-key-change-me')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True').lower() == 'true'

# Allowed hosts - Allow all hosts for development
ALLOWED_HOSTS = ['*']

# Application definition
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
]

# Add SSL server for development HTTPS
# DISABLED FOR DEVELOPMENT - Remove sslserver to avoid HTTPS confusion
# if DEBUG:
#     INSTALLED_APPS.append('sslserver')

MIDDLEWARE = [
    # 'django.middleware.security.SecurityMiddleware',  # DISABLED - Security protection
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',  # ENABLED - Required for form submissions
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',  # DISABLED - Clickjacking protection
    'fleet_app.middleware.synchronisation_middleware.SynchronisationMiddleware',
]

ROOT_URLCONF = 'fleet_management.urls'

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
                'fleet_app.middleware.synchronisation_middleware.synchronisation_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'fleet_management.wsgi.application'

# Database (PostgreSQL via env vars, fallback to SQLite)
_db_engine = os.getenv('DJANGO_DB_ENGINE', 'django.db.backends.sqlite3')
_db_name = os.getenv('DJANGO_DB_NAME', str(BASE_DIR / 'django_fleet.db'))
_db_user = os.getenv('DJANGO_DB_USER', '')
_db_password = os.getenv('DJANGO_DB_PASSWORD', '')
_db_host = os.getenv('DJANGO_DB_HOST', '')
_db_port = os.getenv('DJANGO_DB_PORT', '')

DATABASES = {
    'default': {
        'ENGINE': _db_engine,
        'NAME': _db_name,
        'USER': _db_user,
        'PASSWORD': _db_password,
        'HOST': _db_host,
        'PORT': _db_port,
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# Crispy Forms settings
CRISPY_ALLOWED_TEMPLATE_PACKS = 'bootstrap5'
CRISPY_TEMPLATE_PACK = 'bootstrap5'
CRISPY_BOOTSTRAP5_TEMPLATE_PACK = 'bootstrap5'

# Force HTTP in development - CSRF settings for forms
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = None
