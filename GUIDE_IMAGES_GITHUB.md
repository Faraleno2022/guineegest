# 🖼️ Guide Images GitHub - GuinéeGest

## 📋 Vue d'Ensemble

Ce guide explique comment les images sont gérées dans le projet GuinéeGest et comment elles s'affichent en ligne après déploiement sur GitHub.

---

## 📂 Structure des Images

### Répertoires
```
media/
├── images/
│   ├── Acces.jpg                    # Image originale hero
│   ├── Acces_optimized.jpg          # Version optimisée JPEG
│   ├── Acces_optimized.webp         # Version optimisée WebP
│   └── team/
│       ├── fara.png                 # Photo équipe - Fara
│       ├── ifono.jpg                # Photo équipe - Ifono
│       └── team-member-1.jpg        # Photo par défaut
└── profils/                         # ❌ Non suivi (gitignore)
    ├── entreprises/
    └── personnes/
```

### Images Suivies par Git
✅ **Incluses dans le repo** :
- `media/images/**` - Toutes les images du site
- `media/images/team/**` - Photos de l'équipe

❌ **Exclues du repo** :
- `media/profils/**` - Photos de profil utilisateurs (données sensibles)
- Autres fichiers media générés dynamiquement

---

## ⚙️ Configuration .gitignore

### Configuration Actuelle
```gitignore
# Django media (exclu par défaut)
media/*

# Mais on autorise les images du site
!media/.gitkeep
!media/images/
!media/images/**
```

### Explication
1. `media/*` - Ignore tout le dossier media
2. `!media/images/` - Exception : autorise le dossier images
3. `!media/images/**` - Exception : autorise tout le contenu de images

---

## 🚀 Déploiement avec Images

### Script PowerShell
**Fichier** : `deploy_github_with_images.ps1`

**Fonctionnalités** :
1. ✅ Vérifie les images présentes
2. ✅ Force l'ajout des images (git add -f)
3. ✅ Commit avec message détaillé
4. ✅ Push vers GitHub
5. ✅ Affiche les images incluses

### Commandes Manuelles
```bash
# 1. Forcer l'ajout des images
git add -f media/images/**/*.jpg
git add -f media/images/**/*.jpeg
git add -f media/images/**/*.png
git add -f media/images/**/*.webp

# 2. Ajouter le reste
git add .

# 3. Commit
git commit -m "Feature: Version 2.1.0 avec images"

# 4. Push
git push origin main
```

---

## 🌐 URLs des Images en Ligne

### Sur GitHub
```
https://github.com/votre-username/guineegest/blob/main/media/images/Acces_optimized.jpg
https://github.com/votre-username/guineegest/blob/main/media/images/team/fara.png
https://github.com/votre-username/guineegest/blob/main/media/images/team/ifono.jpg
```

### Sur PythonAnywhere
```
https://votre-domaine.pythonanywhere.com/media/images/Acces_optimized.jpg
https://votre-domaine.pythonanywhere.com/media/images/team/fara.png
https://votre-domaine.pythonanywhere.com/media/images/team/ifono.jpg
```

---

## 📝 Utilisation dans les Templates

### Page d'Accueil (home.html)
```django
<!-- Hero Image avec fallback WebP -->
<link rel="preload" href="{{ MEDIA_URL }}images/Acces_optimized.jpg" as="image" type="image/jpeg" fetchpriority="high">
<link rel="preload" href="{{ MEDIA_URL }}images/Acces_optimized.webp" as="image" type="image/webp">

<section class="hero-section">
    <div class="hero-content">
        <h1>Bienvenue dans Guinée-Ges</h1>
    </div>
</section>

<style>
.hero-section {
    background-image: url('{{ MEDIA_URL }}images/Acces_optimized.jpg');
    background-size: cover;
    background-position: center;
}
</style>
```

### Photos Équipe
```django
<!-- Fara -->
<img src="{{ MEDIA_URL }}images/team/fara.png" 
     alt="Fara" 
     class="img-fluid rounded-circle team-image" 
     style="width: 200px; height: 200px; object-fit: cover;">

<!-- Ifono -->
<img src="{{ MEDIA_URL }}images/team/ifono.jpg" 
     alt="Ifono" 
     class="img-fluid rounded-circle team-image" 
     style="width: 200px; height: 200px; object-fit: cover;">
```

---

## 🔧 Configuration Django

### settings.py
```python
# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### urls.py (développement)
```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ... vos URLs
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 📊 Optimisation des Images

### Images Actuelles

| Image | Taille | Format | Usage |
|-------|--------|--------|-------|
| `Acces.jpg` | ~2MB | JPEG | Original (non utilisé) |
| `Acces_optimized.jpg` | ~200KB | JPEG | Hero section |
| `Acces_optimized.webp` | ~150KB | WebP | Hero section (fallback) |
| `fara.png` | ~100KB | PNG | Photo équipe |
| `ifono.jpg` | ~80KB | JPEG | Photo équipe |

