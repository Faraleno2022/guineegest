# Script de déploiement - Page d'Accueil Publique
# Date: 2025-10-04

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DÉPLOIEMENT PAGE ACCUEIL PUBLIQUE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier le statut Git
Write-Host "📊 Vérification du statut Git..." -ForegroundColor Yellow
git status --short
Write-Host ""

# 2. Ajouter tous les fichiers
Write-Host "➕ Ajout des fichiers modifiés..." -ForegroundColor Yellow
git add .
Write-Host "✅ Fichiers ajoutés" -ForegroundColor Green
Write-Host ""

# 3. Afficher les fichiers à commiter
Write-Host "📝 Fichiers à commiter:" -ForegroundColor Yellow
git status --short
Write-Host ""

# 4. Demander confirmation
$confirmation = Read-Host "Voulez-vous continuer avec le commit? (O/N)"
if ($confirmation -ne 'O' -and $confirmation -ne 'o') {
    Write-Host "❌ Opération annulée" -ForegroundColor Red
    exit
}

# 5. Commit avec message
Write-Host ""
Write-Host "💾 Création du commit..." -ForegroundColor Yellow
$commitMessage = @"
Feature: Page d'accueil publique pour suivi véhicules en location

NOUVELLE FONCTIONNALITÉ:
- Page publique accessible sans authentification (/accueil/)
- Permet aux propriétaires de consulter l'état de leurs véhicules
- Interface moderne et responsive avec Bootstrap 5
- Auto-refresh toutes les 5 minutes

FONCTIONNALITÉS:
✅ Statistiques globales (total, actifs, panne, entretien)
✅ Informations détaillées par véhicule
✅ Badges colorés par statut (vert/rouge/jaune/gris)
✅ Affichage propriétaire (nom, contact, téléphone)
✅ Commentaires et période de location
✅ Design responsive (mobile/desktop)

FICHIERS CRÉÉS:
- fleet_app/templates/fleet_app/locations/accueil_public.html
- Documentation complète (7 fichiers MD)

FICHIERS MODIFIÉS:
- fleet_app/views_location.py (ajout fonction accueil_public)
- fleet_management/urls.py (ajout route /accueil/)
- fleet_app/context_processors.py (fix pour requêtes sans auth)

TESTS:
✅ Tous les tests passés avec succès

URL: /accueil/
"@

git commit -m $commitMessage
Write-Host "✅ Commit créé" -ForegroundColor Green
Write-Host ""

# 6. Afficher le dernier commit
Write-Host "📋 Dernier commit:" -ForegroundColor Yellow
git log -1 --oneline
Write-Host ""

# 7. Demander confirmation pour push
$pushConfirmation = Read-Host "Voulez-vous pusher vers GitHub? (O/N)"
if ($pushConfirmation -ne 'O' -and $pushConfirmation -ne 'o') {
    Write-Host "⚠️  Commit local créé mais pas pushé" -ForegroundColor Yellow
    Write-Host "Pour pusher plus tard: git push origin main" -ForegroundColor Cyan
    exit
}

# 8. Push vers GitHub
Write-Host ""
Write-Host "🚀 Push vers GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Push réussi!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📌 Prochaines étapes:" -ForegroundColor Yellow
    Write-Host "  1. Déployer sur PythonAnywhere" -ForegroundColor White
    Write-Host "  2. Tester en production: /accueil/" -ForegroundColor White
    Write-Host "  3. Partager l'URL avec les propriétaires" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "❌ Erreur lors du push" -ForegroundColor Red
    Write-Host "Vérifiez votre connexion et réessayez" -ForegroundColor Yellow
}
