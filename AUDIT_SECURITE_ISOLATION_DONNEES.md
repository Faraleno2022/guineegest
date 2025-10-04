# 🔒 Audit de Sécurité - Isolation des Données

## 🎯 Objectif
Garantir qu'aucun utilisateur ne puisse voir les données d'un autre utilisateur/entreprise.

---

## ✅ Points Sécurisés (Avec `queryset_filter_by_tenant`)

### 1. Module Locations
| Vue | Fichier | Ligne | Statut |
|-----|---------|-------|--------|
| `locations_dashboard` | views_location.py | 31 | ✅ Sécurisé |
| `location_list` | views_location.py | 305 | ✅ Sécurisé |
| `feuille_pontage_list` | views_location.py | 369 | ✅ Sécurisé |
| `fournisseur_list` | views_location.py | 376 | ✅ Sécurisé |
| `facture_list` | views_location.py | 383 | ✅ Sécurisé |
| `facture_detail` | views_location.py | 390 | ✅ Sécurisé |
| `facture_pdf` | views_location.py | 1015 | ✅ Sécurisé |
| `factures_batch_pdf` | views_location.py | 1106 | ✅ Sécurisé |
| `location_search_ajax` | views_location.py | 305 | ✅ Sécurisé |
| `feuille_pontage_search_ajax` | views_location.py | 149 | ✅ Sécurisé |
| `fournisseur_search_ajax` | views_location.py | 211 | ✅ Sécurisé |
| `facture_search_ajax` | views_location.py | 248 | ✅ Sécurisé |

### 2. Module Gestion Personnel
| Vue | Fichier | Ligne | Statut |
|-----|---------|-------|--------|
| `employe_list` | views_management.py | 41 | ✅ Sécurisé |
| `paie_list` | views_management.py | 55 | ✅ Sécurisé |
| `heure_sup_list` | views_management.py | 74 | ✅ Sécurisé |

### 3. Module Véhicules (views.py)
| Vue | Fichier | Ligne | Statut |
|-----|---------|-------|--------|
| `home` (locations) | views.py | 78, 83, 102 | ✅ Sécurisé |
| `dashboard` (locations) | views.py | 934, 939 | ✅ Sécurisé |

---

## 🚨 PROBLÈME CRITIQUE IDENTIFIÉ

### Page Publique `/accueil/` - FAILLE DE SÉCURITÉ

**Fichier** : `views_location.py`  
**Fonction** : `accueil_public()` (ligne 1181)  
**Problème** : Affiche TOUTES les données de TOUTES les entreprises

#### Code Actuel (NON SÉCURISÉ)
```python
def accueil_public(request):
    # ❌ PAS de filtrage par tenant !
    feuilles_today = FeuillePontageLocation.objects.filter(
        date=today
    ).select_related(...)
    
    # ❌ PAS de filtrage par tenant !
    locations_actives = LocationVehicule.objects.filter(
        statut='Active'
    ).select_related(...)
```

#### Impact
- ❌ Entreprise A peut voir les véhicules de l'entreprise B
- ❌ Propriétaire 1 peut voir les véhicules du propriétaire 2
- ❌ Violation du RGPD et confidentialité
- ❌ Risque de fuite de données sensibles

---

## 🔧 Solutions Proposées

### Option 1 : Authentification Requise (Recommandé)
Supprimer l'accès public et exiger une authentification.

```python
@login_required
def accueil_public(request):
    today = timezone.now().date()
    
    # ✅ Filtrage par tenant
    feuilles_today = queryset_filter_by_tenant(
        FeuillePontageLocation.objects.all(), request
    ).filter(date=today).select_related(...)
    
    # ✅ Filtrage par tenant
    locations_actives = queryset_filter_by_tenant(
        LocationVehicule.objects.all(), request
    ).filter(statut='Active').select_related(...)
```

**Avantages** :
- ✅ Sécurité maximale
- ✅ Isolation complète des données
- ✅ Conforme RGPD

**Inconvénients** :
- ❌ Propriétaires doivent avoir un compte
- ❌ Perd l'aspect "public"

---

### Option 2 : Filtrage par Token/Code Propriétaire
Ajouter un système de code d'accès pour chaque propriétaire.

