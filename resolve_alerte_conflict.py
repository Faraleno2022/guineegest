"""
Script pour résoudre le conflit de modèle Alerte dans l'application Django.
Ce script va:
1. Rechercher toutes les références au modèle Alerte dans le code
2. Vérifier si le modèle est défini plusieurs fois
3. Proposer une solution pour résoudre le conflit
"""

import os
import re
from pathlib import Path

# Chemin vers le projet Django
BASE_DIR = Path(__file__).resolve().parent
APP_DIR = BASE_DIR / "fleet_app"

def search_for_alerte_model():
    """Recherche toutes les définitions et imports du modèle Alerte."""
    model_definitions = []
    model_imports = []
    
    # Parcourir tous les fichiers Python dans l'application
    for file_path in APP_DIR.glob("**/*.py"):
        if file_path.name.startswith("__"):
            continue
            
        relative_path = file_path.relative_to(BASE_DIR)
        content = file_path.read_text(encoding="utf-8")
        
        # Rechercher les définitions de classe Alerte
        class_matches = re.findall(r"class\s+Alerte\s*\(\s*models\.Model\s*\)", content)
        if class_matches:
            model_definitions.append((str(relative_path), len(class_matches)))
            
        # Rechercher les imports du modèle Alerte
        import_matches = re.findall(r"from\s+[\.\w]+\s+import\s+.*Alerte", content)
        if import_matches:
            model_imports.append((str(relative_path), import_matches))
    
    return model_definitions, model_imports

def check_models_py():
    """Vérifie si le modèle Alerte est défini ou importé dans models.py."""
    models_py_path = APP_DIR / "models.py"
    if not models_py_path.exists():
        return False, "Le fichier models.py n'existe pas."
        
    content = models_py_path.read_text(encoding="utf-8")
    
    # Vérifier si le modèle Alerte est défini dans models.py
    class_match = re.search(r"class\s+Alerte\s*\(\s*models\.Model\s*\)", content)
    if class_match:
        return True, f"Le modèle Alerte est défini dans models.py à la ligne {content[:class_match.start()].count(chr(10)) + 1}"
    
    # Vérifier si le modèle Alerte est importé dans models.py
    import_match = re.search(r"from\s+[\.\w]+\s+import\s+.*Alerte", content)
    if import_match:
        return True, f"Le modèle Alerte est importé dans models.py à la ligne {content[:import_match.start()].count(chr(10)) + 1}"
    
    # Vérifier s'il y a une référence à Alerte dans models.py
    alerte_match = re.search(r"\bAlerte\b", content)
    if alerte_match:
        return True, f"Il y a une référence à Alerte dans models.py à la ligne {content[:alerte_match.start()].count(chr(10)) + 1}"
    
    return False, "Le modèle Alerte n'est ni défini ni importé dans models.py."

def main():
    print("Recherche des définitions et imports du modèle Alerte...")
    model_definitions, model_imports = search_for_alerte_model()
    
    print("\nDéfinitions du modèle Alerte trouvées:")
    for path, count in model_definitions:
        print(f"- {path}: {count} définition(s)")
    
    print("\nImports du modèle Alerte trouvés:")
    for path, imports in model_imports:
        print(f"- {path}:")
        for imp in imports:
            print(f"  * {imp}")
    
    print("\nVérification de models.py:")
    has_alerte, message = check_models_py()
    print(message)
    
    print("\nRecommandations:")
    if len(model_definitions) > 1:
        print("1. Le modèle Alerte est défini plusieurs fois. Gardez une seule définition dans models_alertes.py.")
        print("2. Assurez-vous que tous les imports pointent vers cette définition unique.")
    elif has_alerte:
        print("1. Supprimez toute référence au modèle Alerte dans models.py.")
        print("2. Assurez-vous que tous les imports pointent vers models_alertes.py.")
    else:
        print("1. Assurez-vous que tous les imports pointent vers models_alertes.py.")
        print("2. Vérifiez s'il y a des migrations qui font référence à deux modèles Alerte différents.")
    
    print("\nPour résoudre le conflit, vous pouvez essayer:")
    print("1. Supprimer toutes les migrations liées au modèle Alerte")
    print("2. Redémarrer le serveur Django")
    print("3. Créer une nouvelle migration pour le modèle Alerte")
    print("4. Appliquer la migration")

if __name__ == "__main__":
    main()
