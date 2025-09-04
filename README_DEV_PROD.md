# Dev vs Prod Guide

This document explains how to run the project in development and production securely.

## Development
- Settings module: `fleet_management.settings`
- DEBUG: Enabled by default (via `.env`)
- Security middlewares: relaxed for ease of development

Run locally:
```bash
set DJANGO_SETTINGS_MODULE=fleet_management.settings
python manage.py runserver
```

## Production
- Settings module: `fleet_management.settings_prod`
- DEBUG: Disabled
- Security middlewares: enabled (SecurityMiddleware, CSRF, XFrame, HTTPS redirect, HSTS)

Environment variables (set in hosting panel or shell):
- `DJANGO_SECRET_KEY` (required)
- `DJANGO_ALLOWED_HOSTS` (e.g. gestionnairedeparc.pythonanywhere.com,.pythonanywhere.com)
- `DJANGO_DB_ENGINE`, `DJANGO_DB_NAME`, `DJANGO_DB_USER`, `DJANGO_DB_PASSWORD`, `DJANGO_DB_HOST`, `DJANGO_DB_PORT` (if using PostgreSQL)

Example (Windows CMD / PowerShell):
```bash
set DJANGO_SETTINGS_MODULE=fleet_management.settings_prod
python manage.py migrate
python manage.py collectstatic --noinput
```

## Notes
- `.env` should not be committed. Use `.env` only for local development.
- `fleet_management/settings_prod.py` imports base settings and overrides only production-specific options.