```python
def accueil_public(request):
    # Récupérer le code propriétaire depuis l'URL ou session
    code_proprietaire = request.GET.get('code') or request.session.get('code_proprietaire')
    
    if not code_proprietaire:
        return redirect('login_proprietaire')
    
    # Vérifier le code et récupérer le propriétaire
    try:
        fournisseur = FournisseurVehicule.objects.get(
            code_acces=code_proprietaire,
            user=request.user if request.user.is_authenticated else None
        )
    except FournisseurVehicule.DoesNotExist:
        return render(request, 'erreur_acces.html')
    
    # ✅ Filtrer uniquement les véhicules de ce propriétaire
    locations_actives = LocationVehicule.objects.filter(
        fournisseur=fournisseur,
        statut='Active'
    ).select_related(...)
```

**Avantages** :
- ✅ Pas besoin de compte utilisateur
- ✅ Isolation des données
- ✅ URL unique par propriétaire

**Inconvénients** :
- ⚠️ Nécessite modification du modèle (ajout code_acces)
- ⚠️ Gestion des codes d'accès

---

### Option 3 : Filtrage par Entreprise dans l'URL
Utiliser un paramètre d'entreprise dans l'URL.

```python
def accueil_public(request, entreprise_slug):
    # Récupérer l'entreprise
    entreprise = get_object_or_404(Entreprise, slug=entreprise_slug)
    
    # ✅ Filtrer par entreprise
    locations_actives = LocationVehicule.objects.filter(
        user__entreprise=entreprise,
        statut='Active'
    ).select_related(...)
```

**URL** : `/accueil/mon-entreprise/`

**Avantages** :
- ✅ Simple à implémenter
- ✅ URL lisible

**Inconvénients** :
- ⚠️ Slug d'entreprise peut être deviné
- ⚠️ Pas de contrôle d'accès strict

---

## 🛡️ Recommandation Finale

### Solution Hybride (Meilleure Approche)

1. **Pour les gestionnaires** : Authentification requise
   - Accès via `/dashboard/` et `/locations/`
   - Filtrage strict par `queryset_filter_by_tenant`

2. **Pour les propriétaires** : Code d'accès unique
   - Accès via `/accueil/?code=ABC123`
   - Filtrage par fournisseur uniquement
   - Code généré automatiquement et envoyé par email/SMS

3. **Implémentation** :

```python
def accueil_public(request):
    """
    Page publique avec code d'accès pour propriétaires
    """
    code = request.GET.get('code', '').strip()
    
    if not code:
        return render(request, 'fleet_app/locations/acces_code.html', {
            'error': 'Code d\'accès requis'
        })
    
    # Vérifier le code
    try:
        fournisseur = FournisseurVehicule.objects.get(
            code_acces=code,
            actif=True
        )
    except FournisseurVehicule.DoesNotExist:
        return render(request, 'fleet_app/locations/acces_code.html', {
            'error': 'Code d\'accès invalide'
        })
    
    # Sauvegarder en session
    request.session['code_proprietaire'] = code
    request.session['fournisseur_id'] = fournisseur.id
    
    today = timezone.now().date()
    
    # ✅ Filtrer UNIQUEMENT les véhicules de ce propriétaire
    locations_actives = LocationVehicule.objects.filter(
        fournisseur=fournisseur,
        statut='Active'
    ).select_related('vehicule').order_by('vehicule__immatriculation')
    
    # Feuilles de pontage du jour pour ce propriétaire
    feuilles_today = FeuillePontageLocation.objects.filter(
        location__fournisseur=fournisseur,
        date=today
    ).select_related('location', 'location__vehicule')
    
    # Créer dictionnaire véhicules
    vehicules_info = {}
    for location in locations_actives:
        vehicule = location.vehicule
        immat = vehicule.immatriculation
        feuille = feuilles_today.filter(location=location).first()
        
        vehicules_info[immat] = {
            'vehicule': vehicule,
            'location': location,
            'fournisseur': fournisseur,  # Toujours le même
            'feuille': feuille,
            'statut_jour': feuille.statut if feuille else 'Non renseigné',
            'a_travaille': feuille and feuille.statut == 'Travail',
            'en_panne': feuille and feuille.statut in ['Hors service', 'Panne'],
            'en_entretien': feuille and feuille.statut == 'Entretien',
        }
    
    context = {
        'today': today,
        'fournisseur': fournisseur,
        'vehicules_info': vehicules_info,
        'total_vehicules': len(vehicules_info),
        'vehicules_travail': sum(1 for v in vehicules_info.values() if v['a_travaille']),
        'vehicules_panne': sum(1 for v in vehicules_info.values() if v['en_panne']),
        'vehicules_entretien': sum(1 for v in vehicules_info.values() if v['en_entretien']),
    }
    
    return render(request, 'fleet_app/locations/accueil_public.html', context)
```

