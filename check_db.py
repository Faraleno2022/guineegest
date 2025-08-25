import os
import sqlite3
import django

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from fleet_app.models import DistanceParcourue, ConsommationCarburant, DisponibiliteVehicule, UtilisationVehicule, CoutFonctionnement, CoutFinancier, Vehicule

def check_table_exists(cursor, table_name):
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
    return cursor.fetchone() is not None

def print_tables(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in database:")
    for table in tables:
        print(f"- {table[0]}")

def create_table_from_model(cursor, model_class, table_name):
    print(f"Creating table {table_name}...")
    
    # Obtenir les champs du modèle
    fields = []
    for field in model_class._meta.fields:
        field_name = field.name
        field_type = field.get_internal_type()
        
        # Convertir les types Django en types SQLite
        if field_type == 'AutoField' or field_type == 'BigAutoField':
            fields.append(f'"{field_name}" integer NOT NULL PRIMARY KEY AUTOINCREMENT')
        elif field_type == 'CharField' or field_type == 'TextField':
            max_length = getattr(field, 'max_length', None)
            if max_length:
                fields.append(f'"{field_name}" varchar({max_length}) {"NOT NULL" if not field.null else "NULL"}')
            else:
                fields.append(f'"{field_name}" text {"NOT NULL" if not field.null else "NULL"}')
        elif field_type == 'IntegerField':
            fields.append(f'"{field_name}" integer {"NOT NULL" if not field.null else "NULL"}')
        elif field_type == 'FloatField' or field_type == 'DecimalField':
            fields.append(f'"{field_name}" real {"NOT NULL" if not field.null else "NULL"}')
        elif field_type == 'DateField' or field_type == 'DateTimeField':
            fields.append(f'"{field_name}" date {"NOT NULL" if not field.null else "NULL"}')
        elif field_type == 'BooleanField':
            fields.append(f'"{field_name}" boolean {"NOT NULL" if not field.null else "NULL"}')
        elif field_type == 'ForeignKey':
            related_model = field.related_model
            related_table = related_model._meta.db_table
            related_pk = related_model._meta.pk.name
            fields.append(f'"{field_name}_id" varchar(20) {"NOT NULL" if not field.null else "NULL"} REFERENCES "{related_table}" ("{related_pk}")')
    
    # Créer la table
    create_query = f'CREATE TABLE IF NOT EXISTS "{table_name}" (\n    ' + ',\n    '.join(fields) + '\n);'
    print(create_query)
    cursor.execute(create_query)

def main():
    # Connexion à la base de données
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Afficher toutes les tables existantes
    print_tables(cursor)
    
    # Vérifier et créer les tables manquantes
    models_to_check = [
        (DistanceParcourue, 'fleet_app_distanceparcourue'),
        (ConsommationCarburant, 'fleet_app_consommationcarburant'),
        (DisponibiliteVehicule, 'fleet_app_disponibilitevehicule'),
        (UtilisationVehicule, 'fleet_app_utilisationvehicule'),
        (CoutFonctionnement, 'fleet_app_coutfonctionnement'),
        (CoutFinancier, 'fleet_app_coutfinancier')
    ]
    
    for model_class, table_name in models_to_check:
        if not check_table_exists(cursor, table_name):
            print(f"Table {table_name} does not exist. Creating...")
            create_table_from_model(cursor, model_class, table_name)
        else:
            print(f"Table {table_name} already exists.")
    
    # Vérifier la table Vehicule
    vehicule_table = 'fleet_app_vehicule'
    if not check_table_exists(cursor, vehicule_table):
        print(f"WARNING: Main table {vehicule_table} does not exist!")
    else:
        print(f"Main table {vehicule_table} exists.")
    
    # Valider les changements et fermer la connexion
    conn.commit()
    conn.close()
    
    print("Database check and table creation completed.")

if __name__ == "__main__":
    main()
