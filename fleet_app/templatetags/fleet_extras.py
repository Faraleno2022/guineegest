from django import template

register = template.Library()

@register.filter
def subtract(value, arg):
    """Subtract the arg from the value."""
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        try:
            return float(value) - float(arg)
        except (ValueError, TypeError):
            return ''

@register.filter
def lookup(dictionary, key):
    """
    Filtre pour accéder aux valeurs d'un dictionnaire dans les templates Django
    Usage: {{ dict|lookup:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)
