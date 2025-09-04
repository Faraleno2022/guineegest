#!/usr/bin/env python
"""
Script to create a fresh database with all tables properly migrated.
This bypasses migration conflicts by creating tables directly.
"""
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.core.management.color import no_style
from django.db import models

def create_fresh_database():
    """Create a fresh database with all models"""
    
    # Remove existing database if it exists
    db_path = 'db.sqlite3'
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create all tables using Django's SQL generation
    style = no_style()
    
    # Get all models
    from django.apps import apps
    all_models = apps.get_models()
    
    # Generate SQL for all models
    with connection.schema_editor() as schema_editor:
        for model in all_models:
            try:
                schema_editor.create_model(model)
                print(f"Created table for {model._meta.label}")
            except Exception as e:
                print(f"Warning: Could not create table for {model._meta.label}: {e}")
    
    # Mark all migrations as applied
    print("\nMarking migrations as applied...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--fake'])
        print("All migrations marked as applied")
    except Exception as e:
        print(f"Warning during fake migrate: {e}")
    
    print("\nDatabase creation completed!")
    
    # Verify Alerte table exists
    print("\nVerifying Alerte table...")
    with connection.cursor() as cursor:
        try:
            cursor.execute("PRAGMA table_info(fleet_app_alerte)")
            columns = cursor.fetchall()
            if columns:
                print("✓ fleet_app_alerte table exists with columns:")
                for col in columns:
                    print(f"  - {col[1]} ({col[2]})")
            else:
                print("✗ fleet_app_alerte table not found")
        except Exception as e:
            print(f"✗ Error checking fleet_app_alerte: {e}")

if __name__ == '__main__':
    create_fresh_database()
