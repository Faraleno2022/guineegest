# Migration pour ajouter le champ code_acces au modèle FournisseurVehicule
# À créer avec: python manage.py makemigrations

from django.db import migrations, models
import secrets

def generate_codes(apps, schema_editor):
    """Générer des codes d'accès pour les fournisseurs existants"""
    FournisseurVehicule = apps.get_model('fleet_app', 'FournisseurVehicule')
    
    for fournisseur in FournisseurVehicule.objects.all():
        if not fournisseur.code_acces:
            # Générer un code unique de 12 caractères
            fournisseur.code_acces = secrets.token_urlsafe(12)
            fournisseur.save()

class Migration(migrations.Migration):

    dependencies = [
        ('fleet_app', 'XXXX_previous_migration'),  # Remplacer par la dernière migration
    ]

    operations = [
        migrations.AddField(
            model_name='fournisseurvehicule',
            name='code_acces',
            field=models.CharField(
                max_length=20,
                unique=True,
                blank=True,
                null=True,
                help_text="Code d'accès unique pour la page publique"
            ),
        ),
        migrations.RunPython(generate_codes),
    ]
