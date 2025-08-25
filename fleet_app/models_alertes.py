from django.db import models
from django.utils import timezone

class Alerte(models.Model):
    """
    Modèle pour gérer les alertes du système de gestion de parc automobile.
    Les alertes peuvent être liées à un véhicule ou être générales.
    """
    NIVEAU_CHOICES = [
        ('Faible', 'Faible'),
        ('Moyen', 'Moyen'),
        ('Élevé', 'Élevé'),
        ('Critique', 'Critique'),
    ]
    
    STATUT_CHOICES = [
        ('Active', 'Active'),
        ('Résolue', 'Résolue'),
        ('Ignorée', 'Ignorée'),
    ]
    
    titre = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='Moyen', verbose_name="Niveau d'urgence")
    vehicule = models.ForeignKey('fleet_app.Vehicule', on_delete=models.CASCADE, related_name='alertes', null=True, blank=True, verbose_name="Véhicule concerné")
    date_creation = models.DateTimeField(default=timezone.now, verbose_name="Date de création")
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='Active', verbose_name="Statut")
    resolution = models.TextField(blank=True, null=True, verbose_name="Résolution")
    date_resolution = models.DateTimeField(null=True, blank=True, verbose_name="Date de résolution")
    
    def __str__(self):
        return f"{self.titre} - {self.get_niveau_display()} - {self.get_statut_display()}"
    
    def save(self, *args, **kwargs):
        # Si l'alerte est marquée comme résolue et qu'aucune date de résolution n'est définie
        if self.statut == 'Résolue' and not self.date_resolution:
            self.date_resolution = timezone.now()
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Alerte"
        verbose_name_plural = "Alertes"
        ordering = ['-date_creation']
