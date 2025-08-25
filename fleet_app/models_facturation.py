from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum
import os

class Facture(models.Model):
    """Modèle pour les factures"""
    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('validee', 'Validée'),
        ('envoyee', 'Envoyée'),
        ('payee', 'Payée'),
        ('annulee', 'Annulée'),
    ]
    
    # Informations générales
    numero = models.CharField(max_length=20, primary_key=True, verbose_name="Numéro")
    reference = models.CharField(max_length=50, blank=True, null=True, verbose_name="Référence")
    date_creation = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    date_emission = models.DateField(default=timezone.now, verbose_name="Date d'émission")
    date_echeance = models.DateField(null=True, blank=True, verbose_name="Date d'échéance")
    
    # Informations client/tiers
    tiers_nom = models.CharField(max_length=100, verbose_name="Nom/Société")
    tiers_adresse = models.TextField(blank=True, null=True, verbose_name="Adresse")
    tiers_telephone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Téléphone")
    tiers_email = models.EmailField(blank=True, null=True, verbose_name="Email")
    
    # Informations de paiement
    mode_paiement = models.CharField(max_length=50, default="Espèces", verbose_name="Mode de paiement")
    delai_paiement = models.CharField(max_length=50, default="À réception de facture", verbose_name="Délai de paiement")
    
    # Informations bancaires
    banque = models.CharField(max_length=100, blank=True, null=True, verbose_name="Banque")
    rib = models.CharField(max_length=50, blank=True, null=True, verbose_name="RIB")
    
    # Informations financières
    montant_total = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Montant total (GNF)")
    remise = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Remise (GNF)")
    tva = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="TVA (GNF)")
    montant_final = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Montant final (GNF)")
    
    # Statut et informations supplémentaires
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon', verbose_name="Statut")
    utilisateur = models.ForeignKey('auth.User', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Créé par")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Document signé joint
    def get_facture_upload_path(instance, filename):
        # Chemin de stockage: factures/NUMERO_FACTURE/filename
        return os.path.join('factures', instance.numero, filename)
        
    document_signe = models.FileField(upload_to=get_facture_upload_path, null=True, blank=True, verbose_name="Document signé")
    
    def __str__(self):
        return f"{self.numero} - {self.tiers_nom} ({self.montant_final} GNF)"
    
    def calculer_montants(self):
        """Calcule les montants de la facture à partir des lignes"""
        from decimal import Decimal
        
        total = self.lignes.aggregate(Sum('montant'))['montant__sum'] or 0
        self.montant_total = total
        
        # Calcul de la TVA (18%)
        self.tva = (self.montant_total - self.remise) * Decimal('0.18')
        
        # Calcul du montant final
        self.montant_final = self.montant_total - self.remise + self.tva
        self.save(update_fields=['montant_total', 'tva', 'montant_final'])
    
    def save(self, *args, **kwargs):
        # Si c'est une nouvelle facture, générer automatiquement un numéro
        if not self.numero:
            date_str = timezone.now().strftime('%Y%m')
            last_facture = Facture.objects.filter(numero__startswith=f"FG-{date_str}").order_by('numero').last()
            
            if last_facture:
                last_num = int(last_facture.numero.split('-')[-1])
                self.numero = f"FG-{date_str}-{last_num+1:03d}"
            else:
                self.numero = f"FG-{date_str}-001"
                
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Facture"
        verbose_name_plural = "Factures"
        ordering = ['-date_emission', 'numero']


class LigneFacture(models.Model):
    """Modèle pour les lignes de facture"""
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes', verbose_name="Facture")
    produit = models.ForeignKey('Produit', on_delete=models.PROTECT, null=True, blank=True, verbose_name="Produit")
    description = models.CharField(max_length=200, verbose_name="Description")
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Quantité")
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="Prix unitaire (GNF)")
    montant = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Montant (GNF)")
    
    def __str__(self):
        return f"{self.description} - {self.quantite} x {self.prix_unitaire} = {self.montant}"
    
    def save(self, *args, **kwargs):
        # Calculer le montant en convertissant explicitement les types
        from decimal import Decimal
        self.montant = Decimal(self.quantite) * self.prix_unitaire
        super().save(*args, **kwargs)
        
        # Mettre à jour les montants de la facture
        self.facture.calculer_montants()
    
    class Meta:
        verbose_name = "Ligne de facture"
        verbose_name_plural = "Lignes de facture"
        ordering = ['id']
