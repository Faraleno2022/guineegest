from django.shortcuts import render
from django.http import JsonResponse
from django.db import connection
from .models import Vehicule

def debug_vehicle_relations(request, id_vehicule):
    """
    Vue de débogage pour identifier les relations qui bloquent la suppression d'un véhicule.
    """
    try:
        vehicule = Vehicule.objects.get(pk=id_vehicule)
        
        # Récupérer toutes les tables qui référencent la table vehicule
        with connection.cursor() as cursor:
            # Cette requête SQL fonctionne pour SQLite
            cursor.execute("""
                SELECT m.name as table_name, p."from" as from_column, p."to" as to_column
                FROM sqlite_master m
                JOIN pragma_foreign_key_list(m.name) p
                WHERE p."table" = 'fleet_app_vehicule'
            """)
            foreign_keys = cursor.fetchall()
        
        # Vérifier chaque table pour des références au véhicule
        relations = []
        for table_name, from_column, to_column in foreign_keys:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {from_column} = %s", [id_vehicule])
                count = cursor.fetchone()[0]
                if count > 0:
                    relations.append({
                        'table': table_name,
                        'count': count,
                        'column': from_column
                    })
        
        return JsonResponse({
            'vehicule': id_vehicule,
            'blocking_relations': relations
        })
    except Vehicule.DoesNotExist:
        return JsonResponse({'error': f'Véhicule {id_vehicule} non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
