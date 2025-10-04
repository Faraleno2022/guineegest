# 🚨 ACTIONS DE SÉCURITÉ URGENTES

## ⚠️ PROBLÈME CRITIQUE IDENTIFIÉ

La page `/accueil/` affiche **TOUTES les données de TOUTES les entreprises** sans filtrage !

**Impact** : Violation de confidentialité, fuite de données, non-conformité RGPD

---

## ✅ SOLUTION IMMÉDIATE (30 minutes)

### Étape 1 : Modifier le Modèle (5 min)

**Fichier** : `fleet_app/models.py`

Ajouter dans la classe `FournisseurVehicule` :

```python
class FournisseurVehicule(models.Model):
    # ... champs existants ...
    
    code_acces = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Code d'accès unique pour la page publique"
    )
    
    def save(self, *args, **kwargs):
        if not self.code_acces:
            import secrets
            self.code_acces = secrets.token_urlsafe(12)
        super().save(*args, **kwargs)
```

### Étape 2 : Créer la Migration (2 min)

```bash
python manage.py makemigrations
python manage.py migrate
```

### Étape 3 : Générer les Codes pour Fournisseurs Existants (3 min)

```bash
python manage.py shell
```

```python
from fleet_app.models import FournisseurVehicule
import secrets

for f in FournisseurVehicule.objects.all():
    if not f.code_acces:
        f.code_acces = secrets.token_urlsafe(12)
        f.save()
        print(f"{f.nom}: {f.code_acces}")
```

### Étape 4 : Remplacer la Vue (5 min)

**Fichier** : `fleet_app/views_location.py`

Remplacer la fonction `accueil_public()` (ligne 1181) par le contenu de :
```
FIX_SECURITE_ACCUEIL_PUBLIC.py
```

### Étape 5 : Créer le Template (5 min)

**Fichier** : `fleet_app/templates/fleet_app/locations/acces_code.html`

Copier le contenu de :
```
TEMPLATE_ACCES_CODE.html
```

### Étape 6 : Tester (5 min)

```bash
# 1. Récupérer un code
python manage.py shell
>>> from fleet_app.models import FournisseurVehicule
>>> f = FournisseurVehicule.objects.first()
>>> print(f.code_acces)

# 2. Tester l'accès
http://127.0.0.1:8001/accueil/?code=VOTRE_CODE

# 3. Vérifier l'isolation
# Essayer avec le code d'un autre fournisseur
# Vérifier que seuls SES véhicules s'affichent
```

### Étape 7 : Envoyer les Codes aux Propriétaires (5 min)

Créer un script d'envoi :

```python
# fleet_app/management/commands/envoyer_codes_acces.py
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from fleet_app.models import FournisseurVehicule

class Command(BaseCommand):
    def handle(self, *args, **options):
        for f in FournisseurVehicule.objects.all():
            if f.email and f.code_acces:
                url = f"https://votre-domaine.com/accueil/?code={f.code_acces}"
                
                message = f"""
Bonjour {f.nom},

Voici votre lien personnel pour consulter l'état de vos véhicules :
{url}

Ce lien est confidentiel et ne doit pas être partagé.

Cordialement,
L'équipe GuinéeGest
                """
                
                send_mail(
                    'Votre accès GuinéeGest',
                    message,
                    'noreply@guineegest.com',
                    [f.email],
                )
                
                self.stdout.write(f"✅ Code envoyé à {f.nom}")
```

Exécuter :
```bash
python manage.py envoyer_codes_acces
```

---

## 🔒 VÉRIFICATION DE SÉCURITÉ

### Test d'Isolation

```python
# Test 1 : Créer 2 fournisseurs
f1 = FournisseurVehicule.objects.create(nom="Test 1", code_acces="CODE1")
f2 = FournisseurVehicule.objects.create(nom="Test 2", code_acces="CODE2")

# Test 2 : Créer véhicules
v1 = LocationVehicule.objects.create(fournisseur=f1, ...)
v2 = LocationVehicule.objects.create(fournisseur=f2, ...)

# Test 3 : Accéder avec CODE1
# Vérifier que seul v1 est visible

# Test 4 : Accéder avec CODE2
# Vérifier que seul v2 est visible
```

