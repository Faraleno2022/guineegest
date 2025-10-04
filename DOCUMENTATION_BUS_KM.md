# 📋 Documentation - Module Bus/Km (Frais Kilométriques)

## 🎯 Vue d'ensemble

Le module **Bus/Km** permet de gérer les frais kilométriques des employés (chauffeurs). Il calcule automatiquement le montant à payer en fonction des kilomètres parcourus et de la valeur par kilomètre configurée.

---

## ✅ Fonctionnalités Implémentées

### 1. **Gestion des Frais Kilométriques**
- ✅ Ajout de frais kilométriques pour un employé
- ✅ Modification des frais existants
- ✅ Suppression des frais
- ✅ Calcul automatique du total (km × valeur/km)

### 2. **Configuration Flexible**
- ✅ Valeur par km configurée au niveau de l'employé
- ✅ Possibilité de définir une valeur personnalisée par trajet
- ✅ Description optionnelle du trajet

### 3. **Filtrage et Recherche**
- ✅ Filtrage par mois et année
- ✅ Affichage des totaux par employé
- ✅ Groupement automatique des données

### 4. **Interface Utilisateur**
- ✅ Liste des frais avec pagination
- ✅ Cartes de synthèse par employé
- ✅ Modals pour modification/suppression
- ✅ Design moderne et responsive

---

## 📊 Structure des Données

### Modèle `FraisKilometrique`

| Champ | Type | Description |
|-------|------|-------------|
| **employe** | ForeignKey | Employé concerné |
| **date** | DateField | Date du trajet |
| **kilometres** | DecimalField | Kilomètres parcourus |
| **valeur_par_km** | DecimalField | Valeur par km (optionnel) |
| **total_a_payer** | DecimalField | Total calculé automatiquement |
| **description** | TextField | Description du trajet (optionnel) |
| **user** | ForeignKey | Utilisateur propriétaire |
| **created_at** | DateTimeField | Date de création |
| **updated_at** | DateTimeField | Date de modification |

### Champ ajouté au modèle `Employe`

| Champ | Type | Description |
|-------|------|-------------|
| **valeur_km** | DecimalField | Valeur par km par défaut pour cet employé |

---

## 🔧 Composants Créés

### 1. **Backend**

#### Modèle
- **Fichier** : `fleet_app/models_entreprise.py`
- **Classe** : `FraisKilometrique`
- **Méthodes** :
  - `obtenir_valeur_km_employe()` : Récupère la valeur configurée pour l'employé
  - `get_valeur_km()` : Retourne la valeur à utiliser (personnalisée ou configurée)
  - `get_total_calcule()` : Calcule le total dynamiquement
  - `save()` : Calcul automatique du total lors de la sauvegarde

#### Formulaire
- **Fichier** : `fleet_app/forms_entreprise.py`
- **Classe** : `FraisKilometriqueForm`
- **Champs** : employe, date, kilometres, valeur_par_km, description
- **Validation** : Vérifie que les kilomètres sont > 0

#### Vues
- **Fichier** : `fleet_app/views_entreprise.py`
- **Classe** : `FraisKilometriqueListView` (ListView)
  - Affichage de la liste avec filtres
  - Calcul des totaux par employé
  - Actions : modifier, supprimer, définir valeur personnalisée
- **Fonction** : `frais_kilometrique_ajouter()`
  - Ajout d'un nouveau frais kilométrique

#### URLs
- **Fichier** : `fleet_app/urls.py`
- **Routes** :
  - `/frais-kilometriques/` : Liste des frais
  - `/frais-kilometriques/ajouter/` : Formulaire d'ajout

### 2. **Frontend**

#### Templates
1. **frais_kilometrique_list.html**
   - Liste des frais avec tableau
   - Cartes de synthèse par employé
   - Filtres par mois/année
   - Modals de modification/suppression
   - Pagination

2. **frais_kilometrique_form.html**
   - Formulaire d'ajout
   - Aide contextuelle
   - Validation côté client

#### Navigation
- **Fichier** : `fleet_app/templates/fleet_app/base.html`
- **Menu** : Management > Bus/Km
- **Icône** : `fas fa-bus`

### 3. **Administration Django**
- **Fichier** : `fleet_app/admin.py`
- **Classe** : `FraisKilometriqueAdmin`
- **Fonctionnalités** :
  - Liste avec colonnes personnalisées
  - Filtres par date
  - Recherche par employé et description
  - Hiérarchie par date
  - Champ total_a_payer en lecture seule

