from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db.models import Sum
import os

class Produit(models.Model):
    """Modèle pour les produits en inventaire"""
    CATEGORIE_CHOICES = [
        ('Alimentaire', 'Alimentaire'),
        ('Hygiène', 'Hygiène'),
        ('Fourniture', 'Fourniture'),
        ('Équipement', 'Équipement'),
        ('Pièce', 'Pièce détachée'),
        ('Autre', 'Autre'),
    ]
    
    UNITE_CHOICES = [
        ('Pièce', 'Pièce'),
        ('Carton', 'Carton'),
        ('Sac', 'Sac'),
        ('Kg', 'Kilogramme'),
        ('Litre', 'Litre'),
        ('Mètre', 'Mètre'),
        ('Autre', 'Autre'),
    ]
    
    id_produit = models.CharField(max_length=10, primary_key=True, verbose_name="ID Produit")
    nom = models.CharField(max_length=100, verbose_name="Nom du produit")
    categorie = models.CharField(max_length=50, choices=CATEGORIE_CHOICES, verbose_name="Catégorie")
    unite = models.CharField(max_length=20, choices=UNITE_CHOICES, verbose_name="Unité")
    seuil_minimum = models.PositiveIntegerField(default=0, verbose_name="Seuil minimum")
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="Prix unitaire (GNF)")
    fournisseur = models.CharField(max_length=100, verbose_name="Fournisseur")
    date_ajout = models.DateField(default=timezone.now, verbose_name="Date d'ajout")
    
    def __str__(self):
        return f"{self.id_produit} - {self.nom}"
    
    def get_stock_actuel(self):
        """Calcule le stock actuel du produit"""
        total_entrees = EntreeStock.objects.filter(produit=self).aggregate(Sum('quantite'))['quantite__sum'] or 0
        total_sorties = SortieStock.objects.filter(produit=self).aggregate(Sum('quantite'))['quantite__sum'] or 0
        return total_entrees - total_sorties
    
    def get_statut_alerte(self):
        """Détermine si le produit est en alerte de stock"""
        stock_actuel = self.get_stock_actuel()
        if stock_actuel <= self.seuil_minimum:
            return "ALERTE"
        return "OK"
    
    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['id_produit']


class EntreeStock(models.Model):
    """Modèle pour les entrées en stock"""
    id_entree = models.CharField(max_length=10, primary_key=True, verbose_name="ID Entrée")
    date = models.DateField(default=timezone.now, verbose_name="Date d'entrée")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='entrees', verbose_name="Produit")
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Quantité entrée")
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="Prix unitaire (GNF)")
    fournisseur = models.CharField(max_length=100, verbose_name="Fournisseur")
    reference_facture = models.CharField(max_length=20, verbose_name="Référence facture")
    stock_avant = models.PositiveIntegerField(default=0, verbose_name="Stock avant")
    stock_apres = models.PositiveIntegerField(default=0, verbose_name="Stock après")
    
    def __str__(self):
        return f"{self.id_entree} - {self.produit.nom} ({self.quantite})"
    
    def save(self, *args, **kwargs):
        # Calculer le stock avant et après
        if not self.pk:  # Nouvelle entrée
            self.stock_avant = self.produit.get_stock_actuel()
            self.stock_apres = self.stock_avant + self.quantite
        else:  # Mise à jour d'une entrée existante
            try:
                ancien_objet = EntreeStock.objects.get(pk=self.pk)
                stock_actuel = self.produit.get_stock_actuel() - ancien_objet.quantite  # Soustraire l'ancienne quantité
                self.stock_avant = stock_actuel
                self.stock_apres = stock_actuel + self.quantite
            except EntreeStock.DoesNotExist:
                self.stock_avant = self.produit.get_stock_actuel()
                self.stock_apres = self.stock_avant + self.quantite
        
        # Créer un mouvement de stock
        super().save(*args, **kwargs)
        MouvementStock.objects.create(
            date=self.date,
            produit=self.produit,
            type_mouvement='Entrée',
            quantite=self.quantite,
            stock_avant=self.stock_avant,
            stock_apres=self.stock_apres,
            observations=f"Entrée {self.id_entree} - Fournisseur: {self.fournisseur}"
        )
    
    class Meta:
        verbose_name = "Entrée en stock"
        verbose_name_plural = "Entrées en stock"
        ordering = ['-date', 'id_entree']


