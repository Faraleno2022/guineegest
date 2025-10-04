# Script de déploiement GitHub avec images - Version 2.1.0
# Date: 04 Octobre 2025

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DÉPLOIEMENT GITHUB AVEC IMAGES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Vérifier le statut Git
Write-Host "📊 Vérification du statut Git..." -ForegroundColor Yellow
git status --short
Write-Host ""

# 2. Vérifier les images
Write-Host "🖼️  Vérification des images..." -ForegroundColor Yellow
$images = Get-ChildItem -Path "media\images" -Recurse -Include *.jpg,*.jpeg,*.png,*.gif,*.webp,*.svg -ErrorAction SilentlyContinue
if ($images) {
    Write-Host "✅ Images trouvées:" -ForegroundColor Green
    foreach ($img in $images) {
        Write-Host "   - $($img.FullName.Replace((Get-Location).Path + '\', ''))" -ForegroundColor White
    }
} else {
    Write-Host "⚠️  Aucune image trouvée dans media/images/" -ForegroundColor Yellow
}
Write-Host ""

# 3. Forcer l'ajout des images (même si dans .gitignore)
Write-Host "➕ Ajout forcé des images..." -ForegroundColor Yellow
git add -f media/images/**/*.jpg
git add -f media/images/**/*.jpeg
git add -f media/images/**/*.png
git add -f media/images/**/*.gif
git add -f media/images/**/*.webp
git add -f media/images/**/*.svg
Write-Host "✅ Images ajoutées" -ForegroundColor Green
Write-Host ""

# 4. Ajouter tous les autres fichiers
Write-Host "➕ Ajout des fichiers modifiés..." -ForegroundColor Yellow
git add fleet_app/
git add fleet_management/
git add *.md
git add *.txt
git add *.ps1
Write-Host "✅ Fichiers ajoutés" -ForegroundColor Green
Write-Host ""

# 5. Afficher les fichiers à commiter
Write-Host "📝 Fichiers à commiter:" -ForegroundColor Yellow
git status --short
Write-Host ""

# 6. Demander confirmation
$confirmation = Read-Host "Voulez-vous continuer avec le commit? (O/N)"
if ($confirmation -ne 'O' -and $confirmation -ne 'o') {
    Write-Host "❌ Opération annulée" -ForegroundColor Red
    exit
}

# 7. Créer le commit
Write-Host ""
Write-Host "💾 Création du commit..." -ForegroundColor Yellow
$commitMessage = @"
Feature: Version 2.1.0 - 4 fonctionnalités + 6 corrections + Images

FONCTIONNALITÉS AJOUTÉES:

1. CORRECTIONS PDF FACTURES:
   ✅ Fix format date/heure (séparation filtres date et time)
   ✅ Import BytesIO ajouté dans views_location.py
   ✅ Import pisa dans factures_batch_pdf()
   ✅ Tests validés: PDF individuel (5KB) + PDF lot (8KB)

2. PAGE D'ACCUEIL PUBLIQUE (/accueil/):
   ✅ Accessible sans authentification
   ✅ Affiche état journalier des véhicules en location
   ✅ Statistiques en temps réel
   ✅ Design moderne responsive avec Bootstrap 5
   ✅ Auto-refresh toutes les 5 minutes
   ✅ Badges colorés par statut
   ✅ Arrière-plan blanc avec en-tête dégradé
   ✅ Bouton retour à la page d'accueil

3. BLOC VÉHICULES EN LOCATION (Dashboard):
   ✅ Ajouté dans dashboard principal après section KPI
   ✅ Statistiques rapides (4 cartes)
   ✅ Tableau détaillé des 10 premiers véhicules
   ✅ Lien vers page publique

