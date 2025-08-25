"""
Utilitaires pour l'application fleet_app
"""

# Taux de conversion (1 EUR = X GNF)
TAUX_CONVERSION_EUR_GNF = 11500  # Taux fictif, à ajuster selon le taux réel

def convertir_en_gnf(montant_eur):
    """
    Convertit un montant en euros vers des francs guinéens (GNF)
    
    Args:
        montant_eur (float): Montant en euros
        
    Returns:
        float: Montant converti en GNF
    """
    return montant_eur * TAUX_CONVERSION_EUR_GNF

def formater_montant_gnf(montant_gnf):
    """
    Formate un montant en GNF pour l'affichage
    
    Args:
        montant_gnf (float): Montant en GNF
        
    Returns:
        str: Montant formaté (ex: 1,234,567 GNF)
    """
    return f"{int(montant_gnf):,}".replace(",", " ") + " GNF"

def formater_cout_par_km_gnf(cout_par_km_eur):
    """
    Convertit et formate un coût par km de EUR/km à GNF/km
    
    Args:
        cout_par_km_eur (float): Coût par km en EUR/km
        
    Returns:
        str: Coût par km formaté en GNF/km
    """
    cout_par_km_gnf = convertir_en_gnf(cout_par_km_eur)
    return f"{int(cout_par_km_gnf):,}".replace(",", " ") + " GNF/km"