class SortieStock(models.Model):
    """Modèle pour les sorties de stock"""
    id_sortie = models.CharField(max_length=10, primary_key=True, verbose_name="ID Sortie")
    date = models.DateField(default=timezone.now, verbose_name="Date de sortie")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='sorties', verbose_name="Produit")
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Quantité sortie")
    destination = models.CharField(max_length=100, null=True, blank=True, verbose_name="Destination")
    motif = models.CharField(max_length=100, verbose_name="Motif")
    stock_avant = models.PositiveIntegerField(default=0, verbose_name="Stock avant")
    stock_apres = models.PositiveIntegerField(default=0, verbose_name="Stock après")
    
    def __str__(self):
        return f"{self.id_sortie} - {self.produit.nom} ({self.quantite})"
    
    def clean(self):
        """Validation pour s'assurer qu'il y a assez de stock"""
        from django.core.exceptions import ValidationError
        stock_actuel = self.produit.get_stock_actuel()
        if self.pk:  # Si c'est une mise à jour, ajouter l'ancienne quantité
            try:
                ancien_objet = SortieStock.objects.get(pk=self.pk)
                stock_actuel += ancien_objet.quantite
            except SortieStock.DoesNotExist:
                pass
        if self.quantite > stock_actuel:
            raise ValidationError(f"Stock insuffisant. Stock actuel: {stock_actuel}, Quantité demandée: {self.quantite}")
    
    def save(self, *args, **kwargs):
        # Calculer le stock avant et après
        if not self.pk:  # Nouvelle sortie
            self.stock_avant = self.produit.get_stock_actuel()
            self.stock_apres = self.stock_avant - self.quantite
        else:  # Mise à jour d'une sortie existante
            try:
                ancien_objet = SortieStock.objects.get(pk=self.pk)
                stock_actuel = self.produit.get_stock_actuel() + ancien_objet.quantite  # Ajouter l'ancienne quantité
                self.stock_avant = stock_actuel
                self.stock_apres = stock_actuel - self.quantite
            except SortieStock.DoesNotExist:
                self.stock_avant = self.produit.get_stock_actuel()
                self.stock_apres = self.stock_avant - self.quantite
        
        # Vérifier qu'il y a assez de stock
        if self.stock_apres < 0:
            from django.core.exceptions import ValidationError
            raise ValidationError(f"Stock insuffisant. Stock actuel: {self.stock_avant}, Quantité demandée: {self.quantite}")
        
        # Créer un mouvement de stock
        super().save(*args, **kwargs)
        MouvementStock.objects.create(
            date=self.date,
            produit=self.produit,
            type_mouvement='Sortie',
            quantite=self.quantite,
            stock_avant=self.stock_avant,
            stock_apres=self.stock_apres,
            observations=f"Sortie {self.id_sortie} - Destination: {self.destination}, Motif: {self.motif}"
        )
    
    class Meta:
        verbose_name = "Sortie de stock"
        verbose_name_plural = "Sorties de stock"
        ordering = ['-date', 'id_sortie']


class MouvementStock(models.Model):
    """Modèle pour tracer tous les mouvements de stock"""
    TYPE_CHOICES = [
        ('Entrée', 'Entrée'),
        ('Sortie', 'Sortie'),
        ('Ajustement', 'Ajustement'),
    ]
    
    date = models.DateField(default=timezone.now, verbose_name="Date du mouvement")
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='mouvements', verbose_name="Produit")
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name="Type de mouvement")
    quantite = models.IntegerField(verbose_name="Quantité")
    stock_avant = models.PositiveIntegerField(default=0, verbose_name="Stock avant")
    stock_apres = models.PositiveIntegerField(default=0, verbose_name="Stock après")
    observations = models.TextField(blank=True, null=True, verbose_name="Observations")
    
    def __str__(self):
        return f"{self.date} - {self.produit.nom} - {self.type_mouvement} ({self.quantite})"
    
    class Meta:
        verbose_name = "Mouvement de stock"
        verbose_name_plural = "Mouvements de stock"
        ordering = ['-date']


# Les modèles Facture et LigneFacture ont été supprimés


