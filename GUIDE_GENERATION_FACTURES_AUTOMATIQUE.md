# Guide : Génération Automatique de Factures de Location

## Vue d'ensemble

Le système GuinéeGest dispose d'une fonctionnalité de **génération automatique de factures** basée sur les jours travaillés par les véhicules en location. Les factures sont calculées automatiquement à partir des feuilles de pontage.

## Fonctionnement

### 1. Prérequis

Pour générer des factures automatiquement, vous devez avoir :

✅ **Une location active** avec :
- Un véhicule assigné
- Un tarif journalier défini
- Des feuilles de pontage enregistrées

✅ **Des feuilles de pontage** avec statut "Travail" pour les jours facturables

### 2. Calcul automatique

Le système calcule automatiquement :

```
Montant HT = Nombre de jours "Travail" × Tarif journalier
TVA = Montant HT × 18%
Montant TTC = Montant HT + TVA
```

**Exemple :**
- Tarif journalier : 50,000 GNF
- Jours travaillés : 22 jours
- Montant HT : 22 × 50,000 = 1,100,000 GNF
- TVA (18%) : 198,000 GNF
- **Montant TTC : 1,298,000 GNF**

### 3. Types de jours comptabilisés

Le système distingue plusieurs statuts de feuilles de pontage :

| Statut | Facturable | Description |
|--------|-----------|-------------|
| **Travail** | ✅ OUI | Jours où le véhicule a travaillé (facturés) |
| **Entretien** | ❌ NON | Jours d'entretien (non facturés) |
| **Hors service** | ❌ NON | Jours où le véhicule est hors service |
| **Inactif** | ❌ NON | Jours d'inactivité |

## Utilisation

### Méthode 1 : Génération mensuelle (Recommandée)

Accédez à `/locations/factures/` et utilisez le panneau de génération en haut à droite :

1. **Sélectionnez le mois** (Jan, Fév, Mar, etc.)
2. **Saisissez l'année** (ex: 2025)
3. **Cliquez sur l'icône d'engrenage** ⚙️

Le système va :
- ✅ Parcourir toutes vos locations actives
- ✅ Compter les jours "Travail" du mois sélectionné
- ✅ Calculer les montants automatiquement
- ✅ Créer ou mettre à jour les factures

**Numéro de facture généré :** `LOC-{ID_LOCATION}-{YYYYMM}`

**Exemple :** `LOC-6-202501` pour la location #6 en janvier 2025

### Méthode 2 : Génération par location

Depuis la page d'une location spécifique :

1. Accédez à `/locations/{id}/`
2. Cliquez sur "Générer facture"
3. Le système compte tous les jours "Travail" non facturés

**Numéro de facture généré :** `FACT-{ID_LOCATION}-{TIMESTAMP}`

## Fonctionnalités avancées

### Éviter les doublons

Le système utilise un numéro de facture unique par location et par mois :
- Si une facture existe déjà pour ce mois → **Mise à jour** des montants
- Si aucune facture n'existe → **Création** d'une nouvelle facture

### Période de facturation

Pour chaque location, le système calcule :

1. **Période couverte** = Intersection entre :
   - Dates de la location (date_debut → date_fin)
   - Dates du mois sélectionné

2. **Jours travaillés** = Feuilles de pontage "Travail" dans cette période

3. **Jours non travaillés** = Jours couverts - Jours travaillés

**Exemple :**
- Location du 15 janvier au 15 février 2025
- Génération pour janvier 2025
- Période couverte : 15-31 janvier (17 jours)
- Jours travaillés : 14 jours
- Jours non travaillés : 3 jours

### Statut des factures

Les factures générées automatiquement ont le statut **"Brouillon"** par défaut.

Vous pouvez ensuite :
- ✅ Modifier les montants si nécessaire
- ✅ Changer le statut en "Payée" une fois le paiement reçu
- ✅ Annuler la facture si besoin

## Interface utilisateur

### Page `/locations/factures/`

