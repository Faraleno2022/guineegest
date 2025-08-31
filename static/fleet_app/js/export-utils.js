/**
 * Utilitaires pour l'exportation des données des tableaux KPI
 */

// Fonction pour exporter un tableau en Excel
function exportTableToExcel(tableId, filename = 'export') {
    const table = document.getElementById(tableId);
    const ws = XLSX.utils.table_to_sheet(table);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Données");
    XLSX.writeFile(wb, `${filename}.xlsx`);
}

// Fonction pour exporter un tableau en PDF
function exportTableToPDF(tableId, filename = 'export') {
    const table = document.getElementById(tableId);
    
    // Configuration pour html2pdf
    const opt = {
        margin: 1,
        filename: `${filename}.pdf`,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'cm', format: 'a4', orientation: 'landscape' }
    };
    
    // Créer un élément temporaire pour l'export
    const element = document.createElement('div');
    element.innerHTML = `<h2>${filename}</h2>`;
    element.appendChild(table.cloneNode(true));
    
    // Générer le PDF
    html2pdf().set(opt).from(element).save();
}

// Fonction pour confirmer la suppression
function confirmDelete(url, itemName) {
    if (confirm(`Êtes-vous sûr de vouloir supprimer ${itemName} ?`)) {
        window.location.href = url;
    }
}
