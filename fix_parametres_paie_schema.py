import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.db import connection

def check_and_fix_parametres_paie():
    cursor = connection.cursor()
    
    # Check current schema
    cursor.execute("PRAGMA table_info('ParametresPaie')")
    columns = cursor.fetchall()
    
    print("Current ParametresPaie columns:")
    column_names = []
    for col in columns:
        print(f"  {col[1]} ({col[2]})")
        column_names.append(col[1])
    
    # Check if 'nom' column exists
    if 'nom' not in column_names:
        print("\n❌ Missing 'nom' column - adding it now...")
        
        # Add the missing nom column
        cursor.execute("ALTER TABLE ParametresPaie ADD COLUMN nom varchar(100)")
        
        # Update existing rows to have a default nom value based on cle
        cursor.execute("UPDATE ParametresPaie SET nom = COALESCE(cle, 'Paramètre') WHERE nom IS NULL")
        
        print("✅ Added 'nom' column and updated existing rows")
    else:
        print("\n✅ 'nom' column already exists")
    
    # Verify the fix
    cursor.execute("PRAGMA table_info('ParametresPaie')")
    columns_after = cursor.fetchall()
    
    print("\nFinal ParametresPaie schema:")
    for col in columns_after:
        print(f"  {col[1]} ({col[2]})")
    
    print("\n🎉 Schema check and fix completed!")

if __name__ == "__main__":
    check_and_fix_parametres_paie()