```
┌─────────────────────────────────────────────────────────────┐
│ 🧾 Factures                    [Mois ▼] [2025] ⚙️ [PDF Lot] │
├─────────────────────────────────────────────────────────────┤
│ 🔍 Recherche avancée                                        │
│                                                             │
│ ☑ Numéro      Date      Véhicule    Montant   Jours   Statut│
│ ☐ LOC-6-202501 31/01/25 Toyota...  1,298,000  22/3   Brouillon│
│ ☐ LOC-7-202501 31/01/25 Nissan...  1,100,000  20/5   Brouillon│
└─────────────────────────────────────────────────────────────┘
```

### Boutons d'action

- **⚙️ Engrenage** : Génère les factures du mois sélectionné
- **PDF Lot** : Génère un PDF groupé des factures sélectionnées
- **+ Nouvelle Facture** : Création manuelle d'une facture

## Réponse du système

Après génération, le système affiche :

```
✅ Factures générées/mises à jour pour 3 location(s) sur 2025-01.
Total du mois: 3,398,000 GNF

Détails:
- Location #6 (Toyota Hilux): 22 jours travaillés → 1,298,000 GNF
- Location #7 (Nissan Patrol): 20 jours travaillés → 1,100,000 GNF
- Location #8 (Mercedes Sprinter): 18 jours travaillés → 1,000,000 GNF
```

## Génération de PDF

Une fois les factures générées :

1. **PDF individuel** : Cliquez sur l'icône PDF à côté de chaque facture
2. **PDF en lot** : 
   - Cochez les factures souhaitées
   - Cliquez sur "PDF Lot (X)"
   - Un PDF unique avec toutes les factures sera généré

## Bonnes pratiques

### ✅ À faire

1. **Enregistrer les feuilles de pontage régulièrement** (quotidiennement ou hebdomadairement)
2. **Générer les factures en fin de mois** pour avoir tous les jours comptabilisés
3. **Vérifier les montants** avant de changer le statut en "Payée"
4. **Archiver les PDF** pour la comptabilité

### ❌ À éviter

1. Ne pas oublier d'enregistrer les feuilles de pontage (sinon jours = 0)
2. Ne pas modifier manuellement les numéros de facture générés automatiquement
3. Ne pas supprimer les factures "Brouillon" sans raison (les mettre à jour plutôt)

## Dépannage

### Problème : Aucune facture générée

**Causes possibles :**
- Aucune location active pour le mois sélectionné
- Aucune feuille de pontage "Travail" enregistrée
- Tarif journalier = 0

**Solution :**
1. Vérifiez que des locations existent pour cette période
2. Vérifiez les feuilles de pontage dans `/locations/feuilles-pontage/`
3. Vérifiez que le tarif journalier est défini dans la location

### Problème : Montant incorrect

**Causes possibles :**
- Feuilles de pontage manquantes
- Mauvais statut sur les feuilles (Entretien au lieu de Travail)
- Tarif journalier incorrect

**Solution :**
1. Vérifiez les feuilles de pontage pour le mois concerné
2. Corrigez les statuts si nécessaire
3. Mettez à jour le tarif journalier dans la location
4. Régénérez la facture pour le même mois (mise à jour automatique)

### Problème : Facture dupliquée

**Impossible :** Le système utilise un numéro unique par location et par mois. Si vous régénérez pour le même mois, la facture existante sera mise à jour, pas dupliquée.

## Accès API

Pour les développeurs, l'endpoint AJAX est :

```
POST /locations/factures/generation-mensuelle/
Paramètres:
  - month: 1-12
  - year: 2000-2100

Réponse JSON:
{
  "success": true,
  "message": "Factures générées/mises à jour pour 3 location(s) sur 2025-01.",
  "total_mois": 3398000.0,
  "details": [
    {
      "location_id": 6,
      "vehicule": "Toyota Hilux (GN-001-AA)",
      "jours_travail": 22,
      "jours_non_travail": 3,
      "montant_ttc": 1298000.0,
      "facture_id": 15,
      "numero": "LOC-6-202501",
      "created": false
    }
  ]
}
```

## Support

Pour toute question ou problème, contactez l'administrateur système.

---
**Version :** GuinéeGest v1.0  
**Dernière mise à jour :** 2025-10-04  
**Module :** Locations - Facturation automatique
