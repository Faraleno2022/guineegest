from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db import connection
import logging

# Configuration du logger
logger = logging.getLogger(__name__)

@login_required
def check_model_relations(request, model_name, object_id):
    """
    Vue de diagnostic pour identifier les relations qui empêchent la suppression d'un objet.
    Cette vue analyse les contraintes de clé étrangère et identifie les enregistrements qui référencent l'objet.
    
    Args:
        model_name: Nom du modèle (ex: 'vehicule', 'chauffeur', 'disponibilitevehicule')
        object_id: ID de l'objet à vérifier
    
    Returns:
        JsonResponse avec les relations bloquantes
    """
    try:
        # Normaliser le nom du modèle pour correspondre aux conventions Django
        model_name_lower = model_name.lower()
        if not model_name_lower.startswith('fleet_app_'):
            model_name_normalized = f'fleet_app_{model_name_lower}'
        else:
            model_name_normalized = model_name_lower
            
        # Vérifier si la table existe
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{model_name_normalized}'")
            if not cursor.fetchone():
                # Essayer avec d'autres conventions de nommage
                alternative_names = [
                    model_name_lower,
                    model_name_lower.capitalize(),
                    f"{model_name_lower}s",
                    f"{model_name_lower.capitalize()}s"
                ]
                
                found = False
                for alt_name in alternative_names:
                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{alt_name}'")
                    if cursor.fetchone():
                        model_name_normalized = alt_name
                        found = True
                        break
                
                if not found:
                    return JsonResponse({'error': f'Table pour le modèle {model_name} non trouvée'}, status=404)
        
        # Identifier les tables qui référencent ce modèle
        with connection.cursor() as cursor:
            cursor.execute(f"""
                SELECT m.name as table_name, p."from" as from_column, p."to" as to_column
                FROM sqlite_master m
                JOIN pragma_foreign_key_list(m.name) p
                WHERE p."table" = '{model_name_normalized}'
            """)
            foreign_keys = cursor.fetchall()
        
        # Vérifier chaque table pour des références à l'objet
        blocking_relations = []
        for table_name, from_column, to_column in foreign_keys:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {from_column} = ?", [object_id])
                count = cursor.fetchone()[0]
                if count > 0:
                    # Récupérer des informations sur les enregistrements bloquants
                    cursor.execute(f"SELECT * FROM {table_name} WHERE {from_column} = ? LIMIT 5", [object_id])
                    columns = [col[0] for col in cursor.description]
                    records = [dict(zip(columns, row)) for row in cursor.fetchall()]
                    
                    blocking_relations.append({
                        'table': table_name,
                        'column': from_column,
                        'count': count,
                        'sample_records': records
                    })
        
        return JsonResponse({
            'model': model_name,
            'object_id': object_id,
            'blocking_relations': blocking_relations,
            'can_be_deleted': len(blocking_relations) == 0
        })
    except Exception as e:
        logger.error(f"Erreur lors de la vérification des relations pour {model_name} {object_id}: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def list_model_dependencies(request):
    """
    Vue qui liste toutes les dépendances entre les modèles de l'application.
    Cette vue est utile pour comprendre la structure des relations dans la base de données.
    
    Returns:
        JsonResponse avec la structure des dépendances entre modèles
    """
    try:
        # Récupérer toutes les tables
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
            tables = [row[0] for row in cursor.fetchall()]
        
        # Analyser les relations pour chaque table
        model_dependencies = {}
        for table in tables:
            with connection.cursor() as cursor:
                # Récupérer les clés étrangères sortantes (références vers d'autres tables)
                cursor.execute(f"""
                    SELECT p."table" as referenced_table, p."from" as from_column, p."to" as to_column
                    FROM pragma_foreign_key_list('{table}') p
                """)
                outgoing_relations = [
                    {
                        'referenced_table': row[0],
                        'from_column': row[1],
                        'to_column': row[2]
                    }
                    for row in cursor.fetchall()
                ]
                
                # Récupérer les clés étrangères entrantes (tables qui référencent cette table)
                incoming_relations = []
                for other_table in tables:
                    if other_table != table:
                        cursor.execute(f"""
                            SELECT p."from" as from_column, p."to" as to_column
                            FROM pragma_foreign_key_list('{other_table}') p
                            WHERE p."table" = '{table}'
                        """)
                        for row in cursor.fetchall():
                            incoming_relations.append({
                                'referencing_table': other_table,
                                'from_column': row[0],
                                'to_column': row[1]
                            })
                
                model_dependencies[table] = {
                    'outgoing_relations': outgoing_relations,
                    'incoming_relations': incoming_relations
                }
        
        return JsonResponse({
            'model_dependencies': model_dependencies
        })
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des dépendances entre modèles: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
