from django.apps import AppConfig


class FleetAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fleet_app'
    
    def ready(self):
        """Activation des signaux pour la synchronisation automatique"""
        try:
            import fleet_app.signals
            print("SYNC: Signaux de synchronisation automatique actives")
        except ImportError as e:
            print(f"SYNC ERROR: Impossible d'importer les signaux - {e}")
