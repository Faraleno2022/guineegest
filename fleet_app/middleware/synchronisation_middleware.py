"""
Middleware de synchronisation inter-modules
Gère automatiquement les paramètres de mois/année entre tous les modules de gestion
"""

from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from datetime import datetime
import json


class SynchronisationMiddleware(MiddlewareMixin):
    """
    Middleware pour synchroniser automatiquement la navigation mois/année
    entre tous les modules de gestion
    """
    
    # Modules concernés par la synchronisation
    MODULES_SYNC = [
        'management_presence_list',
        'management_paie_list', 
        'management_heure_supplementaire_list',
        'management_parametre_paie_list',
        'management_bulletin_paie_list',
        'management_archivage_mensuel'
    ]
    
    # URLs de base pour chaque module
    MODULE_PATTERNS = [
        '/management/presences/',
        '/management/paies/',
        '/management/heures-supplementaires/',
        '/management/parametres-paie/',
        '/management/bulletins-paie/',
        '/management/archivage-mensuel/'
    ]
    
    def process_request(self, request):
        """
        Traite la requête entrante pour gérer la synchronisation
        """
        # Vérifier si c'est une URL de module de gestion
        if not self.is_management_url(request.path):
            return None
            
        # Récupérer ou initialiser la période
        period = self.get_or_set_period(request)
        
        # Ajouter la période au contexte de la requête
        request.sync_period = period
        
        return None
    
    def process_response(self, request, response):
        """
        Traite la réponse pour ajouter les informations de synchronisation
        """
        # Ajouter les headers de synchronisation
        if hasattr(request, 'sync_period'):
            response['X-Sync-Month'] = str(request.sync_period['month'])
            response['X-Sync-Year'] = str(request.sync_period['year'])
            
        return response
    
    def is_management_url(self, path):
        """
        Vérifie si l'URL fait partie des modules de gestion
        """
        return any(pattern in path for pattern in self.MODULE_PATTERNS)
    
    def get_or_set_period(self, request):
        """
        Récupère ou définit la période actuelle
        """
        # Priorité 1: Paramètres GET
        month = request.GET.get('mois') or request.GET.get('month')
        year = request.GET.get('annee') or request.GET.get('year')
        
        if month and year:
            try:
                period = {
                    'month': int(month),
                    'year': int(year)
                }
                # Sauvegarder en session
                request.session['management_period'] = period
                return period
            except (ValueError, TypeError):
                pass
        
        # Priorité 2: Session
        if 'management_period' in request.session:
            period = request.session['management_period']
            if self.is_valid_period(period):
                return period
        
        # Priorité 3: Valeurs par défaut (mois/année actuels)
        now = datetime.now()
        period = {
            'month': now.month,
            'year': now.year
        }
        
        request.session['management_period'] = period
        return period
    
    def is_valid_period(self, period):
        """
        Valide une période
        """
        if not isinstance(period, dict):
            return False
            
        month = period.get('month')
        year = period.get('year')
        
        if not isinstance(month, int) or not isinstance(year, int):
            return False
            
        return 1 <= month <= 12 and 2020 <= year <= 2030


class SynchronisationContextProcessor:
    """
    Processeur de contexte pour ajouter les informations de synchronisation
    aux templates
    """
    
    def __call__(self, request):
        """
        Ajoute les variables de synchronisation au contexte
        """
        context = {}
        
        # Ajouter la période actuelle
        if hasattr(request, 'sync_period'):
            context['sync_period'] = request.sync_period
        else:
            # Valeurs par défaut
            now = datetime.now()
            context['sync_period'] = {
                'month': now.month,
                'year': now.year
            }
        
        # Ajouter les informations de module
        context['sync_modules'] = {
            'current_module': self.get_current_module(request.path),
            'available_modules': self.get_available_modules(),
            'is_management_page': any(pattern in request.path 
                                    for pattern in SynchronisationMiddleware.MODULE_PATTERNS)
        }
        
        # Ajouter les noms de mois en français
        context['month_names'] = {
            1: 'Janvier', 2: 'Février', 3: 'Mars', 4: 'Avril',
            5: 'Mai', 6: 'Juin', 7: 'Juillet', 8: 'Août',
            9: 'Septembre', 10: 'Octobre', 11: 'Novembre', 12: 'Décembre'
        }
        
        return context
    
    def get_current_module(self, path):
        """
        Détermine le module actuel depuis le chemin
        """
        module_map = {
            '/management/presences/': 'pointage',
            '/management/paies/': 'paies',
            '/management/heures-supplementaires/': 'heures-supplementaires',
            '/management/parametres-paie/': 'parametres-paie',
            '/management/bulletins-paie/': 'bulletins-paie',
            '/management/archivage-mensuel/': 'archivage-mensuel'
        }
        
        for pattern, module in module_map.items():
            if pattern in path:
                return module
                
        return None
    
    def get_available_modules(self):
        """
        Retourne la liste des modules disponibles
        """
        return [
            {
                'name': 'pointage',
                'title': 'Pointage Journalier',
                'url': '/management/presences/',
                'icon': 'fas fa-clock'
            },
            {
                'name': 'paies',
                'title': 'Gestion des Paies',
                'url': '/management/paies/',
                'icon': 'fas fa-money-bill-wave'
            },
            {
                'name': 'heures-supplementaires',
                'title': 'Heures Supplémentaires',
                'url': '/management/heures-supplementaires/',
                'icon': 'fas fa-clock'
            },
            {
                'name': 'parametres-paie',
                'title': 'Paramètres de Paie',
                'url': '/management/parametres-paie/',
                'icon': 'fas fa-cog'
            },
            {
                'name': 'bulletins-paie',
                'title': 'Bulletins de Paie',
                'url': '/management/bulletins-paie/',
                'icon': 'fas fa-file-invoice'
            },
            {
                'name': 'archivage-mensuel',
                'title': 'Archivage Mensuel',
                'url': '/management/archivage-mensuel/',
                'icon': 'fas fa-archive'
            }
        ]


def synchronisation_context_processor(request):
    """
    Fonction de processeur de contexte pour la synchronisation
    """
    processor = SynchronisationContextProcessor()
    return processor(request)