class Commande(models.Model):
    """Modèle pour les commandes de produits"""
    STATUS_CHOICES = [
        ('Brouillon', 'Brouillon'),
        ('En attente', 'En attente de validation'),
        ('Validée', 'Validée'),
        ('En cours', 'En cours de traitement'),
        ('Livrée', 'Livrée'),
        ('Annulée', 'Annulée'),
    ]
    
    numero = models.CharField(max_length=15, primary_key=True, verbose_name="Numéro de commande")
    date_creation = models.DateField(default=timezone.now, verbose_name="Date de création")
    date_livraison_prevue = models.DateField(null=True, blank=True, verbose_name="Date de livraison prévue")
    date_livraison_reelle = models.DateField(null=True, blank=True, verbose_name="Date de livraison réelle")
    
    fournisseur = models.CharField(max_length=100, verbose_name="Fournisseur")
    adresse_fournisseur = models.TextField(blank=True, verbose_name="Adresse du fournisseur")
    telephone_fournisseur = models.CharField(max_length=20, blank=True, verbose_name="Téléphone du fournisseur")
    email_fournisseur = models.EmailField(blank=True, verbose_name="Email du fournisseur")
    
    montant_total = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Montant total (GNF)")
    remise = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="Remise (%)")
    montant_final = models.DecimalField(max_digits=15, decimal_places=0, default=0, verbose_name="Montant final (GNF)")
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Brouillon', verbose_name="Statut")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Document signé joint
    def get_commande_upload_path(instance, filename):
        # Chemin de stockage: commandes/NUMERO_COMMANDE/filename
        return os.path.join('commandes', instance.numero, filename)
        
    document_signe = models.FileField(upload_to=get_commande_upload_path, null=True, blank=True, verbose_name="Document signé")
    
    def __str__(self):
        return f"{self.numero} - {self.fournisseur} ({self.montant_final} GNF)"
    
    @property
    def montant_remise(self):
        """Calcule le montant de la remise"""
        if not self.remise:
            return 0
        return (self.montant_total * self.remise) / 100
    
    def calculer_montants(self):
        """Calcule les montants de la commande à partir des lignes"""
        from django.db.models import Sum
        total = self.lignes.aggregate(Sum('prix_total'))['prix_total__sum'] or 0
        self.montant_total = total
        
        # Calcul du montant final après remise
        montant_remise = (self.montant_total * self.remise) / 100 if self.remise else 0
        self.montant_final = self.montant_total - montant_remise
        
        self.save(update_fields=['montant_total', 'montant_final'])
    
    def save(self, *args, **kwargs):
        # Si c'est une nouvelle commande, générer automatiquement un numéro
        if not self.numero:
            date_str = timezone.now().strftime('%Y%m')
            last_commande = Commande.objects.filter(numero__startswith=f"CMD{date_str}").order_by('numero').last()
            
            if last_commande:
                last_num = int(last_commande.numero[7:])
                self.numero = f"CMD{date_str}{last_num+1:04d}"
            else:
                self.numero = f"CMD{date_str}0001"
                
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_creation', 'numero']


class LigneCommande(models.Model):
    """Modèle pour les lignes de commande"""
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='lignes', verbose_name="Commande")
    produit = models.ForeignKey(Produit, on_delete=models.PROTECT, verbose_name="Produit")
    nom_produit = models.CharField(max_length=100, blank=True, verbose_name="Nom du produit")
    categorie = models.CharField(max_length=50, blank=True, verbose_name="Catégorie")
    quantite = models.PositiveIntegerField(validators=[MinValueValidator(1)], verbose_name="Quantité")
    prix_unitaire = models.DecimalField(max_digits=12, decimal_places=0, validators=[MinValueValidator(0)], verbose_name="Prix unitaire (GNF)")
    prix_total = models.DecimalField(max_digits=15, decimal_places=0, verbose_name="Prix total (GNF)")
    
    def __str__(self):
        return f"{self.produit.nom} - {self.quantite} x {self.prix_unitaire} = {self.prix_total}"
    
    def save(self, *args, **kwargs):
        # Remplir automatiquement le nom et la catégorie du produit
        if self.produit:
            self.nom_produit = self.produit.nom
            self.categorie = self.produit.categorie
            
        self.prix_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)
        self.commande.calculer_montants()
    
    class Meta:
        verbose_name = "Ligne de commande"
        verbose_name_plural = "Lignes de commande"
        ordering = ['id']


# Les modèles Facture et LigneFacture ont été déplacés vers models_facturation.py