### Checklist

- [ ] Champ `code_acces` ajouté au modèle
- [ ] Migration créée et appliquée
- [ ] Codes générés pour fournisseurs existants
- [ ] Vue `accueil_public()` sécurisée
- [ ] Template `acces_code.html` créé
- [ ] Tests d'isolation réussis
- [ ] Codes envoyés aux propriétaires
- [ ] Documentation mise à jour

---

## 📊 AVANT / APRÈS

### AVANT (NON SÉCURISÉ)
```python
# ❌ Affiche TOUS les véhicules
locations_actives = LocationVehicule.objects.filter(
    statut='Active'
)
```

**Résultat** : Entreprise A voit les véhicules de l'entreprise B

### APRÈS (SÉCURISÉ)
```python
# ✅ Affiche UNIQUEMENT les véhicules du propriétaire
locations_actives = LocationVehicule.objects.filter(
    fournisseur=fournisseur,  # ← FILTRAGE
    statut='Active'
)
```

**Résultat** : Chaque propriétaire voit UNIQUEMENT ses véhicules

---

## 🚀 DÉPLOIEMENT

### En Local
```bash
# 1. Appliquer les modifications
python manage.py makemigrations
python manage.py migrate

# 2. Générer les codes
python manage.py shell
# ... (voir Étape 3)

# 3. Tester
python manage.py runserver
```

### Sur PythonAnywhere
```bash
# 1. Pull les modifications
cd ~/guineegest
git pull origin main

# 2. Appliquer migrations
python manage.py makemigrations
python manage.py migrate

# 3. Générer codes
python manage.py shell
# ... (voir Étape 3)

# 4. Reload
touch /var/www/gestionnairedeparc_pythonanywhere_com_wsgi.py
```

---

## 📝 COMMIT GIT

```bash
git add fleet_app/models.py
git add fleet_app/views_location.py
git add fleet_app/templates/fleet_app/locations/acces_code.html
git add fleet_app/migrations/XXXX_add_code_acces.py
git add AUDIT_SECURITE_ISOLATION_DONNEES.md
git add FIX_SECURITE_ACCUEIL_PUBLIC.py
git add ACTIONS_SECURITE_URGENTES.md

git commit -m "Security: Fix isolation données page publique + système code d'accès

PROBLÈME CRITIQUE RÉSOLU:
- Page /accueil/ affichait TOUTES les données sans filtrage
- Violation de confidentialité et RGPD

SOLUTION IMPLÉMENTÉE:
- Ajout champ code_acces au modèle FournisseurVehicule
- Filtrage strict par fournisseur dans accueil_public()
- Template de saisie du code d'accès
- Génération automatique de codes uniques
- Tests d'isolation validés

SÉCURITÉ:
- Isolation complète des données par propriétaire
- Codes d'accès uniques et sécurisés
- Aucune fuite de données possible

IMPACT:
- Conformité RGPD restaurée
- Confidentialité garantie
- Accès propriétaires simplifié (pas de compte requis)"

git push origin main
```

---

## ⏱️ TEMPS TOTAL ESTIMÉ

- Modification modèle : 5 min
- Migration : 2 min
- Génération codes : 3 min
- Modification vue : 5 min
- Création template : 5 min
- Tests : 5 min
- Envoi codes : 5 min

**TOTAL : 30 minutes**

---

## 🎯 PRIORITÉ

**CRITIQUE - À FAIRE IMMÉDIATEMENT**

La faille de sécurité expose actuellement les données de tous les utilisateurs.

---

**📅 Date** : 04 Octobre 2025  
**⏰ Heure** : 12:01  
**🚨 Statut** : URGENT  
**✅ Action** : Appliquer MAINTENANT
