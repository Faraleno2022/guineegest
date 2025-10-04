# 🔧 Correction Images sur PythonAnywhere

## 🎯 Problème
Les images ne s'affichent pas sur PythonAnywhere alors qu'elles sont dans le repo GitHub.

## ✅ Solution

### Étape 1 : Connexion SSH
```bash
ssh gestionnairedeparc@ssh.pythonanywhere.com
```

### Étape 2 : Naviguer vers le projet
```bash
cd ~/guineegest
```

### Étape 3 : Vérifier l'état actuel
```bash
# Voir la branche actuelle
git branch

# Voir les derniers commits
git log --oneline -3

# Vérifier si les images sont présentes
ls -la media/images/
ls -la media/images/team/
```

### Étape 4 : Pull avec force
```bash
# Fetch toutes les modifications
git fetch origin

# Reset hard sur origin/main
git reset --hard origin/main

# Ou pull avec force
git pull origin main --force
```

### Étape 5 : Vérifier les images après pull
```bash
# Lister les images
ls -la media/images/
ls -la media/images/team/

# Vérifier les fichiers
file media/images/Acces_optimized.jpg
file media/images/team/fara.png
```

### Étape 6 : Vérifier les permissions
```bash
# Donner les bonnes permissions
chmod 755 media/
chmod 755 media/images/
chmod 755 media/images/team/
chmod 644 media/images/*.jpg
chmod 644 media/images/*.webp
chmod 644 media/images/team/*.png
chmod 644 media/images/team/*.jpg
```

### Étape 7 : Vérifier la configuration Django
```bash
# Ouvrir la console Python
python manage.py shell

# Dans la console Python
>>> from django.conf import settings
>>> print(settings.MEDIA_URL)
# Devrait afficher: /media/
>>> print(settings.MEDIA_ROOT)
# Devrait afficher: /home/gestionnairedeparc/guineegest/media
>>> exit()
```

### Étape 8 : Reload l'application
```bash
# Via la console
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py

# Ou via l'interface Web
# Web → Reload
```

### Étape 9 : Tester les URLs
```bash
# Tester l'accès aux images
curl -I https://gestionnairedeparc.pythonanywhere.com/media/images/Acces_optimized.jpg
curl -I https://gestionnairedeparc.pythonanywhere.com/media/images/team/fara.png
```

**Résultat attendu** : `HTTP/1.1 200 OK`

---

## 🔍 Diagnostic Avancé

### Si les images ne sont toujours pas là après pull

```bash
# Vérifier le .gitignore
cat .gitignore | grep media

# Devrait afficher:
# media/*
# !media/images/
# !media/images/**

# Vérifier les fichiers trackés par Git
git ls-tree -r HEAD --name-only | grep media

# Devrait lister toutes les images
```

### Si Git ne voit pas les images

```bash
# Forcer le checkout des images
git checkout HEAD -- media/images/

# Ou cloner à nouveau
cd ~
mv guineegest guineegest_backup
git clone https://github.com/Faraleno2022/guineegest.git
cd guineegest
ls -la media/images/
```

---

## 📝 Configuration PythonAnywhere Web

### Vérifier Static Files Mapping
Dans l'interface Web de PythonAnywhere :

**Web → Static files**

Ajouter si absent :
```
URL: /media/
Directory: /home/gestionnairedeparc/guineegest/media/
```

---

## 🧪 Tests

### Test 1 : Fichiers présents
```bash
cd ~/guineegest
test -f media/images/Acces_optimized.jpg && echo "✅ OK" || echo "❌ MANQUANT"
test -f media/images/team/fara.png && echo "✅ OK" || echo "❌ MANQUANT"
```

### Test 2 : Permissions
```bash
ls -l media/images/Acces_optimized.jpg
# Devrait afficher: -rw-r--r--
```

### Test 3 : Accès Web
```bash
curl -I https://gestionnairedeparc.pythonanywhere.com/media/images/Acces_optimized.jpg
```

---

## 🚨 Si Rien ne Fonctionne

### Solution de Dernier Recours : Upload Manuel

```bash
# Sur votre machine locale
cd C:\Users\faral\Desktop\Gestion_parck

# Créer une archive
tar -czf images.tar.gz media/images/

# Upload via SCP
scp images.tar.gz gestionnairedeparc@ssh.pythonanywhere.com:~/

# Sur PythonAnywhere
cd ~/guineegest
tar -xzf ~/images.tar.gz
rm ~/images.tar.gz
```

---

## ✅ Vérification Finale

### Checklist
- [ ] `git log` montre le commit avec les images
- [ ] `ls media/images/` liste les 3 fichiers
- [ ] `ls media/images/team/` liste les 3 fichiers
- [ ] Permissions correctes (755 pour dossiers, 644 pour fichiers)
- [ ] Static files mapping configuré
- [ ] Application reloadée
- [ ] URLs images accessibles (HTTP 200)
- [ ] Images s'affichent sur le site

---

## 📞 Support

Si le problème persiste après toutes ces étapes :

1. Vérifier les logs d'erreur :
   ```bash
   tail -f /var/log/gestionnairedeparc.pythonanywhere.com.error.log
   ```

2. Vérifier les logs d'accès :
   ```bash
   tail -f /var/log/gestionnairedeparc.pythonanywhere.com.access.log
   ```

3. Contacter le support PythonAnywhere

---

**📅 Date** : 04 Octobre 2025  
**🎯 Objectif** : Images visibles sur PythonAnywhere  
**✅ Statut** : Instructions prêtes
