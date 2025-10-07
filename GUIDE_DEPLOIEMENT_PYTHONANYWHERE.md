# 🚀 Guide de Déploiement PythonAnywhere

## 📅 Date : 07 Octobre 2025

---

## 🎯 Objectif

Déployer les dernières corrections et améliorations sur PythonAnywhere :
- ✅ Corrections assignation utilisateur (12 modules)
- ✅ Navigation entre les mois (3 modules)
- ✅ Module Bonus/Km complet
- ✅ Migrations corrigées

---

## 📋 Étapes de Déploiement

### 1️⃣ Connexion à PythonAnywhere

```bash
# Se connecter via SSH ou console Bash
ssh gestionnairedeparc@ssh.pythonanywhere.com
```

---

### 2️⃣ Aller dans le Répertoire du Projet

```bash
cd ~/guineegest
source .venv/bin/activate
```

---

### 3️⃣ Sauvegarder l'État Actuel (Optionnel mais Recommandé)

```bash
# Sauvegarder la base de données
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Ou sauvegarder juste les migrations
python manage.py showmigrations fleet_app > migrations_avant.txt
```

---

### 4️⃣ Récupérer les Dernières Modifications

```bash
git pull origin main
```

**Sortie attendue** :
```
Updating 4b93168..c8353e5
Fast-forward
 fleet_app/migrations/0018_placeholder.py | 14 ++++++++++++++
 fleet_app/migrations/0019_add_frais_km_to_paie.py | 2 +-
 fleet_app/migrations/0020_add_frais_kilometrique.py | 39 +++++++++++++++++++++++++++++++++++++++
 fleet_app/views.py | 28 +++++++++++++++++++--------
 fleet_app/views_facturation.py | 3 ++-
 ...
```

---

### 5️⃣ Installer les Dépendances

```bash
pip install -r requirements.txt
```

**Nouvelle dépendance** : `python-dateutil` (pour navigation mois)

---

### 6️⃣ Vérifier les Migrations Actuelles

```bash
python check_migrations.py
```

**Ou** :
```bash
python manage.py showmigrations fleet_app
```

**Identifier la dernière migration appliquée** (exemple) :
```
[X] 0016_backfill_inventaire_entreprise
[ ] 0017_vehicule_fournisseur
[ ] 0018_placeholder
[ ] 0019_add_frais_km_to_paie
[ ] 0020_add_frais_kilometrique
```

---

### 7️⃣ Appliquer les Migrations

#### Cas 1 : Si 0017 n'existe pas (probable)

```bash
# Fake 0017 si elle n'existe pas mais que le champ existe
python manage.py migrate fleet_app 0017 --fake

# Appliquer 0018 (vide, juste pour la séquence)
python manage.py migrate fleet_app 0018

# Appliquer 0019 (ajout champ montant_frais_kilometriques)
python manage.py migrate fleet_app 0019

# Appliquer 0020 (création modèle FraisKilometrique)
python manage.py migrate fleet_app 0020
```

#### Cas 2 : Si 0017 existe déjà

```bash
# Appliquer toutes les migrations d'un coup
python manage.py migrate fleet_app
```

#### Cas 3 : Si erreur "table already exists"

```bash
# Fake la migration problématique
python manage.py migrate fleet_app 0020 --fake
```

---

### 8️⃣ Vérifier que Tout est OK

```bash
# Vérifier les migrations
python manage.py showmigrations fleet_app | grep '\[X\]' | tail -5

# Vérifier qu'il n'y a pas d'erreurs
python manage.py check

# Tester la connexion à la base de données
python manage.py shell -c "from fleet_app.models_entreprise import FraisKilometrique; print(FraisKilometrique.objects.count())"
```

---

### 9️⃣ Collecter les Fichiers Statiques

```bash
python manage.py collectstatic --noinput
```

---

### 🔟 Redémarrer l'Application Web

```bash
# Toucher le fichier WSGI pour redémarrer
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

**Ou via l'interface Web** :
1. Aller sur https://www.pythonanywhere.com/user/gestionnairedeparc/webapps/
2. Cliquer sur **"Reload gestionnairedeparc.pythonanywhere.com"**

---

## ✅ Vérifications Post-Déploiement

### 1. Tester les Modules Corrigés

#### Chauffeurs
```
URL: https://www.guineegest.space/chauffeurs/
Action: Ajouter un chauffeur
Vérification: Le chauffeur apparaît dans la liste
```

#### KPI Distance
```
URL: https://www.guineegest.space/kpi-distance/
Action: Ajouter une distance
Vérification: La distance apparaît dans le tableau
```

#### KPI Consommation
```
URL: https://www.guineegest.space/kpi-consommation/
Action: Ajouter une consommation
Vérification: La consommation apparaît dans le tableau
```

#### Bonus/Km
```
URL: https://www.guineegest.space/frais-kilometriques/
Action: Ajouter des frais km
Vérification: Les frais apparaissent dans le tableau
Test Navigation: Cliquer sur "Mois Suivant" et "Mois Précédent"
```

---

### 2. Vérifier les Logs

```bash
# Voir les logs d'erreur
tail -f /var/log/gestionnairedeparc.pythonanywhere.com.error.log

