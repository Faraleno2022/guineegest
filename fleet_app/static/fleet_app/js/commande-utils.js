/**
 * Utilitaires JavaScript pour la gestion des commandes
 * 
 * Ce fichier contient des fonctions utilitaires pour améliorer l'expérience utilisateur
 * dans la gestion des commandes et des lignes de commande.
 */

// Fonction pour formater les nombres avec séparateur de milliers
function formatNumber(number) {
    return new Intl.NumberFormat('fr-FR').format(number);
}

// Fonction pour calculer le montant total d'une commande
function calculerMontantTotal(lignes) {
    let total = 0;
    lignes.forEach(ligne => {
        total += ligne.prix_total || (ligne.quantite * ligne.prix_unitaire);
    });
    return total;
}

// Fonction pour calculer le montant de la remise
function calculerMontantRemise(montantTotal, pourcentageRemise) {
    return (montantTotal * pourcentageRemise) / 100;
}

// Fonction pour calculer le montant final
function calculerMontantFinal(montantTotal, montantRemise) {
    return montantTotal - montantRemise;
}

// Fonction pour mettre à jour les totaux dans l'interface
function mettreAJourTotaux(montantTotal, pourcentageRemise, montantRemise, montantFinal) {
    // Mettre à jour les éléments HTML avec les valeurs calculées
    const montantTotalElement = document.getElementById('montantTotal');
    if (montantTotalElement) {
        montantTotalElement.textContent = formatNumber(montantTotal) + ' GNF';
    }
    
    const montantRemiseElement = document.getElementById('montantRemise');
    if (montantRemiseElement) {
        montantRemiseElement.textContent = formatNumber(montantRemise) + ' GNF';
    }
    
    const montantFinalElement = document.getElementById('montantFinal');
    if (montantFinalElement) {
        montantFinalElement.textContent = formatNumber(montantFinal) + ' GNF';
    }
    
    // Mettre à jour les champs cachés pour la soumission du formulaire si présents
    const montantTotalInput = document.querySelector('input[name="montant_total"]');
    if (montantTotalInput) {
        montantTotalInput.value = montantTotal;
    }
    
    const montantRemiseInput = document.querySelector('input[name="montant_remise"]');
    if (montantRemiseInput) {
        montantRemiseInput.value = montantRemise;
    }
    
    const montantFinalInput = document.querySelector('input[name="montant_final"]');
    if (montantFinalInput) {
        montantFinalInput.value = montantFinal;
    }
}

// Fonction pour récupérer les infos d'un produit via AJAX
function getProduitInfo(produitId, callback) {
    // Récupérer le token CSRF
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Effectuer la requête AJAX
    fetch('/inventaire/commandes/get-produit-info/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: `produit_id=${produitId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            callback(data);
        } else {
            console.error('Erreur lors de la récupération des informations du produit:', data.error);
        }
    })
    .catch(error => {
        console.error('Erreur lors de la requête AJAX:', error);
    });
}

