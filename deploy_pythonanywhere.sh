#!/bin/bash
# Script de déploiement automatique pour PythonAnywhere
# Date: 08 Octobre 2025

set -e  # Arrêter en cas d'erreur

echo "========================================="
echo "  DÉPLOIEMENT GUINEEGEST - PYTHONANYWHERE"
echo "========================================="
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables
PROJECT_DIR=~/guineegest
VENV_DIR=$PROJECT_DIR/.venv
WSGI_FILE=/var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py

echo "📁 Répertoire du projet: $PROJECT_DIR"
echo "🐍 Environnement virtuel: $VENV_DIR"
echo ""

# Étape 1: Aller dans le répertoire du projet
echo "1️⃣  Navigation vers le projet..."
cd $PROJECT_DIR || { echo -e "${RED}❌ Erreur: Impossible d'accéder au répertoire${NC}"; exit 1; }
echo -e "${GREEN}✅ OK${NC}"
echo ""

# Étape 2: Activer l'environnement virtuel
echo "2️⃣  Activation de l'environnement virtuel..."
source $VENV_DIR/bin/activate || { echo -e "${RED}❌ Erreur: Impossible d'activer le venv${NC}"; exit 1; }
echo -e "${GREEN}✅ OK${NC}"
echo ""

# Étape 3: Sauvegarder l'état actuel
echo "3️⃣  Sauvegarde de l'état actuel..."
python manage.py showmigrations fleet_app > migrations_avant_$(date +%Y%m%d_%H%M%S).txt
echo -e "${GREEN}✅ Sauvegarde créée${NC}"
echo ""

# Étape 4: Récupérer les dernières modifications
echo "4️⃣  Récupération des dernières modifications depuis GitHub..."
git fetch origin
git status
echo ""
echo -e "${YELLOW}⚠️  Voulez-vous continuer avec git pull? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    git pull origin main || { echo -e "${RED}❌ Erreur lors du git pull${NC}"; exit 1; }
    echo -e "${GREEN}✅ Code mis à jour${NC}"
else
    echo -e "${YELLOW}⏭️  Git pull ignoré${NC}"
fi
echo ""

# Étape 5: Installer/Mettre à jour les dépendances
echo "5️⃣  Installation des dépendances..."
pip install -r requirements.txt --quiet
echo -e "${GREEN}✅ Dépendances installées${NC}"
echo ""

# Étape 6: Vérifier les migrations
echo "6️⃣  Vérification des migrations..."
python manage.py showmigrations fleet_app | tail -10
echo ""

# Étape 7: Appliquer les migrations
echo "7️⃣  Application des migrations..."
echo -e "${YELLOW}⚠️  Migrations à appliquer:${NC}"
python manage.py showmigrations fleet_app | grep '\[ \]' || echo "Aucune migration en attente"
echo ""
echo -e "${YELLOW}⚠️  Appliquer les migrations? (y/n)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    python manage.py migrate fleet_app || { echo -e "${RED}❌ Erreur lors des migrations${NC}"; exit 1; }
    echo -e "${GREEN}✅ Migrations appliquées${NC}"
else
    echo -e "${YELLOW}⏭️  Migrations ignorées${NC}"
fi
echo ""

# Étape 8: Vérifier la structure de la base de données
echo "8️⃣  Vérification de la structure de la base de données..."
python manage.py shell << EOF
from fleet_app.models import Employe, Chauffeur
print("\n📊 Champs Employe:")
for f in Employe._meta.get_fields():
    print(f"  - {f.name}")
    
print("\n👤 Champs Chauffeur:")
for f in Chauffeur._meta.get_fields():
    print(f"  - {f.name}")

# Vérifier valeur_km
if hasattr(Employe, 'valeur_km'):
    print("\n✅ valeur_km existe dans Employe")
else:
    print("\n❌ valeur_km n'existe PAS dans Employe")
EOF
echo ""

# Étape 9: Collecter les fichiers statiques
echo "9️⃣  Collecte des fichiers statiques..."
python manage.py collectstatic --noinput || { echo -e "${RED}❌ Erreur lors de collectstatic${NC}"; exit 1; }
echo -e "${GREEN}✅ Fichiers statiques collectés${NC}"
echo ""

# Étape 10: Vérifier le système
echo "🔟 Vérification du système..."
python manage.py check --deploy
echo -e "${GREEN}✅ Vérifications OK${NC}"
echo ""

# Étape 11: Redémarrer l'application
echo "1️⃣1️⃣  Redémarrage de l'application web..."
touch $WSGI_FILE || { echo -e "${RED}❌ Erreur lors du redémarrage${NC}"; exit 1; }
echo -e "${GREEN}✅ Application redémarrée${NC}"
echo ""

# Étape 12: Vérifications post-déploiement
echo "1️⃣2️⃣  Vérifications post-déploiement..."
echo ""
echo "📋 Migrations appliquées:"
python manage.py showmigrations fleet_app | grep '\[X\]' | tail -5
echo ""

# Résumé
echo "========================================="
echo "  ✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS"
echo "========================================="
echo ""
echo "🔍 Prochaines étapes:"
echo "  1. Vérifier les logs: tail -f /var/log/gestionnairedeparc.pythonanywhere.com.error.log"
echo "  2. Tester l'application: https://www.guineegest.space"
echo "  3. Tester les modules corrigés:"
echo "     - /chauffeurs/ajouter/"
echo "     - /heures-supplementaires/"
echo "     - /paies-legacy/"
echo ""
echo "📝 Fichiers de sauvegarde créés dans: $PROJECT_DIR"
echo ""
