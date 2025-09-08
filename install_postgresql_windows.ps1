# Script d'installation PostgreSQL pour Windows
# Exécutez ce script en tant qu'administrateur

Write-Host "=== Installation PostgreSQL pour GuinéeGest ===" -ForegroundColor Green

# Vérifier les privilèges administrateur
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERREUR: Ce script doit être exécuté en tant qu'administrateur!" -ForegroundColor Red
    Write-Host "Clic droit sur PowerShell > Exécuter en tant qu'administrateur" -ForegroundColor Yellow
    pause
    exit 1
}

# URL de téléchargement PostgreSQL 15 (version stable recommandée)
$postgresUrl = "https://get.enterprisedb.com/postgresql/postgresql-15.8-1-windows-x64.exe"
$installerPath = "$env:TEMP\postgresql-installer.exe"

Write-Host "1. Téléchargement de PostgreSQL..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri $postgresUrl -OutFile $installerPath -UseBasicParsing
    Write-Host "✓ Téléchargement terminé" -ForegroundColor Green
} catch {
    Write-Host "✗ Erreur de téléchargement: $_" -ForegroundColor Red
    Write-Host "Téléchargez manuellement depuis: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    pause
    exit 1
}

Write-Host "2. Lancement de l'installation..." -ForegroundColor Yellow
Write-Host "IMPORTANT: Notez bien le mot de passe du superutilisateur 'postgres' !" -ForegroundColor Red

# Lancer l'installateur
Start-Process -FilePath $installerPath -Wait

Write-Host "3. Vérification de l'installation..." -ForegroundColor Yellow

# Ajouter PostgreSQL au PATH si nécessaire
$pgPath = "C:\Program Files\PostgreSQL\15\bin"
if (Test-Path $pgPath) {
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")
    if ($currentPath -notlike "*$pgPath*") {
        Write-Host "Ajout de PostgreSQL au PATH..." -ForegroundColor Yellow
        [Environment]::SetEnvironmentVariable("PATH", "$currentPath;$pgPath", "Machine")
        $env:PATH += ";$pgPath"
    }
    Write-Host "✓ PostgreSQL installé avec succès" -ForegroundColor Green
} else {
    Write-Host "✗ Installation non détectée" -ForegroundColor Red
    exit 1
}

# Test de la commande psql
try {
    & "$pgPath\psql.exe" --version
    Write-Host "✓ Commande psql fonctionnelle" -ForegroundColor Green
} catch {
    Write-Host "✗ Erreur avec psql" -ForegroundColor Red
}

Write-Host "`n=== Prochaines étapes ===" -ForegroundColor Green
Write-Host "1. Redémarrez PowerShell pour actualiser le PATH"
Write-Host "2. Exécutez: setup_database.ps1"
Write-Host "3. Configurez le fichier .env"

# Nettoyer le fichier temporaire
Remove-Item $installerPath -ErrorAction SilentlyContinue

Write-Host "`nInstallation terminée !" -ForegroundColor Green
pause
