# Script de configuration de la base de données PostgreSQL pour GuinéeGest
# Exécutez après l'installation de PostgreSQL

Write-Host "=== Configuration Base de Données GuinéeGest ===" -ForegroundColor Green

# Chemin vers psql pour PostgreSQL 17
$psqlPath = "C:\Program Files\PostgreSQL\17\bin\psql.exe"

# Demander le mot de passe postgres
$postgresPassword = Read-Host "Entrez le mot de passe du superutilisateur 'postgres'" -AsSecureString
$postgresPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword))

# Demander le mot de passe pour le nouvel utilisateur
$userPassword = Read-Host "Choisissez un mot de passe pour l'utilisateur 'guineegest_user'" -AsSecureString
$userPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($userPassword))

Write-Host "1. Création de la base de données..." -ForegroundColor Yellow

# Créer un fichier SQL temporaire
$sqlScript = @"
-- Créer la base de données
CREATE DATABASE guineegest_db;

-- Créer l'utilisateur
CREATE USER guineegest_user WITH PASSWORD '$userPasswordPlain';

-- Accorder les privilèges
GRANT ALL PRIVILEGES ON DATABASE guineegest_db TO guineegest_user;

-- Se connecter à la nouvelle base
\c guineegest_db

-- Accorder les privilèges sur le schéma public (PostgreSQL 15+)
GRANT ALL ON SCHEMA public TO guineegest_user;
GRANT CREATE ON SCHEMA public TO guineegest_user;
"@

$sqlFile = "$env:TEMP\setup_guineegest.sql"
$sqlScript | Out-File -FilePath $sqlFile -Encoding UTF8

try {
    # Exécuter le script SQL
    $env:PGPASSWORD = $postgresPasswordPlain
    & $psqlPath -U postgres -h localhost -f $sqlFile
    
    Write-Host "✓ Base de données créée avec succès" -ForegroundColor Green
    
    # Test de connexion avec le nouvel utilisateur
    Write-Host "2. Test de connexion..." -ForegroundColor Yellow
    $env:PGPASSWORD = $userPasswordPlain
    $testResult = & $psqlPath -U guineegest_user -h localhost -d guineegest_db -c "SELECT version()" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Connexion utilisateur réussie" -ForegroundColor Green
    } else {
        Write-Host "✗ Erreur de connexion utilisateur" -ForegroundColor Red
        Write-Host $testResult
    }
    
} catch {
    Write-Host "✗ Erreur lors de la création: $_" -ForegroundColor Red
    exit 1
} finally {
    # Nettoyer les variables d'environnement
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    Remove-Item $sqlFile -ErrorAction SilentlyContinue
}

Write-Host "3. Création du fichier .env..." -ForegroundColor Yellow

# Générer une clé secrète Django
$secretKey = -join ((1..50) | ForEach-Object {Get-Random -input ([char[]]"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*")})

# Créer le fichier .env
$envContent = @"
# Configuration PostgreSQL pour GuinéeGest
DJANGO_SECRET_KEY=$secretKey
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

# PostgreSQL Database Configuration
DJANGO_DB_ENGINE=django.db.backends.postgresql
DJANGO_DB_NAME=guineegest_db
DJANGO_DB_USER=guineegest_user
DJANGO_DB_PASSWORD=$userPasswordPlain
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432
"@

$envFile = "c:\Users\faral\Desktop\Gestion_parck\.env"
$envContent | Out-File -FilePath $envFile -Encoding UTF8

Write-Host "Fichier .env cree" -ForegroundColor Green

Write-Host "`n=== Prochaines etapes ===" -ForegroundColor Green
Write-Host "1. Activez votre environnement virtuel: .venv\Scripts\activate"
Write-Host "2. Installez les dependances: pip install -r requirements.txt"
Write-Host "3. Appliquez les migrations: python manage.py migrate"
Write-Host "4. Testez la connexion: python test_postgresql_connection.py"

Write-Host "`nConfiguration terminee !" -ForegroundColor Green
