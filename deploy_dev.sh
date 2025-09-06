#!/usr/bin/env bash
# Déploiement rapide de la branche dev sur PythonAnywhere
# Usage:
#   bash deploy_dev.sh            # déploiement standard
#   bash deploy_dev.sh --install  # déploiement + installation des dépendances

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$HOME/guineegest}"
VENV_DIR="${VENV_DIR:-$PROJECT_DIR/.venv}"
DJ_SETTINGS="${DJ_SETTINGS:-fleet_management.settings_prod}"

echo "[Deploy] Projet: $PROJECT_DIR"
cd "$PROJECT_DIR"

echo "[Deploy] Fetch & Pull (dev)"
git fetch --all
# S'assure d'être sur dev sans interrompre les sessions PA existantes
if [ "$(git rev-parse --abbrev-ref HEAD)" != "dev" ]; then
  git checkout dev
fi
git pull --rebase origin dev

if [ -d "$VENV_DIR" ]; then
  echo "[Deploy] Activation du virtualenv"
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
else
  echo "[Deploy] AVERTISSEMENT: Virtualenv introuvable à $VENV_DIR"
fi

if [ "${1:-}" = "--install" ]; then
  echo "[Deploy] Installation des dépendances"
  pip install --upgrade pip wheel
  pip install -r requirements.txt
fi

echo "[Deploy] Migrations (settings=$DJ_SETTINGS)"
python manage.py migrate --settings="$DJ_SETTINGS"

echo "[Deploy] Collectstatic"
python manage.py collectstatic --noinput --settings="$DJ_SETTINGS"

cat <<'EOF'
[Deploy] Terminé.
- Ouvrez le tableau de bord PythonAnywhere > Web > cliquez sur Reload.
- URL: https://gestionnairedeparc.pythonanywhere.com/

Astuce:
Vous pouvez définir des variables d'environnement avant l'exécution:
  export PROJECT_DIR=$HOME/guineegest
  export VENV_DIR=$HOME/guineegest/.venv
  export DJ_SETTINGS=fleet_management.settings_prod
EOF