// Fonction pour ajouter une nouvelle ligne de commande dynamiquement
function ajouterLigneCommande(container, index, produitOptions) {
    const newRow = document.createElement('div');
    newRow.className = 'ligne-commande row mb-3 align-items-center';
    newRow.dataset.index = index;
    
    newRow.innerHTML = `
        <div class="col-md-4">
            <select name="lignes[${index}][produit]" class="form-select produit-select" required>
                <option value="">Sélectionner un produit</option>
                ${produitOptions}
            </select>
        </div>
        <div class="col-md-2">
            <input type="text" name="lignes[${index}][nom_produit]" class="form-control nom-produit" readonly>
        </div>
        <div class="col-md-2">
            <input type="number" name="lignes[${index}][quantite]" class="form-control quantite" min="1" required value="1">
        </div>
        <div class="col-md-2">
            <input type="number" name="lignes[${index}][prix_unitaire]" class="form-control prix-unitaire" min="0" required>
        </div>
        <div class="col-md-1">
            <span class="prix-total">0 GNF</span>
        </div>
        <div class="col-md-1">
            <button type="button" class="btn btn-danger btn-sm supprimer-ligne">
                <i class="fas fa-trash"></i>
            </button>
        </div>
    `;
    
    // Ajouter la nouvelle ligne au conteneur
    container.appendChild(newRow);
    
    // Configurer les événements pour la nouvelle ligne
    const produitSelect = newRow.querySelector('.produit-select');
    const quantiteInput = newRow.querySelector('.quantite');
    const prixUnitaireInput = newRow.querySelector('.prix-unitaire');
    const nomProduitInput = newRow.querySelector('.nom-produit');
    const prixTotalSpan = newRow.querySelector('.prix-total');
    const supprimerBtn = newRow.querySelector('.supprimer-ligne');
    
    // Événement de changement de produit
    produitSelect.addEventListener('change', function() {
        const produitId = this.value;
        if (produitId) {
            getProduitInfo(produitId, function(data) {
                nomProduitInput.value = data.nom_produit;
                prixUnitaireInput.value = data.prix_unitaire;
                
                // Calculer et mettre à jour le prix total
                const quantite = parseInt(quantiteInput.value) || 0;
                const prixUnitaire = parseFloat(prixUnitaireInput.value) || 0;
                const prixTotal = quantite * prixUnitaire;
                prixTotalSpan.textContent = formatNumber(prixTotal) + ' GNF';
                
                // Mettre à jour les totaux de la commande
                mettreAJourTotauxCommande();
            });
        } else {
            nomProduitInput.value = '';
            prixUnitaireInput.value = '';
            prixTotalSpan.textContent = '0 GNF';
            mettreAJourTotauxCommande();
        }
    });
    
    // Événements pour recalculer le prix total
    [quantiteInput, prixUnitaireInput].forEach(input => {
        input.addEventListener('input', function() {
            const quantite = parseInt(quantiteInput.value) || 0;
            const prixUnitaire = parseFloat(prixUnitaireInput.value) || 0;
            const prixTotal = quantite * prixUnitaire;
            prixTotalSpan.textContent = formatNumber(prixTotal) + ' GNF';
            
            // Mettre à jour les totaux de la commande
            mettreAJourTotauxCommande();
        });
    });
    
    // Événement pour supprimer la ligne
    supprimerBtn.addEventListener('click', function() {
        newRow.remove();
        mettreAJourTotauxCommande();
    });
    
    return newRow;
}

// Fonction pour mettre à jour les totaux de la commande
function mettreAJourTotauxCommande() {
    // Récupérer toutes les lignes de commande
    const lignes = document.querySelectorAll('.ligne-commande');
    let montantTotal = 0;
    
    // Calculer le montant total
    lignes.forEach(ligne => {
        const quantiteInput = ligne.querySelector('.quantite');
        const prixUnitaireInput = ligne.querySelector('.prix-unitaire');
        
        if (quantiteInput && prixUnitaireInput) {
            const quantite = parseInt(quantiteInput.value) || 0;
            const prixUnitaire = parseFloat(prixUnitaireInput.value) || 0;
            montantTotal += quantite * prixUnitaire;
            
            // Mettre à jour le prix total de la ligne si l'élément existe
            const prixTotalElement = ligne.querySelector('.prix-total');
            if (prixTotalElement) {
                prixTotalElement.textContent = formatNumber(quantite * prixUnitaire) + ' GNF';
            }
        }
    });
    
    // Récupérer le pourcentage de remise
    const remiseInput = document.getElementById('id_remise');
    const pourcentageRemise = remiseInput ? (parseFloat(remiseInput.value) || 0) : 0;
    
    // Calculer les montants
    const montantRemise = calculerMontantRemise(montantTotal, pourcentageRemise);
    const montantFinal = calculerMontantFinal(montantTotal, montantRemise);
    
    // Mettre à jour l'affichage
    mettreAJourTotaux(montantTotal, pourcentageRemise, montantRemise, montantFinal);
    
    // Log pour débogage
    console.log('Montants calculés:', {
        montantTotal: montantTotal,
        pourcentageRemise: pourcentageRemise,
        montantRemise: montantRemise,
        montantFinal: montantFinal
    });
}

