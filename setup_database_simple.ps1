# Script simple de configuration PostgreSQL pour GuinéeGest
Write-Host "=== Configuration Base de Donnees GuineeGest ===" -ForegroundColor Green

$psqlPath = "C:\Program Files\PostgreSQL\17\bin\psql.exe"

# Demander les mots de passe
$postgresPassword = Read-Host "Mot de passe du superutilisateur 'postgres'" -AsSecureString
$postgresPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($postgresPassword))

$userPassword = Read-Host "Mot de passe pour 'guineegest_user'" -AsSecureString  
$userPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($userPassword))

Write-Host "Creation de la base de donnees..." -ForegroundColor Yellow

# Script SQL
$sqlScript = @"
CREATE DATABASE guineegest_db;
CREATE USER guineegest_user WITH PASSWORD '$userPasswordPlain';
GRANT ALL PRIVILEGES ON DATABASE guineegest_db TO guineegest_user;
\c guineegest_db
GRANT ALL ON SCHEMA public TO guineegest_user;
GRANT CREATE ON SCHEMA public TO guineegest_user;
"@

$sqlFile = "$env:TEMP\setup_guineegest.sql"
$sqlScript | Out-File -FilePath $sqlFile -Encoding UTF8

try {
    $env:PGPASSWORD = $postgresPasswordPlain
    & $psqlPath -U postgres -h localhost -f $sqlFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Base de donnees creee avec succes" -ForegroundColor Green
        
        # Test connexion
        $env:PGPASSWORD = $userPasswordPlain
        & $psqlPath -U guineegest_user -h localhost -d guineegest_db -c "SELECT 1"
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Connexion utilisateur OK" -ForegroundColor Green
        }
    }
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
} finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
    Remove-Item $sqlFile -ErrorAction SilentlyContinue
}

# Créer fichier .env
Write-Host "Creation du fichier .env..." -ForegroundColor Yellow
$secretKey = -join ((1..50) | ForEach-Object {Get-Random -InputObject ([char[]]"abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")})

$envContent = @"
DJANGO_SECRET_KEY=$secretKey
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
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
Write-Host "Configuration terminee !" -ForegroundColor Green