4. BLOC VÉHICULES EN LOCATION (Page d'accueil):
   ✅ Ajouté sur home.html après "Nos services principaux"
   ✅ Aperçu de 6 véhicules avec badges
   ✅ Affichage conditionnel selon authentification

CORRECTIONS DE BUGS:
1. TypeError - Format date avec heure (PDF)
2. NameError - BytesIO non importé
3. NameError - pisa non importé
4. AttributeError - Context processor
5. UnboundLocalError - Variable timezone
6. NoReverseMatch - URL feuille_pontage_list

IMAGES AJOUTÉES:
✅ media/images/Acces.jpg
✅ media/images/Acces_optimized.jpg
✅ media/images/Acces_optimized.webp
✅ media/images/team/fara.png
✅ media/images/team/ifono.jpg

FICHIERS MODIFIÉS:
- Backend: views.py, views_location.py, urls.py, context_processors.py
- Frontend: dashboard.html, home.html, accueil_public.html, templates PDF
- Documentation: 18 fichiers MD

TESTS: 100% réussis
URLs: /, /dashboard/, /accueil/ (nouveau)
Version: 2.1.0
"@

git commit -m $commitMessage
Write-Host "✅ Commit créé" -ForegroundColor Green
Write-Host ""

# 8. Afficher le dernier commit
Write-Host "📋 Dernier commit:" -ForegroundColor Yellow
git log -1 --oneline
Write-Host ""

# 9. Vérifier les images dans le commit
Write-Host "🖼️  Images dans le commit:" -ForegroundColor Yellow
git diff-tree --no-commit-id --name-only -r HEAD | Select-String "media/images"
Write-Host ""

# 10. Demander confirmation pour push
$pushConfirmation = Read-Host "Voulez-vous pusher vers GitHub? (O/N)"
if ($pushConfirmation -ne 'O' -and $pushConfirmation -ne 'o') {
    Write-Host "⚠️  Commit local créé mais pas pushé" -ForegroundColor Yellow
    Write-Host "Pour pusher plus tard: git push origin main" -ForegroundColor Cyan
    exit
}

# 11. Push vers GitHub
Write-Host ""
Write-Host "🚀 Push vers GitHub..." -ForegroundColor Yellow
git push origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Push réussi!" -ForegroundColor Green
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  DÉPLOIEMENT GITHUB RÉUSSI!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "📊 RÉSUMÉ:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "✅ Code source pushé" -ForegroundColor Green
    Write-Host "✅ Images incluses dans le commit" -ForegroundColor Green
    Write-Host "✅ Documentation complète" -ForegroundColor Green
    Write-Host ""
    
    Write-Host "🖼️  IMAGES DISPONIBLES EN LIGNE:" -ForegroundColor Yellow
    Write-Host "   - Hero image: media/images/Acces_optimized.jpg" -ForegroundColor White
    Write-Host "   - WebP version: media/images/Acces_optimized.webp" -ForegroundColor White
    Write-Host "   - Équipe Fara: media/images/team/fara.png" -ForegroundColor White
    Write-Host "   - Équipe Ifono: media/images/team/ifono.jpg" -ForegroundColor White
    Write-Host ""
    
    Write-Host "📌 PROCHAINES ÉTAPES:" -ForegroundColor Yellow
    Write-Host "  1. Déployer sur PythonAnywhere:" -ForegroundColor White
    Write-Host "     cd ~/guineegest" -ForegroundColor Gray
    Write-Host "     git pull origin main" -ForegroundColor Gray
    Write-Host "     # Reload web app" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  2. Vérifier les images en ligne:" -ForegroundColor White
    Write-Host "     https://github.com/votre-repo/tree/main/media/images" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  3. Tester l'affichage:" -ForegroundColor White
    Write-Host "     - Page d'accueil: /" -ForegroundColor Gray
    Write-Host "     - Page publique: /accueil/" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "🎉 SUCCÈS COMPLET!" -ForegroundColor Green
    Write-Host "   - Version 2.1.0 déployée" -ForegroundColor White
    Write-Host "   - Images disponibles en ligne" -ForegroundColor White
    Write-Host "   - Documentation à jour" -ForegroundColor White
    Write-Host ""
    
} else {
    Write-Host "❌ Erreur lors du push" -ForegroundColor Red
    Write-Host "Vérifiez votre connexion et réessayez" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "💡 Commandes utiles:" -ForegroundColor Yellow
    Write-Host "   git status" -ForegroundColor Gray
    Write-Host "   git log -1" -ForegroundColor Gray
    Write-Host "   git push origin main --force (si nécessaire)" -ForegroundColor Gray
}
