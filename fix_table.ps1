$filePath = "c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\presence_journaliere_list.html"
$content = Get-Content -Path $filePath -Raw

# Définir le début et la fin de la section à remplacer
$startPattern = '<div class="table-wrapper">'
$endPattern = '</div><!-- Fin de la table-wrapper -->'

# Si le marqueur de fin n'existe pas, utiliser un autre point de repère
if ($content -notmatch $endPattern) {
    $endPattern = '</div>\s*</div>\s*<script>'
}

# Charger le contenu de remplacement
$part1 = Get-Content -Path "c:\Users\faral\Desktop\Gestion_parck\fixed_table_part1.html" -Raw
$part2 = Get-Content -Path "c:\Users\faral\Desktop\Gestion_parck\fixed_table_part2.html" -Raw
$replacement = $part1 + "`n" + $part2

# Trouver l'index de début
$startIndex = $content.IndexOf($startPattern)
if ($startIndex -eq -1) {
    Write-Host "Motif de début non trouvé"
    exit 1
}

# Chercher la fin en utilisant une expression régulière
$regex = [regex]::new($endPattern)
$match = $regex.Match($content, $startIndex)
if (-not $match.Success) {
    Write-Host "Motif de fin non trouvé"
    exit 1
}
$endIndex = $match.Index + $match.Length

# Extraire les parties avant et après
$before = $content.Substring(0, $startIndex)
$after = $content.Substring($endIndex)

# Créer le nouveau contenu
$newContent = $before + $replacement + $after

# Écrire le nouveau contenu dans le fichier
Set-Content -Path $filePath -Value $newContent

Write-Host "Remplacement effectué avec succès"
