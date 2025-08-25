/**
 * Système de connexion logique inter-modules
 * Partage la période (mois/année) entre tous les modules de gestion
 * Navigation manuelle uniquement - pas de synchronisation automatique
 * 
 * Modules concernés :
 * - pointage/ (management/presences/)
 * - paies/ (management/paies/)
 * - heures-supplementaires/ (management/heures-supplementaires/)
 * - parametres-paie/ (management/parametres-paie/)
 * - bulletins-paie/ (management/bulletins-paie/)
 * - archivage-mensuel/ (management/archivage-mensuel/)
 */

class ConnexionModules {
    constructor() {
        this.currentMonth = new Date().getMonth() + 1; // 1-12
        this.currentYear = new Date().getFullYear();
        this.modules = [
            'pointage',
            'paies',
            'heures-supplementaires',
            'parametres-paie',
            'bulletins-paie',
            'archivage-mensuel'
        ];
        
        // URLs de base pour chaque module
        this.moduleUrls = {
            'pointage': '/management/presences/',
            'paies': '/management/paies/',
            'heures-supplementaires': '/management/heures-supplementaires/',
            'parametres-paie': '/management/parametres-paie/',
            'bulletins-paie': '/management/bulletins-paie/',
            'archivage-mensuel': '/management/archivage-mensuel/'
        };
        
        this.init();
    }
    
    init() {
        console.log('🔗 Initialisation de la connexion logique inter-modules');
        
        // Récupérer le mois/année depuis l'URL ou le localStorage
        this.loadCurrentPeriod();
        
        // Créer le sélecteur de période global
        this.createGlobalPeriodSelector();
        
        // Écouter les changements de période (navigation manuelle uniquement)
        this.setupEventListeners();
        
        // Mettre à jour les liens de navigation
        this.updateNavigationLinks();
        
        console.log(`📅 Période actuelle : ${this.currentMonth}/${this.currentYear}`);
    }
    
    loadCurrentPeriod() {
        // Essayer de récupérer depuis l'URL
        const urlParams = new URLSearchParams(window.location.search);
        const urlMonth = urlParams.get('mois') || urlParams.get('month');
        const urlYear = urlParams.get('annee') || urlParams.get('year');
        
        if (urlMonth && urlYear) {
            this.currentMonth = parseInt(urlMonth);
            this.currentYear = parseInt(urlYear);
        } else {
            // Récupérer depuis le localStorage
            const savedPeriod = localStorage.getItem('management_period');
            if (savedPeriod) {
                const period = JSON.parse(savedPeriod);
                this.currentMonth = period.month;
                this.currentYear = period.year;
            }
        }
        
        // Sauvegarder dans le localStorage
        this.savePeriod();
    }
    
    savePeriod() {
        const period = {
            month: this.currentMonth,
            year: this.currentYear,
            timestamp: Date.now()
        };
        localStorage.setItem('management_period', JSON.stringify(period));
        
        // Déclencher un événement personnalisé
        window.dispatchEvent(new CustomEvent('periodChanged', {
            detail: period
        }));
    }
    
