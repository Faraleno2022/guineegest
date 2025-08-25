from django import template
from django.template.defaultfilters import floatformat
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiplie la valeur par l'argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
        
@register.filter
def divide(value, arg):
    """Divise la valeur par l'argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def intcomma(value):
    """Formate un nombre avec des séparateurs de milliers"""
    try:
        value = float(value)
        if value == int(value):
            value = int(value)
        orig = str(value)
        new = ""
        
        if '.' in orig:
            dec = orig.split('.')[1]
            orig = orig.split('.')[0]
        else:
            dec = ""
            
        i = len(orig)
        while i > 0:
            new = orig[i-1:i] + new
            i = i - 1
            if i > 0 and (len(orig) - i) % 3 == 0:
                new = " " + new
                
        if dec:
            return new + ',' + dec
        else:
            return new
    except (ValueError, TypeError):
        return value

@register.filter
def get_item(dictionary, key):
    """Récupère un élément d'un dictionnaire par sa clé"""
    return dictionary.get(key)

@register.filter
def subtract(value, arg):
    """Soustrait l'argument de la valeur"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def get_status_color(statut):
    """Retourne la couleur Bootstrap pour un statut de présence"""
    status_colors = {
        # Présences normales
        'P(Am)': 'success',
        'P(Pm)': 'success', 
        'P(Am&Pm)': 'success',
        # Présences dimanche
        'P(dim_Am)': 'info',
        'P(dim_Pm)': 'info',
        'P(dim_Am_&_Pm)': 'info',
        # Absences et autres
        'A': 'danger',
        'M': 'warning',
        'M(Payer)': 'primary',
        'C': 'info',
        'F': 'warning',
        'OFF': 'secondary',
    }
    return status_colors.get(statut, 'secondary')

@register.filter
def get_status_class(statut):
    """Retourne la classe CSS pour un statut de présence"""
    status_classes = {
        'P(Am)': 'present-am',
        'P(Pm)': 'present-pm',
        'P(Am&Pm)': 'present-full',
        'P(dim_Am)': 'present-dim-am',
        'P(dim_Pm)': 'present-dim-pm',
        'P(dim_Am_&_Pm)': 'present-dim-full',
        'A': 'absent',
        'M': 'maladie',
        'M(Payer)': 'maladie-paye',
        'C': 'conge',
        'F': 'formation',
        'OFF': 'repos',
    }
    return status_classes.get(statut, 'default')

@register.filter
def get_status_display(statut):
    """Retourne le libellé d'affichage pour un statut de présence"""
    status_display = {
        # Présences normales
        'P(Am)': 'Matin',
        'P(Pm)': 'AM', 
        'P(Am&Pm)': 'Journée',
        # Présences dimanche
        'P(dim_Am)': 'Dim AM',
        'P(dim_Pm)': 'Dim PM',
        'P(dim_Am_&_Pm)': 'Dim J',
        # Absences et autres
        'A': 'Absent',
        'M': 'Maladie',
        'M(Payer)': 'M.Payé',
        'C': 'Congé',
        'F': 'Formation',
        'OFF': 'Repos',
    }
    return status_display.get(statut, statut)
