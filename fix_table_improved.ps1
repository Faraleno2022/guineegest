$filePath = "c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\presence_journaliere_list.html"
$replacementPath = "c:\Users\faral\Desktop\Gestion_parck\fixed_table_complete.html"

# Lire le contenu du fichier original
$content = Get-Content -Path $filePath -Raw

# Lire le contenu de remplacement
$replacement = Get-Content -Path $replacementPath -Raw

# Définir les marqueurs de début et de fin pour la section à remplacer
$startMarker = '<div class="table-wrapper">'
$endMarker = '</div>\s*<!-- Script pour appliquer un statut'

# Trouver l'index de début
$startIndex = $content.IndexOf($startMarker)
if ($startIndex -eq -1) {
    Write-Host "Marqueur de début non trouvé"
    exit 1
}

# Trouver l'index de fin en utilisant une expression régulière
$regex = [regex]::new($endMarker)
$match = $regex.Match($content, $startIndex)
if (-not $match.Success) {
    Write-Host "Marqueur de fin non trouvé"
    exit 1
}
$endIndex = $match.Index

# Extraire les parties avant et après
$before = $content.Substring(0, $startIndex)
$after = $content.Substring($endIndex)

# Créer le nouveau contenu
$newContent = $before + $replacement + $after

# Écrire le nouveau contenu dans le fichier
Set-Content -Path $filePath -Value $newContent

Write-Host "Remplacement effectué avec succès"