    createGlobalPeriodSelector() {
        // Vérifier si le sélecteur existe déjà
        if (document.getElementById('global-period-selector')) {
            return;
        }
        
        // Créer le conteneur du sélecteur
        const selectorHtml = `
            <div id="global-period-selector" class="card mb-3">
                <div class="card-body py-2">
                    <div class="row align-items-center">
                        <div class="col-auto">
                            <i class="fas fa-calendar-alt text-primary"></i>
                            <strong>Période :</strong>
                        </div>
                        <div class="col-auto">
                            <select id="period-month" class="form-select form-select-sm">
                                <option value="1">Janvier</option>
                                <option value="2">Février</option>
                                <option value="3">Mars</option>
                                <option value="4">Avril</option>
                                <option value="5">Mai</option>
                                <option value="6">Juin</option>
                                <option value="7">Juillet</option>
                                <option value="8">Août</option>
                                <option value="9">Septembre</option>
                                <option value="10">Octobre</option>
                                <option value="11">Novembre</option>
                                <option value="12">Décembre</option>
                            </select>
                        </div>
                        <div class="col-auto">
                            <select id="period-year" class="form-select form-select-sm">
                                ${this.generateYearOptions()}
                            </select>
                        </div>
                        <div class="col-auto">
                            <button id="apply-period" class="btn btn-primary btn-sm">
                                <i class="fas fa-sync-alt me-1"></i>Synchroniser
                            </button>
                        </div>
                        <div class="col-auto">
                            <button id="prev-month" class="btn btn-outline-secondary btn-sm" title="Mois précédent">
                                <i class="fas fa-chevron-left"></i>
                            </button>
                            <button id="next-month" class="btn btn-outline-secondary btn-sm" title="Mois suivant">
                                <i class="fas fa-chevron-right"></i>
                            </button>
                        </div>
                        <div class="col">
                            <div id="sync-status" class="text-muted small">
                                <i class="fas fa-check-circle text-success"></i>
                                Modules synchronisés
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Insérer le sélecteur au début du contenu principal
        const mainContent = document.querySelector('.container-fluid, .container, main, .content');
        if (mainContent) {
            mainContent.insertAdjacentHTML('afterbegin', selectorHtml);
            
            // Définir les valeurs actuelles
            document.getElementById('period-month').value = this.currentMonth;
            document.getElementById('period-year').value = this.currentYear;
        }
    }
    
    generateYearOptions() {
        const currentYear = new Date().getFullYear();
        let options = '';
        
        for (let year = currentYear - 2; year <= currentYear + 2; year++) {
            const selected = year === this.currentYear ? 'selected' : '';
            options += `<option value="${year}" ${selected}>${year}</option>`;
        }
        
        return options;
    }
    
    setupEventListeners() {
        // Boutons navigation mois (navigation manuelle)
        document.addEventListener('click', (e) => {
            if (e.target.id === 'prev-month' || e.target.closest('#prev-month')) {
                this.navigateMonth(-1);
            } else if (e.target.id === 'next-month' || e.target.closest('#next-month')) {
                this.navigateMonth(1);
            }
        });
        
        // Changement de sélecteurs (mise à jour manuelle uniquement)
        document.addEventListener('change', (e) => {
            if (e.target.id === 'period-month' || e.target.id === 'period-year') {
                // Sauvegarder la nouvelle période sans synchronisation automatique
                this.currentMonth = parseInt(document.getElementById('period-month').value);
                this.currentYear = parseInt(document.getElementById('period-year').value);
                this.savePeriod();
                this.updateNavigationLinks();
            }
        });
        
        // Écouter les événements de changement de période
        window.addEventListener('periodChanged', (e) => {
            this.updatePeriodSelectors();
        });
    }
    
    applyPeriodChange() {
        const monthSelect = document.getElementById('period-month');
        const yearSelect = document.getElementById('period-year');
        
        if (monthSelect && yearSelect) {
            this.currentMonth = parseInt(monthSelect.value);
            this.currentYear = parseInt(yearSelect.value);
            
            this.savePeriod();
            this.syncAllModules();
            
            console.log(`📅 Période changée : ${this.currentMonth}/${this.currentYear}`);
        }
    }
    
    navigateMonth(direction) {
        let newMonth = this.currentMonth + direction;
        let newYear = this.currentYear;
        
        if (newMonth < 1) {
            newMonth = 12;
            newYear--;
        } else if (newMonth > 12) {
            newMonth = 1;
            newYear++;
        }
        
        this.currentMonth = newMonth;
        this.currentYear = newYear;
        
        this.updatePeriodSelectors();
        this.savePeriod();
        
        // Navigation manuelle : rediriger vers le module actuel avec la nouvelle période
        this.navigateToCurrentModule();
    }
    
    updatePeriodSelectors() {
        const monthSelect = document.getElementById('period-month');
        const yearSelect = document.getElementById('period-year');
        
        if (monthSelect) monthSelect.value = this.currentMonth;
        if (yearSelect) yearSelect.value = this.currentYear;
    }
    
    navigateToCurrentModule() {
        // Déterminer le module actuel depuis l'URL
        const currentPath = window.location.pathname;
        const currentModule = this.getCurrentModule(currentPath);
        
        if (currentModule) {
            console.log(`🔗 Navigation vers ${currentModule} pour ${this.currentMonth}/${this.currentYear}`);
            
            // Construire l'URL avec les nouveaux paramètres
            const currentUrl = new URL(window.location);
            currentUrl.searchParams.set('mois', this.currentMonth);
            currentUrl.searchParams.set('annee', this.currentYear);
            
            // Rediriger vers la nouvelle URL
            window.location.href = currentUrl.toString();
        }
    }
    
    syncCurrentModule() {
        // Déterminer le module actuel depuis l'URL
        const currentPath = window.location.pathname;
        const currentModule = this.getCurrentModule(currentPath);
        
        if (currentModule) {
            console.log(`🔄 Synchronisation du module : ${currentModule}`);
            
            // Recharger la page avec les nouveaux paramètres
            const newUrl = this.buildModuleUrl(currentModule);
            
            // Utiliser pushState pour éviter le rechargement complet
            const urlParams = new URLSearchParams(window.location.search);
            urlParams.set('mois', this.currentMonth);
            urlParams.set('annee', this.currentYear);
            
            const newFullUrl = `${window.location.pathname}?${urlParams.toString()}`;
            window.history.pushState({}, '', newFullUrl);
            
            // Déclencher le rechargement des données via AJAX si possible
            this.reloadModuleData(currentModule);
        }
    }
    
    getCurrentModule(path) {
        for (const [module, url] of Object.entries(this.moduleUrls)) {
            if (path.includes(url.replace('/management/', '')) || path.includes(url)) {
                return module;
            }
        }
        return null;
    }
    
    buildModuleUrl(module) {
        const baseUrl = this.moduleUrls[module];
        return `${baseUrl}?mois=${this.currentMonth}&annee=${this.currentYear}`;
    }
    
    updateNavigationLinks() {
        // Mettre à jour tous les liens de navigation vers les modules
        document.querySelectorAll('a[href*="/management/"]').forEach(link => {
            const href = link.getAttribute('href');
            const module = this.getCurrentModule(href);
            
            if (module) {
                const url = new URL(href, window.location.origin);
                url.searchParams.set('mois', this.currentMonth);
                url.searchParams.set('annee', this.currentYear);
                link.setAttribute('href', url.pathname + url.search);
            }
        });
    }
    
    reloadModuleData(module) {
        // Déclencher un événement personnalisé pour que chaque module puisse recharger ses données
        const event = new CustomEvent('moduleDataReload', {
            detail: {
                module: module,
                month: this.currentMonth,
                year: this.currentYear
            }
        });
        
        window.dispatchEvent(event);
        
        // Essayer de recharger les tableaux de données
        this.reloadDataTables();
    }
    
    reloadDataTables() {
        // Recharger les DataTables si présents
        if (typeof $ !== 'undefined' && $.fn.DataTable) {
            $('.table').each(function() {
                if ($.fn.DataTable.isDataTable(this)) {
                    $(this).DataTable().ajax.reload();
                }
            });
        }
        
        // Déclencher un rechargement de page si aucune méthode AJAX n'est disponible
        setTimeout(() => {
            if (document.querySelector('.table')) {
                window.location.reload();
            }
        }, 2000);
    }
    
    triggerModuleSync() {
        // Déclencher des événements spécifiques pour chaque module
        this.modules.forEach(module => {
            const event = new CustomEvent(`sync_${module}`, {
                detail: {
                    month: this.currentMonth,
                    year: this.currentYear
                }
            });
            window.dispatchEvent(event);
        });
    }
    
    updateSyncStatus(message, type = 'info') {
        const statusElement = document.getElementById('sync-status');
        if (statusElement) {
            const icons = {
                'success': 'fas fa-check-circle text-success',
                'warning': 'fas fa-sync-alt fa-spin text-warning',
                'error': 'fas fa-exclamation-triangle text-danger',
                'info': 'fas fa-info-circle text-info'
            };
            
            statusElement.innerHTML = `
                <i class="${icons[type]}"></i>
                ${message}
            `;
        }
    }
    
    // API publique pour les modules
    static getInstance() {
        if (!window.connexionModules) {
            window.connexionModules = new ConnexionModules();
        }
        return window.connexionModules;
    }
    
    static getCurrentPeriod() {
        const instance = ConnexionModules.getInstance();
        return {
            month: instance.currentMonth,
            year: instance.currentYear
        };
    }
    
    static setPeriod(month, year) {
        const instance = ConnexionModules.getInstance();
        instance.currentMonth = month;
        instance.currentYear = year;
        instance.savePeriod();
        instance.updateNavigationLinks();
    }
}

// Initialisation automatique
document.addEventListener('DOMContentLoaded', function() {
    // Attendre un peu pour que les autres scripts se chargent
    setTimeout(() => {
        ConnexionModules.getInstance();
    }, 500);
});

// Exporter pour utilisation globale
window.ConnexionModules = ConnexionModules;
// Compatibilité avec l'ancien nom
window.SynchronisationModules = ConnexionModules;
