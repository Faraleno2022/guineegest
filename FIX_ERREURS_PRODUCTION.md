# 🔧 Correction Erreurs Production

## 📅 Date : 07 Octobre 2025

---

## 🐛 Problèmes Identifiés

### 1. ❌ Fichier Manquant : `export-utils.js`
```
Not Found: /static/fleet_app/js/export-utils.js
```

### 2. ❌ Colonne Manquante : `Employes.valeur_km`
```
MySQLdb.OperationalError: (1054, "Unknown column 'Employes.valeur_km' in 'field list'")
```

### 3. ❌ Champs Chauffeur Inexistants
```
FieldError: Unknown field(s) (date_naissance, photo, date_validite_permis, adresse) specified for Chauffeur
```

---

## ✅ Solutions

### Solution 1 : Créer `export-utils.js`

Le fichier est référencé mais n'existe pas. Créons-le.

**Fichier** : `fleet_app/static/fleet_app/js/export-utils.js`

```javascript
// Utilitaires d'export pour GuineeGest
console.log('Export utilities loaded');

// Fonction d'export CSV (si nécessaire)
function exportToCSV(tableId, filename) {
    // Implémentation à venir
    console.log('Export CSV:', filename);
}

// Fonction d'export PDF (si nécessaire)
function exportToPDF(elementId, filename) {
    // Implémentation à venir
    console.log('Export PDF:', filename);
}
```

---

### Solution 2 : Appliquer Migration `valeur_km`

La migration 0020 n'a pas été appliquée sur le serveur.

**Commandes sur PythonAnywhere** :

```bash
cd ~/guineegest
source .venv/bin/activate

# Vérifier les migrations
python manage.py showmigrations fleet_app

# Appliquer la migration 0020
python manage.py migrate fleet_app 0020

# Redémarrer
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

---

### Solution 3 : Corriger Vue Chauffeur

Le modèle `Chauffeur` sur le serveur n'a pas les mêmes champs que localement.

**Fichier à modifier** : `fleet_app/views.py`

**Avant** (ligne 1086) :
```python
class ChauffeurCreateView(LoginRequiredMixin, CreateView):
    model = Chauffeur
    template_name = 'fleet_app/chauffeur_form.html'
    fields = ['nom', 'prenom', 'date_naissance', 'numero_permis', 'date_validite_permis', 'telephone', 'email', 'adresse', 'photo']
    success_url = reverse_lazy('fleet_app:chauffeur_list')
```

**Après** :
```python
class ChauffeurCreateView(LoginRequiredMixin, CreateView):
    model = Chauffeur
    template_name = 'fleet_app/chauffeur_form.html'
    fields = ['nom', 'prenom', 'numero_permis', 'telephone', 'email']  # Champs existants uniquement
    success_url = reverse_lazy('fleet_app:chauffeur_list')
```

**Même correction pour** `ChauffeurUpdateView` (ligne 1096).

---

## 🔍 Diagnostic Complet

### Étape 1 : Vérifier Structure Base de Données

**Sur PythonAnywhere** :

```bash
cd ~/guineegest
source .venv/bin/activate

python manage.py shell
```

```python
from fleet_app.models import Chauffeur, Employe

# Vérifier champs Chauffeur
print("Champs Chauffeur:")
for field in Chauffeur._meta.get_fields():
    print(f"  - {field.name}")

# Vérifier champs Employe
print("\nChamps Employe:")
for field in Employe._meta.get_fields():
    print(f"  - {field.name}")
    
# Vérifier si valeur_km existe
if hasattr(Employe, 'valeur_km'):
    print("\n✅ valeur_km existe")
else:
    print("\n❌ valeur_km n'existe pas")
```

---

### Étape 2 : Vérifier Migrations Appliquées

```bash
python manage.py showmigrations fleet_app | tail -10
```

**Vérifier que ces migrations sont appliquées** :
- `[X] 0018_placeholder`
- `[X] 0019_add_frais_km_to_paie`
- `[X] 0020_add_frais_kilometrique`

---

## 📝 Script de Correction Automatique

**Fichier** : `fix_production_errors.sh`

```bash
#!/bin/bash
# Script de correction des erreurs production

cd ~/guineegest
source .venv/bin/activate

echo "=== Correction des erreurs production ==="

# 1. Créer export-utils.js si manquant
echo "\n1. Création export-utils.js..."
mkdir -p fleet_app/static/fleet_app/js
cat > fleet_app/static/fleet_app/js/export-utils.js << 'EOF'
// Utilitaires d'export pour GuineeGest
console.log('Export utilities loaded');
EOF

# 2. Appliquer migrations
echo "\n2. Application des migrations..."
python manage.py migrate fleet_app

# 3. Collecter fichiers statiques
echo "\n3. Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

# 4. Vérifier structure base de données
echo "\n4. Vérification base de données..."
python manage.py shell -c "
from fleet_app.models import Employe
print('Champs Employe:')
for f in Employe._meta.get_fields():
    print(f'  - {f.name}')
"

# 5. Redémarrer application
echo "\n5. Redémarrage application..."
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py

echo "\n✅ Corrections appliquées!"
```

**Rendre exécutable et lancer** :
```bash
chmod +x fix_production_errors.sh
./fix_production_errors.sh
```

---

## 🚀 Corrections Immédiates

### Sur Votre Machine Locale

1. **Créer `export-utils.js`** :

```bash
mkdir -p fleet_app/static/fleet_app/js
```

2. **Corriger les vues Chauffeur** :

Modifier `fleet_app/views.py` lignes 1086 et 1096.

3. **Commiter et pousser** :

```bash
git add -A
git commit -m "Fix: Corrections erreurs production - export-utils.js et champs Chauffeur"
git push origin main
```

---

### Sur PythonAnywhere

```bash
cd ~/guineegest
source .venv/bin/activate

# Récupérer les corrections
git pull origin main

# Appliquer migrations
python manage.py migrate fleet_app

# Collecter statiques
python manage.py collectstatic --noinput

# Redémarrer
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

---

## 🔒 Sécurité : Tentatives d'Intrusion Détectées

**Dans les logs** :
```
2025-10-06 16:38:37,637: Not Found: /.env
2025-10-06 16:38:37,725: Not Found: /api/.env
2025-10-06 16:38:39,135: Not Found: /phpinfo.php
```

**Actions** :
- ✅ Fichiers sensibles protégés par `.gitignore`
- ✅ Pas d'exposition de `.env`
- ✅ Pas de fichiers PHP exposés

**Recommandation** : Installer Fail2Ban ou CloudFlare pour bloquer ces IPs.

---

## ✅ Checklist de Correction

### Local
- [ ] Créer `export-utils.js`
- [ ] Corriger `ChauffeurCreateView`
- [ ] Corriger `ChauffeurUpdateView`
- [ ] Commiter et pousser

### PythonAnywhere
- [ ] `git pull origin main`
- [ ] Vérifier migrations : `python manage.py showmigrations fleet_app`
- [ ] Appliquer migrations : `python manage.py migrate fleet_app`
- [ ] Collecter statiques : `python manage.py collectstatic --noinput`
- [ ] Redémarrer : `touch /var/www/...wsgi.py`
- [ ] Tester : Accéder à `/chauffeurs/ajouter/`
- [ ] Vérifier logs : `tail -f /var/log/...error.log`

---

**Date** : 07 Octobre 2025  
**Priorité** : 🔴 **CRITIQUE**  
**Statut** : ⏳ **À CORRIGER IMMÉDIATEMENT**