---

## 📝 Utilisation

### 1. **Configurer la valeur par km pour un employé**

1. Aller dans **Management > Employés**
2. Modifier un employé
3. Renseigner le champ **"Valeur par km (GNF)"**
4. Enregistrer

### 2. **Ajouter un frais kilométrique**

1. Aller dans **Management > Bus/Km**
2. Cliquer sur **"Ajouter des frais km"**
3. Remplir le formulaire :
   - Sélectionner l'employé
   - Saisir la date
   - Saisir les kilomètres parcourus
   - (Optionnel) Saisir une valeur par km spécifique
   - (Optionnel) Ajouter une description
4. Cliquer sur **"Enregistrer"**

### 3. **Consulter les frais par mois**

1. Aller dans **Management > Bus/Km**
2. Utiliser les filtres **Mois** et **Année**
3. Cliquer sur **"Filtrer"**
4. Les totaux par employé s'affichent en haut

### 4. **Modifier un frais**

1. Dans la liste, cliquer sur l'icône **"Modifier"** (crayon)
2. Modifier les champs dans le modal
3. Cliquer sur **"Enregistrer"**

### 5. **Supprimer un frais**

1. Dans la liste, cliquer sur l'icône **"Supprimer"** (poubelle)
2. Confirmer la suppression dans le modal

---

## 🧮 Calcul Automatique

### Formule
```
Total à payer = Kilomètres × Valeur par km
```