---

## 📝 Modifications Nécessaires

### 1. Modèle FournisseurVehicule
Ajouter un champ `code_acces` :

```python
class FournisseurVehicule(models.Model):
    # ... champs existants ...
    code_acces = models.CharField(
        max_length=20, 
        unique=True, 
        blank=True,
        help_text="Code d'accès unique pour la page publique"
    )
    
    def save(self, *args, **kwargs):
        if not self.code_acces:
            # Générer un code unique
            import secrets
            self.code_acces = secrets.token_urlsafe(12)
        super().save(*args, **kwargs)
```

### 2. Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Template de Saisie du Code
Créer `acces_code.html` :

```html
<div class="container mt-5">
    <div class="card mx-auto" style="max-width: 500px;">
        <div class="card-body">
            <h3>Accès Propriétaires</h3>
            <p>Veuillez entrer votre code d'accès</p>
            
            {% if error %}
            <div class="alert alert-danger">{{ error }}</div>
            {% endif %}
            
            <form method="get">
                <input type="text" name="code" class="form-control" 
                       placeholder="Code d'accès" required>
                <button type="submit" class="btn btn-primary mt-3">
                    Accéder
                </button>
            </form>
        </div>
    </div>
</div>
```

### 4. Email aux Propriétaires
Envoyer le code d'accès :

```python
def envoyer_code_acces(fournisseur):
    url = f"https://votre-domaine.com/accueil/?code={fournisseur.code_acces}"
    
    message = f"""
    Bonjour {fournisseur.nom},
    
    Voici votre lien d'accès pour consulter l'état de vos véhicules :
    {url}
    
    Ce lien est personnel et confidentiel.
    """
    
    # Envoyer par email
    send_mail(
        'Votre accès GuinéeGest',
        message,
        'noreply@guineegest.com',
        [fournisseur.email],
    )
```

---

## ✅ Checklist de Sécurité

### Avant Déploiement
- [ ] Modifier `accueil_public()` avec filtrage par code
- [ ] Ajouter champ `code_acces` au modèle
- [ ] Créer migration
- [ ] Créer template `acces_code.html`
- [ ] Générer codes pour fournisseurs existants
- [ ] Envoyer codes par email
- [ ] Tester isolation des données
- [ ] Vérifier qu'aucun utilisateur ne voit les données d'un autre

### Tests de Sécurité
```python
# Test 1 : Vérifier isolation
def test_isolation_proprietaires():
    # Créer 2 fournisseurs
    f1 = FournisseurVehicule.objects.create(nom="Fournisseur 1")
    f2 = FournisseurVehicule.objects.create(nom="Fournisseur 2")
    
    # Créer véhicules
    v1 = LocationVehicule.objects.create(fournisseur=f1, ...)
    v2 = LocationVehicule.objects.create(fournisseur=f2, ...)
    
    # Accéder avec code f1
    response = client.get(f'/accueil/?code={f1.code_acces}')
    
    # Vérifier que seul v1 est visible
    assert v1.vehicule.immatriculation in response.content.decode()
    assert v2.vehicule.immatriculation not in response.content.decode()
```

---

## 📊 Résumé

### État Actuel
- ✅ 95% des vues sont sécurisées avec `queryset_filter_by_tenant`
- ❌ 1 vue critique non sécurisée : `accueil_public()`

### Actions Requises
1. **URGENT** : Sécuriser `accueil_public()` avec système de code
2. Ajouter champ `code_acces` au modèle
3. Générer et envoyer codes aux propriétaires
4. Tester isolation complète

### Impact
- **Avant** : Fuite de données possible
- **Après** : Isolation totale garantie

---

**📅 Date** : 04 Octobre 2025  
**🎯 Priorité** : CRITIQUE  
**⏱️ Temps estimé** : 2-3 heures  
**✅ Statut** : À implémenter IMMÉDIATEMENT