### Recommandations
1. ✅ Utiliser WebP pour les images modernes
2. ✅ Fournir fallback JPEG pour compatibilité
3. ✅ Optimiser les images avant upload
4. ✅ Utiliser lazy loading pour images non critiques

---

## 🚨 Dépannage

### Problème 1 : Images Non Affichées

**Symptôme** : Images cassées (icône 🖼️ brisée)

**Solutions** :
```bash
# 1. Vérifier que les images sont dans le repo
git ls-files media/images/

# 2. Vérifier les permissions
ls -la media/images/

# 3. Vérifier MEDIA_URL dans settings
python manage.py shell
>>> from django.conf import settings
>>> print(settings.MEDIA_URL)
>>> print(settings.MEDIA_ROOT)
```

### Problème 2 : Images Non Pushées

**Symptôme** : Images manquantes sur GitHub

**Solutions** :
```bash
# 1. Vérifier .gitignore
cat .gitignore | grep media

# 2. Forcer l'ajout
git add -f media/images/**/*

# 3. Vérifier le commit
git diff --cached --name-only | grep media

# 4. Push
git push origin main
```

### Problème 3 : Images Trop Lourdes

**Symptôme** : Chargement lent de la page

**Solutions** :
```bash
# Optimiser avec ImageMagick
convert Acces.jpg -quality 85 -resize 1920x1080 Acces_optimized.jpg

# Créer version WebP
cwebp -q 80 Acces_optimized.jpg -o Acces_optimized.webp

# Ou utiliser un service en ligne
# - TinyPNG.com
# - Squoosh.app
```

---

## 📱 Responsive Images

### Utilisation de srcset
```html
<img src="{{ MEDIA_URL }}images/Acces_optimized.jpg"
     srcset="{{ MEDIA_URL }}images/Acces_optimized.webp 1920w,
             {{ MEDIA_URL }}images/Acces_optimized.jpg 1920w"
     sizes="100vw"
     alt="Accueil GuinéeGest"
     loading="lazy">
```

### Picture Element
```html
<picture>
    <source srcset="{{ MEDIA_URL }}images/Acces_optimized.webp" type="image/webp">
    <source srcset="{{ MEDIA_URL }}images/Acces_optimized.jpg" type="image/jpeg">
    <img src="{{ MEDIA_URL }}images/Acces_optimized.jpg" alt="Accueil">
</picture>
```

---

## 🔒 Sécurité

### Images Publiques vs Privées

**✅ Images Publiques** (dans repo) :
- Logo entreprise
- Images hero/bannières
- Photos équipe (avec consentement)
- Icônes et illustrations

**❌ Images Privées** (hors repo) :
- Photos profil utilisateurs
- Documents scannés
- Factures/reçus
- Données sensibles

### Bonnes Pratiques
1. ✅ Ne jamais commiter de données personnelles
2. ✅ Obtenir consentement pour photos équipe
3. ✅ Utiliser .gitignore pour profils utilisateurs
4. ✅ Sauvegarder images privées séparément

---

## 📦 Déploiement PythonAnywhere

### Étapes
```bash
# 1. Se connecter à PythonAnywhere
ssh votre-username@ssh.pythonanywhere.com

# 2. Naviguer vers le projet
cd ~/guineegest

# 3. Pull les modifications (avec images)
git pull origin main

# 4. Vérifier les images
ls -la media/images/
ls -la media/images/team/

# 5. Reload l'application
# Via interface Web ou :
touch /var/www/votre_username_pythonanywhere_com_wsgi.py

# 6. Tester
curl https://votre-domaine.pythonanywhere.com/media/images/Acces_optimized.jpg -I
```

### Configuration Nginx (PythonAnywhere)
Les fichiers media sont servis automatiquement par PythonAnywhere via :
```
/media/ → ~/guineegest/media/
```

---

## ✅ Checklist Déploiement

### Avant le Push
- [ ] Images optimisées (< 500KB chacune)
- [ ] Formats multiples (JPEG + WebP)
- [ ] .gitignore configuré correctement
- [ ] Images ajoutées avec `git add -f`
- [ ] Commit créé avec message descriptif

### Après le Push
- [ ] Vérifier images sur GitHub
- [ ] Pull sur PythonAnywhere
- [ ] Vérifier URLs media en production
- [ ] Tester affichage sur site
- [ ] Vérifier responsive (mobile/desktop)

---

## 📞 Support

### Problèmes Courants
- Images non affichées → Vérifier MEDIA_URL et permissions
- Images trop lourdes → Optimiser avec outils
- Images non pushées → Utiliser `git add -f`

### Documentation
- Django Media Files : https://docs.djangoproject.com/en/5.0/howto/static-files/
- Git LFS (pour gros fichiers) : https://git-lfs.github.com/

---

**📅 Date** : 04 Octobre 2025  
**✅ Statut** : Images configurées et prêtes  
**🎯 Objectif** : Affichage correct en ligne
