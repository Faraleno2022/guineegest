$(document).ready(function() {
    // Initialisation de DataTables avec la nouvelle structure
    var table = $('#facturesTable').DataTable({
        language: {
            url: '//cdn.datatables.net/plug-ins/1.11.5/i18n/fr-FR.json'
        },
        responsive: true,
        order: [[1, 'desc']], // Tri par date d'émission décroissante
        columnDefs: [
            { targets: 0, width: '10%' }, // N° Facture
            { targets: 1, width: '10%' }, // Date émission
            { targets: 2, width: '20%' }, // Client/Fournisseur
            { targets: 3, width: '10%' }, // Type
            { targets: 4, width: '15%', className: 'text-end' }, // Montant TTC
            { targets: 5, width: '10%' }, // Statut
            { targets: 6, width: '15%', orderable: false } // Actions
        ],
        dom: 'Bfrtip',
        buttons: [
            {
                extend: 'excel',
                text: '<i class="fas fa-file-excel"></i> Excel',
                className: 'btn btn-success btn-sm',
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5]
                }
            },
            {
                extend: 'pdf',
                text: '<i class="fas fa-file-pdf"></i> PDF',
                className: 'btn btn-danger btn-sm',
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5]
                }
            },
            {
                extend: 'print',
                text: '<i class="fas fa-print"></i> Imprimer',
                className: 'btn btn-secondary btn-sm',
                exportOptions: {
                    columns: [0, 1, 2, 3, 4, 5]
                }
            }
        ],
        lengthMenu: [[10, 25, 50, -1], [10, 25, 50, "Tous"]],
        pageLength: 25
    });

    // Initialisation des tooltips Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Animation pour la facture nouvellement créée
    if ($('#newly-created-facture').length) {
        $('#newly-created-facture').addClass('animate__animated animate__pulse');
        setTimeout(function() {
            $('#newly-created-facture').removeClass('animate__animated animate__pulse');
        }, 3000);
    }

    // Validation du formulaire de suppression de toutes les factures
    $('#deleteAllFacturesForm').on('submit', function(e) {
        var confirmation = $('#confirmationInput').val();
        if (confirmation !== 'SUPPRIMER_TOUT') {
            e.preventDefault();
            alert("Veuillez saisir exactement 'SUPPRIMER_TOUT' pour confirmer la suppression.");
        }
    });
});
