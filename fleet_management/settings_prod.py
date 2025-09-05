from pathlib import Path
import os
from .settings import *  # Import base settings (development defaults)

# Production overrides
DEBUG = False

# Secret key must come from environment in production
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("DJANGO_SECRET_KEY must be set in production")

# Allowed hosts: comma-separated list in DJANGO_ALLOWED_HOSTS
# Example: DJANGO_ALLOWED_HOSTS="gestionnairedeparc.pythonanywhere.com,.pythonanywhere.com"
_allowed = os.getenv('DJANGO_ALLOWED_HOSTS', '').strip()
if _allowed:
    ALLOWED_HOSTS = [h.strip() for h in _allowed.split(',') if h.strip()]
else:
    # Sensible default if not provided (adjust as needed)
    ALLOWED_HOSTS = [
        'gestionnairedeparc.pythonanywhere.com',
        '.pythonanywhere.com',
    ]

# Re-enable security middleware stack for production
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'fleet_app.middleware.synchronisation_middleware.SynchronisationMiddleware',
]

# Security hardening
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_USE_SESSIONS = False
CSRF_COOKIE_SAMESITE = 'Lax'

SECURE_HSTS_SECONDS = int(os.getenv('DJANGO_SECURE_HSTS_SECONDS', '31536000'))  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Internationalization (keep same as base or override if needed)
# LANGUAGE_CODE, TIME_ZONE come from base settings

# Static/Media: reuse base configuration
# DATABASES: inherited from base settings which already reads env vars

# WSGI/ASGI application remains the same as base