### Priorité de la valeur par km
1. **Valeur personnalisée** (si renseignée pour ce trajet)
2. **Valeur configurée** (dans le profil de l'employé)
3. **0** (si aucune valeur n'est configurée)

### Exemple
- Employé : Jean Dupont
- Valeur par km configurée : 500 GNF
- Trajet 1 : 50 km → Total = 50 × 500 = **25,000 GNF**
- Trajet 2 : 30 km avec valeur personnalisée 600 GNF → Total = 30 × 600 = **18,000 GNF**

---

## 📊 Totaux par Employé

Le système calcule automatiquement pour chaque employé :
- **Total des kilomètres** parcourus
- **Nombre de trajets** effectués
- **Total à payer** (somme de tous les frais)

Ces totaux sont affichés :
- Dans des cartes en haut de la liste
- Filtrables par mois/année
- Avec des badges colorés

---

## 🎨 Interface Utilisateur

### Cartes de Synthèse
```
┌─────────────────────────────────────┐
│ 👤 Jean Dupont                      │
│ Matricule: EMP001                   │
│                                     │
│ 150.50 km    5 trajets             │
│                     75,250 GNF ✓   │
└─────────────────────────────────────┘
```

### Tableau
| Matricule | Prénom | Nom | Fonction | Date | Km | Valeur/Km | Total | Description | Actions |
|-----------|--------|-----|----------|------|----|-----------| ------|-------------|---------|
| EMP001 | Jean | Dupont | Chauffeur | 15/10/2025 | 50.00 | 500 | 25,000 GNF | Conakry-Kindia | ✏️ 🗑️ |

---

## 🔒 Sécurité

### Isolation des Données
- ✅ Chaque utilisateur ne voit que ses propres frais
- ✅ Filtrage automatique par `user=request.user`
- ✅ Validation des permissions sur toutes les actions

### Validation
- ✅ Kilomètres > 0
- ✅ Date valide
- ✅ Employé appartient à l'utilisateur
- ✅ Protection CSRF sur tous les formulaires

---

## 🗄️ Base de Données

### Table créée
```sql
CREATE TABLE FraisKilometriques (
    id INTEGER PRIMARY KEY,
    employe_id INTEGER NOT NULL,
    date DATE NOT NULL,
    kilometres DECIMAL(10,2) DEFAULT 0,
    valeur_par_km DECIMAL(10,2),
    total_a_payer DECIMAL(10,2) DEFAULT 0,
    description TEXT,
    user_id INTEGER,
    created_at DATETIME,
    updated_at DATETIME,
    FOREIGN KEY (employe_id) REFERENCES Employes(id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);
```

### Champ ajouté à la table Employes
```sql
ALTER TABLE Employes ADD COLUMN valeur_km DECIMAL(10,2) DEFAULT 0;
```

---

## 📁 Fichiers Modifiés/Créés

### Modifiés
1. `fleet_app/models_entreprise.py` - Ajout du modèle FraisKilometrique et champ valeur_km
2. `fleet_app/forms_entreprise.py` - Ajout du formulaire FraisKilometriqueForm
3. `fleet_app/views_entreprise.py` - Ajout des vues pour Bus/Km
4. `fleet_app/urls.py` - Ajout des routes
5. `fleet_app/admin.py` - Ajout de l'admin FraisKilometrique
6. `fleet_app/templates/fleet_app/base.html` - Ajout du menu Bus/Km

### Créés
1. `fleet_app/templates/fleet_app/entreprise/frais_kilometrique_list.html`
2. `fleet_app/templates/fleet_app/entreprise/frais_kilometrique_form.html`
3. `fleet_app/migrations/0018_add_frais_kilometrique.py`
4. `DOCUMENTATION_BUS_KM.md` (ce fichier)

---

## 🚀 Migration

### Commandes exécutées
```bash
# Créer la migration
python manage.py makemigrations fleet_app --name add_frais_kilometrique

# Appliquer la migration
python manage.py migrate fleet_app

# Vérifier l'intégrité
python manage.py check
```

### Résultat
```
✅ Migration 0018_add_frais_kilometrique créée
✅ Table FraisKilometriques créée
✅ Champ valeur_km ajouté à Employes
✅ Aucun problème détecté
```

---

## 🧪 Tests Recommandés

### Tests Manuels
1. ✅ Ajouter un frais avec valeur configurée
2. ✅ Ajouter un frais avec valeur personnalisée
3. ✅ Modifier un frais existant
4. ✅ Supprimer un frais
5. ✅ Filtrer par mois/année
6. ✅ Vérifier les totaux par employé
7. ✅ Tester la pagination
8. ✅ Vérifier l'isolation des données (multi-utilisateurs)

### Tests Unitaires (À créer)
```python
# tests/test_frais_kilometrique.py
def test_calcul_total_avec_valeur_configuree()
def test_calcul_total_avec_valeur_personnalisee()
def test_filtrage_par_mois()
def test_totaux_par_employe()
def test_isolation_donnees_utilisateur()
```

---

## 📈 Améliorations Futures

### Court Terme
- [ ] Export CSV/Excel des frais
- [ ] Graphiques d'évolution des km par mois
- [ ] Validation des doublons (même employé, même date)
- [ ] Ajout en masse (import CSV)

### Moyen Terme
- [ ] Intégration avec le module Paie
- [ ] Calcul automatique des frais dans les bulletins
- [ ] Historique des modifications
- [ ] Notifications par email

### Long Terme
- [ ] Application mobile pour saisie terrain
- [ ] Géolocalisation des trajets
- [ ] Calcul automatique des distances
- [ ] Intégration avec Google Maps

---

## 🆘 Support

### En cas de problème

1. **Erreur de migration** :
   ```bash
   python manage.py migrate fleet_app --fake 0018
   python manage.py migrate fleet_app
   ```

2. **Champ valeur_km manquant** :
   - Vérifier que la migration 0018 est appliquée
   - Recréer la migration si nécessaire

3. **Menu Bus/Km invisible** :
   - Vider le cache du navigateur
   - Vérifier que l'utilisateur est authentifié

4. **Totaux incorrects** :
   - Vérifier que la valeur_km est configurée pour l'employé
   - Vérifier les calculs dans le modèle

---

## ✅ Checklist de Déploiement

- [x] Modèle FraisKilometrique créé
- [x] Champ valeur_km ajouté au modèle Employe
- [x] Formulaire FraisKilometriqueForm créé
- [x] Vues créées (liste, ajout, modification, suppression)
- [x] Templates créés (liste, formulaire)
- [x] URLs ajoutées
- [x] Menu ajouté dans la navigation
- [x] Admin Django configuré
- [x] Migration créée et appliquée
- [x] Tests de vérification passés
- [x] Documentation créée

---

## 📞 Contact

Pour toute question ou suggestion concernant le module Bus/Km, veuillez contacter l'équipe de développement.

---

**Version** : 1.0.0  
**Date** : 04 Octobre 2025  
**Statut** : ✅ Opérationnel
