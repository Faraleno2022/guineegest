from django.shortcuts import redirect
from django.contrib import messages
from django.db import connection
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
@require_POST
def force_delete_vehicule(request, id_vehicule):
    """
    Vue qui force la suppression d'un véhicule en contournant le système de suppression de Django.
    Cette vue utilise des requêtes SQL directes et désactive temporairement les contraintes de clé étrangère.
    """
    try:
        # Journaliser l'opération
        logger.info(f"Tentative de suppression forcée du véhicule {id_vehicule}")
        
        with connection.cursor() as cursor:
            # 1. Désactiver les contraintes de clé étrangère
            cursor.execute('PRAGMA foreign_keys = OFF;')
            logger.info("Contraintes de clé étrangère désactivées")
            
            # 2. Supprimer tous les enregistrements liés dans les tables identifiées
            tables_to_clean = [
                'DistancesParcourues',
                'ConsommationCarburant',
                'fleet_app_alerte',
                'DisponibiliteVehicule',
                'UtilisationActifs',
                'UtilisationsVehicules',
                'IncidentsSecurite',
                'FeuillesDeRoute',
                'DocumentsAdministratifs',
                'CoutsFonctionnement',
                'CoutsFinanciers'
            ]
            
            for table in tables_to_clean:
                try:
                    # Vérifier si la table existe
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if cursor.fetchone():
                        # Identifier la colonne qui référence le véhicule
                        cursor.execute(f"""
                            SELECT "from" FROM pragma_foreign_key_list('{table}') 
                            WHERE "table" = 'fleet_app_vehicule'
                        """)
                        result = cursor.fetchone()
                        if result:
                            column = result[0]
                            # Supprimer les enregistrements
                            logger.info(f"Suppression des enregistrements de {table} où {column}='{id_vehicule}'")
                            cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", [id_vehicule])
                except Exception as table_error:
                    logger.error(f"Erreur lors du nettoyage de la table {table}: {str(table_error)}")
            
            # 3. Supprimer également via des requêtes SQL directes pour les tables connues
            known_tables = [
                ('fleet_app_documentadministratif', 'vehicule_id'),
                ('fleet_app_distanceparcourue', 'vehicule_id'),
                ('fleet_app_consommationcarburant', 'vehicule_id'),
                ('fleet_app_disponibilitevehicule', 'vehicule_id'),
                ('fleet_app_utilisationactif', 'vehicule_id'),
                ('fleet_app_coutfonctionnement', 'vehicule_id'),
                ('fleet_app_coutfinancier', 'vehicule_id'),
                ('fleet_app_utilisationvehicule', 'vehicule_id'),
                ('fleet_app_feuillederoute', 'vehicule_id'),
                ('fleet_app_incidentsecurite', 'vehicule_id'),
                ('fleet_app_alerte', 'vehicule_id')
            ]
            
            for table, column in known_tables:
                try:
                    # Vérifier si la table existe
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if cursor.fetchone():
                        logger.info(f"Suppression des enregistrements de {table} où {column}='{id_vehicule}'")
                        cursor.execute(f"DELETE FROM {table} WHERE {column} = ?", [id_vehicule])
                except Exception as table_error:
                    logger.error(f"Erreur lors du nettoyage de la table {table}: {str(table_error)}")
            
            # 4. Rechercher et supprimer toutes les références au véhicule dans toutes les tables
            cursor.execute("""
                SELECT m.name as table_name, p."from" as column_name
                FROM sqlite_master m
                JOIN pragma_foreign_key_list(m.name) p ON p."table" = 'fleet_app_vehicule'
                WHERE m.type = 'table'
            """)
            
            foreign_keys = cursor.fetchall()
            for table_name, column_name in foreign_keys:
                try:
                    logger.info(f"Suppression des références dans {table_name}.{column_name} pour le véhicule {id_vehicule}")
                    cursor.execute(f"DELETE FROM {table_name} WHERE {column_name} = ?", [id_vehicule])
                except Exception as fk_error:
                    logger.error(f"Erreur lors de la suppression des références dans {table_name}: {str(fk_error)}")
            
            # 5. Supprimer le véhicule lui-même
            try:
                logger.info(f"Suppression du véhicule {id_vehicule}")
                cursor.execute("DELETE FROM fleet_app_vehicule WHERE id_vehicule = ?", [id_vehicule])
                
                # Vérifier si la suppression a réussi
                cursor.execute("SELECT COUNT(*) FROM fleet_app_vehicule WHERE id_vehicule = ?", [id_vehicule])
                if cursor.fetchone()[0] == 0:
                    logger.info(f"Véhicule {id_vehicule} supprimé avec succès")
                else:
                    logger.error(f"La suppression du véhicule {id_vehicule} a échoué")
                    messages.error(request, f"La suppression du véhicule {id_vehicule} a échoué pour une raison inconnue.")
                    return redirect('fleet_app:vehicule_detail', id_vehicule=id_vehicule)
            except Exception as delete_error:
                logger.error(f"Erreur lors de la suppression du véhicule {id_vehicule}: {str(delete_error)}")
                messages.error(request, f"Erreur lors de la suppression du véhicule : {str(delete_error)}")
                return redirect('fleet_app:vehicule_detail', id_vehicule=id_vehicule)
            
            # 6. Réactiver les contraintes de clé étrangère
            cursor.execute('PRAGMA foreign_keys = ON;')
            logger.info("Contraintes de clé étrangère réactivées")
        
        messages.success(request, f"Véhicule {id_vehicule} supprimé avec succès.")
        return redirect('fleet_app:vehicule_list')
    
    except Exception as e:
        logger.error(f"Erreur lors de la suppression forcée du véhicule {id_vehicule}: {str(e)}")
        messages.error(request, f"Erreur lors de la suppression du véhicule : {str(e)}")
        return redirect('fleet_app:vehicule_detail', id_vehicule=id_vehicule)
