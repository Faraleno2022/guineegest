# Installation des Dépendances sur PythonAnywhere

## Commandes à exécuter dans la console Bash de PythonAnywhere

```bash
# 1. Installer django-crispy-forms
pip3.10 install --user django-crispy-forms==2.4

# 2. Installer crispy-bootstrap5
pip3.10 install --user crispy-bootstrap5==2025.6

# 3. Installer toutes les autres dépendances depuis requirements.txt
pip3.10 install --user -r requirements.txt

# 4. Vérifier les installations
python3.10 -c "import crispy_forms; print('crispy_forms OK')"
python3.10 -c "import crispy_bootstrap5; print('crispy_bootstrap5 OK')"
python3.10 -c "import psycopg2; print('psycopg2 OK')"

# 5. Tester les migrations
python3.10 manage.py migrate

# 6. Créer un superuser (optionnel)
python3.10 manage.py createsuperuser

# 7. Collecter les fichiers statiques
python3.10 manage.py collectstatic --noinput
```

## Alternative : Installation par groupe

Si vous préférez installer par groupe :

```bash
# Dépendances Django de base
pip3.10 install --user Django==5.2.5 django-widget-tweaks==1.5.0

# Dépendances Bootstrap et formulaires
pip3.10 install --user django-crispy-forms==2.4 crispy-bootstrap5==2025.6 django-bootstrap5==25.2

# Dépendances utilitaires
pip3.10 install --user python-dotenv==1.1.1 pillow==11.3.0

# Dépendances PDF
pip3.10 install --user xhtml2pdf==0.2.10 reportlab==3.5.67

# Base de données
pip3.10 install --user psycopg2-binary==2.9.10

# SSL (si nécessaire)
pip3.10 install --user django-sslserver==0.22
```

## Vérification des modules installés

```bash
# Lister tous les packages installés
pip3.10 list --user

# Vérifier spécifiquement les modules Django
python3.10 -c "
import django
import crispy_forms
import crispy_bootstrap5
import psycopg2
print('Tous les modules sont installés correctement!')
"
```