# Voir les logs d'accès
tail -f /var/log/gestionnairedeparc.pythonanywhere.com.access.log
```

---

## 🐛 Résolution de Problèmes

### Problème 1 : Migration déjà appliquée

**Erreur** :
```
django.db.utils.OperationalError: table "FraisKilometriques" already exists
```

**Solution** :
```bash
python manage.py migrate fleet_app 0020 --fake
```

---

### Problème 2 : Migration parent manquante

**Erreur** :
```
NodeNotFoundError: Migration fleet_app.0019_add_frais_km_to_paie 
dependencies reference nonexistent parent node
```

**Solution** :
```bash
# Identifier la dernière migration existante
python manage.py showmigrations fleet_app | grep '\[X\]' | tail -1

# Fake les migrations intermédiaires
python manage.py migrate fleet_app 0017 --fake
python manage.py migrate fleet_app 0018 --fake
python manage.py migrate fleet_app 0019
python manage.py migrate fleet_app 0020
```

---

### Problème 3 : Module python-dateutil manquant

**Erreur** :
```
ModuleNotFoundError: No module named 'dateutil'
```

**Solution** :
```bash
pip install python-dateutil
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

---

### Problème 4 : Erreur 500 après déploiement

**Actions** :
```bash
# Vérifier les logs
tail -50 /var/log/gestionnairedeparc.pythonanywhere.com.error.log

# Vérifier la configuration
python manage.py check --deploy

# Redémarrer l'application
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

---

## 📊 Résumé des Changements Déployés

### Commits Déployés
1. **a73d537** - Corrections KPIs, Chauffeurs, Feuilles de route
2. **c166082** - Corrections vues dupliquées KPIs et Facturation
3. **5e3a0f3** - Navigation mois pour Heures Supplémentaires et Paies
4. **4b93168** - Réorganisation migrations
5. **c8353e5** - Ajout migration 0018_placeholder

### Modules Corrigés (12)
- ✅ Chauffeurs
- ✅ KPI Distance (2 vues)
- ✅ KPI Consommation (2 vues)
- ✅ KPI Disponibilité (2 vues)
- ✅ KPI Utilisation
- ✅ KPI Incidents
- ✅ Feuilles de Route (2 vues)
- ✅ Facturation

### Nouvelles Fonctionnalités
- ✅ Module Bonus/Km complet
- ✅ Navigation mois (Heures Sup, Paies, Bonus/Km)
- ✅ Export CSV Bonus/Km
- ✅ Intégration Bonus/Km avec Paie

---

## 🔒 Sécurité

Toutes les données sont maintenant correctement isolées par utilisateur :
- Chaque objet créé a un propriétaire (`user`)
- Les utilisateurs ne voient que leurs propres données
- Pas de fuite de données entre utilisateurs

---

## 📞 Support

### Documentation
- `CORRECTIONS_COMPLETES_SYSTEME.md` - Résumé des corrections
- `FIX_MIGRATION_PYTHONANYWHERE.md` - Guide migrations
- `AMELIORATIONS_BONUS_KM.md` - Module Bonus/Km

### Scripts Utilitaires
- `check_migrations.py` - Vérifier migrations appliquées
- `fix_migrations_django.py` - Corriger historique migrations

---

## ✅ Checklist de Déploiement

- [ ] Connexion à PythonAnywhere
- [ ] `cd ~/guineegest && source .venv/bin/activate`
- [ ] Sauvegarde base de données (optionnel)
- [ ] `git pull origin main`
- [ ] `pip install -r requirements.txt`
- [ ] Vérifier migrations actuelles
- [ ] Appliquer migrations
- [ ] `python manage.py check`
- [ ] `python manage.py collectstatic --noinput`
- [ ] Redémarrer application web
- [ ] Tester les modules corrigés
- [ ] Vérifier les logs

---

**Date** : 07 Octobre 2025  
**Version** : 2.0.0  
**Statut** : ✅ Prêt pour déploiement
