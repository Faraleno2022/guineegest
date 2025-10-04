# Correction du filtrage des locations et autres données

## Problème identifié

Les locations créées n'étaient **pas visibles** dans `/locations/list/` pour les utilisateurs sans entreprise associée.

### Cause racine

La fonction `queryset_filter_by_tenant()` dans `fleet_app/utils/decorators.py` retournait `qs.none()` (aucun résultat) lorsque :
- Le modèle avait un champ `entreprise`
- L'utilisateur n'avait pas d'entreprise associée

```python
# AVANT (code problématique)
if has_ent:
    if user_ent is not None:
        return qs.filter(**{entreprise_field: user_ent})
    # Retourne aucun résultat si pas d'entreprise
    return qs.none()  # ❌ PROBLÈME ICI
```

### Impact

Cette logique affectait **tous les modules** utilisant `queryset_filter_by_tenant()` :
- ✅ **Module Locations** : LocationVehicule, FeuillePontageLocation, FactureLocation, FournisseurVehicule
- ✅ **Module Inventaire** : Produit, EntreeStock, SortieStock, Commande
- ✅ **Module Management** : Employe, PaieEmploye, HeureSupplementaire
- ✅ **Module Véhicules** : Vehicule, Chauffeur, etc.

## Solution appliquée

Modification de la logique pour **fallback sur le filtrage par user** même si le modèle a un champ entreprise :

```python
# APRÈS (code corrigé)
# Prefer entreprise scoping when available
if has_ent and user_ent is not None:
    return qs.filter(**{entreprise_field: user_ent})

# Fallback to user scoping if field exists 
# (même si le modèle a un champ entreprise mais l'utilisateur n'a pas d'entreprise)
if has_user:
    return qs.filter(**{user_field: request.user})  # ✅ SOLUTION
```

## Résultats

### Avant la correction
```
User: LENO
Has entreprise: False
Total locations in DB: 6
Filtered locations for user: 0  ❌ Aucune location visible
```

### Après la correction
```
User: LENO
Has entreprise: False
Total locations in DB: 6
Filtered locations for user: 3  ✅ Locations visibles
  - Location 6: Toyota Hilux (GN-001-AA) (Externe)
  - Location 7: Nissan Patrol (GN-002-BB) (Externe)
  - Location 8: Mercedes Sprinter (GN-003-CC) (Externe)
```

## Fichiers modifiés

- `fleet_app/utils/decorators.py` : Correction de la fonction `queryset_filter_by_tenant()`
- `check_locations.py` : Script de diagnostic (nouveau)
- `test_location_filter.py` : Script de test (nouveau)

## Commit GitHub

**Commit a8e2143** : "fix: correction du filtrage des locations pour utilisateurs sans entreprise"

## Cas d'usage supportés

La fonction supporte maintenant 3 scénarios :

1. **Utilisateur avec entreprise** → Filtrage par entreprise (isolation multi-tenant)
2. **Utilisateur sans entreprise** → Filtrage par user (données personnelles)
3. **Modèle sans champs tenant** → Pas de filtrage (données publiques)

## Tests recommandés

1. ✅ Vérifier que les locations sont visibles dans `/locations/list/`
2. ✅ Vérifier que les fournisseurs sont visibles dans `/locations/fournisseurs/`
3. ✅ Vérifier que les factures sont visibles dans `/locations/factures/`
4. ✅ Vérifier que les employés sont visibles dans `/management/employes/`
5. ✅ Vérifier que les produits sont visibles dans `/inventaire/produits/`

## Déploiement PythonAnywhere

Commandes à exécuter :
```bash
cd ~/guineegest
git pull origin main
# Reload de l'application web via l'interface PythonAnywhere
```

---
**Date de correction** : 2025-10-04  
**Version** : GuinéeGest v1.0  
**Statut** : ✅ Corrigé et testé
