# Déploiement PythonAnywhere (branche `dev`)

Ce document décrit les étapes pour déployer la branche `dev` de `guineegest` sur PythonAnywhere.

## Prérequis

- Dépôt cloné dans `~/guineegest`
- Virtualenv présent dans `~/guineegest/.venv`
- Variables d'environnement configurées dans l'onglet Web > Environment:
  - `DJANGO_SECRET_KEY` = (chaîne aléatoire 50+)
  - `DJANGO_ALLOWED_HOSTS` = `gestionnairedeparc.pythonanywhere.com`
  - `DJANGO_SETTINGS_MODULE` = `fleet_management.settings_prod`

## Déploiement rapide via script

Sur la console Bash PythonAnywhere, exécutez:

```bash
cd ~/guineegest
bash deploy_dev.sh            # déploiement standard
# ou
bash deploy_dev.sh --install  # si vous voulez réinstaller les dépendances
```

Le script:
- fait `git fetch` + `git pull --rebase` sur `dev`
- active le virtualenv `~/.venv`
- exécute `migrate` et `collectstatic` avec `settings_prod`

À la fin:
- Allez dans l'onglet Web, cliquez sur **Reload**.

## Déploiement manuel (pas à pas)

```bash
cd ~/guineegest
git fetch --all
git checkout dev
git pull --rebase origin dev

source .venv/bin/activate

# Facultatif si requirements ont changé
pip install --upgrade pip wheel
pip install -r requirements.txt

python manage.py migrate --settings=fleet_management.settings_prod
python manage.py collectstatic --noinput --settings=fleet_management.settings_prod
```

Puis rechargez l'app dans l'onglet Web.

## Dépannage

- Si vous voyez une erreur de settings/secret key: vérifiez les variables d'environnement dans l'onglet Web.
- Si des statiques ne s'affichent pas: relancez `collectstatic` et vérifiez le mapping des statiques dans l'onglet Web (`/static/` vers `~/guineegest/staticfiles`).
- Si le virtualenv ne s'active pas: vérifiez le chemin `~/guineegest/.venv` et la configuration Web `Virtualenv`.