// Fonction d'initialisation pour le formulaire de commande dynamique
function initCommandeForm() {
    console.log('Initialisation du formulaire de commande dynamique');
    const container = document.getElementById('lignes-container');
    const ajouterBtn = document.getElementById('ajouter-ligne');
    const produitOptions = document.getElementById('produit-options') ? document.getElementById('produit-options').innerHTML : '';
    let index = document.querySelectorAll('.ligne-commande').length;
    
    // Événement pour ajouter une nouvelle ligne
    if (ajouterBtn) {
        ajouterBtn.addEventListener('click', function() {
            ajouterLigneCommande(container, index++, produitOptions);
        });
    }
    
    // Configurer les événements pour les lignes existantes
    document.querySelectorAll('.ligne-commande').forEach(ligne => {
        const produitSelect = ligne.querySelector('.produit-select');
        const quantiteInput = ligne.querySelector('.quantite');
        const prixUnitaireInput = ligne.querySelector('.prix-unitaire');
        const nomProduitInput = ligne.querySelector('.nom-produit');
        const prixTotalSpan = ligne.querySelector('.prix-total');
        const supprimerBtn = ligne.querySelector('.supprimer-ligne');
        
        // Événement de changement de produit
        if (produitSelect) {
            produitSelect.addEventListener('change', function() {
                const produitId = this.value;
                if (produitId) {
                    getProduitInfo(produitId, function(data) {
                        if (nomProduitInput) nomProduitInput.value = data.nom_produit;
                        if (prixUnitaireInput) prixUnitaireInput.value = data.prix_unitaire;
                        
                        // Calculer et mettre à jour le prix total
                        const quantite = quantiteInput ? (parseInt(quantiteInput.value) || 0) : 0;
                        const prixUnitaire = parseFloat(data.prix_unitaire) || 0;
                        const prixTotal = quantite * prixUnitaire;
                        if (prixTotalSpan) prixTotalSpan.textContent = formatNumber(prixTotal) + ' GNF';
                        
                        // Mettre à jour les totaux de la commande
                        mettreAJourTotauxCommande();
                    });
                } else {
                    if (nomProduitInput) nomProduitInput.value = '';
                    if (prixUnitaireInput) prixUnitaireInput.value = '';
                    if (prixTotalSpan) prixTotalSpan.textContent = '0 GNF';
                    mettreAJourTotauxCommande();
                }
            });
        }
        
        // Événements pour recalculer le prix total
        [quantiteInput, prixUnitaireInput].forEach(input => {
            if (input) {
                input.addEventListener('input', function() {
                    const quantite = quantiteInput ? (parseInt(quantiteInput.value) || 0) : 0;
                    const prixUnitaire = prixUnitaireInput ? (parseFloat(prixUnitaireInput.value) || 0) : 0;
                    const prixTotal = quantite * prixUnitaire;
                    if (prixTotalSpan) prixTotalSpan.textContent = formatNumber(prixTotal) + ' GNF';
                    mettreAJourTotauxCommande();
                });
            }
        });
        
        // Événement pour supprimer la ligne
        if (supprimerBtn) {
            supprimerBtn.addEventListener('click', function() {
                ligne.remove();
                mettreAJourTotauxCommande();
            });
        }
    });
    
    // Événement pour la remise
    const remiseInput = document.getElementById('id_remise');
    if (remiseInput) {
        remiseInput.addEventListener('input', mettreAJourTotauxCommande);
    }
    
    // Initialiser les totaux
    setTimeout(function() {
        mettreAJourTotauxCommande();
        console.log('Totaux initialisés au chargement de la page');
    }, 100); // Petit délai pour s'assurer que tous les éléments sont chargés
}
