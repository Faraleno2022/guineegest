# Generated manually to add user fields to all models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fleet_app', '0009_alter_configurationsalaire_unique_together_and_more'),
    ]

    operations = [
        # Add user field to Vehicule if it doesn't exist
        migrations.AddField(
            model_name='vehicule',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
        
        # Add user field to Chauffeur if it doesn't exist
        migrations.AddField(
            model_name='chauffeur',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
        
        # Add user field to FeuilleDeRoute if it doesn't exist
        migrations.AddField(
            model_name='feuillederroute',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
        
        # Add user field to Alerte if it doesn't exist
        migrations.AddField(
            model_name='alerte',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
        
        # Add user field to CoutFonctionnement if it doesn't exist
        migrations.AddField(
            model_name='coutfonctionnement',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
        
        # Add user field to CoutFinancier if it doesn't exist
        migrations.AddField(
            model_name='coutfinancier',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
        
        # Add user field to UtilisationVehicule if it doesn't exist
        migrations.AddField(
            model_name='utilisationvehicule',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur'),
        ),
    ]
