import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import json
import os

class ThemesFrame(ttk.Frame):
    """Module de personnalisation des thèmes pour l'application de gestion de parc automobile"""
    
    def __init__(self, parent, root):
        super().__init__(parent)
        self.root = root
        self.config_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config")
        self.themes_file = os.path.join(self.config_dir, "themes.json")
        
        # Couleurs par défaut
        self.default_theme = {
            "background": "#f0f0f0",
            "foreground": "#000000",
            "button_bg": "#e1e1e1",
            "button_fg": "#000000",
            "highlight_bg": "#0078d7",
            "highlight_fg": "#ffffff",
            "tab_bg": "#e1e1e1",
            "tab_fg": "#000000",
            "table_bg": "#ffffff",
            "table_fg": "#000000",
            "table_header_bg": "#e1e1e1",
            "table_header_fg": "#000000",
            "table_row_alt": "#f5f5f5"
        }
        
        # Thèmes prédéfinis
        self.predefined_themes = {
            "Clair (Défaut)": self.default_theme,
            "Sombre": {
                "background": "#2d2d2d",
                "foreground": "#ffffff",
                "button_bg": "#3d3d3d",
                "button_fg": "#ffffff",
                "highlight_bg": "#0078d7",
                "highlight_fg": "#ffffff",
                "tab_bg": "#3d3d3d",
                "tab_fg": "#ffffff",
                "table_bg": "#2d2d2d",
                "table_fg": "#ffffff",
                "table_header_bg": "#3d3d3d",
                "table_header_fg": "#ffffff",
                "table_row_alt": "#353535"
            },
            "Bleu": {
                "background": "#e6f0ff",
                "foreground": "#000000",
                "button_bg": "#b3d1ff",
                "button_fg": "#000000",
                "highlight_bg": "#0052cc",
                "highlight_fg": "#ffffff",
                "tab_bg": "#b3d1ff",
                "tab_fg": "#000000",
                "table_bg": "#ffffff",
                "table_fg": "#000000",
                "table_header_bg": "#b3d1ff",
                "table_header_fg": "#000000",
                "table_row_alt": "#e6f0ff"
            },
            "Vert": {
                "background": "#e6ffe6",
                "foreground": "#000000",
                "button_bg": "#b3ffb3",
                "button_fg": "#000000",
                "highlight_bg": "#00b300",
                "highlight_fg": "#ffffff",
                "tab_bg": "#b3ffb3",
                "tab_fg": "#000000",
                "table_bg": "#ffffff",
                "table_fg": "#000000",
                "table_header_bg": "#b3ffb3",
                "table_header_fg": "#000000",
                "table_row_alt": "#e6ffe6"
            }
        }
        
        # Thème actuel (par défaut au début)
        self.current_theme = self.default_theme.copy()
        
        # Charger les thèmes sauvegardés
        self.load_themes()
        
        # Créer l'interface utilisateur
        self.create_widgets()
    
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Personnalisation des thèmes", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame pour les thèmes prédéfinis
        predefined_frame = ttk.LabelFrame(main_frame, text="Thèmes prédéfinis")
        predefined_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Liste des thèmes prédéfinis
        self.theme_listbox = tk.Listbox(predefined_frame, height=5)
        self.theme_listbox.pack(fill=tk.X, padx=5, pady=5)
        
        # Remplir la liste des thèmes
        for theme_name in self.predefined_themes.keys():
            self.theme_listbox.insert(tk.END, theme_name)
        
        # Thèmes personnalisés
        if hasattr(self, 'custom_themes'):
            for theme_name in self.custom_themes.keys():
                self.theme_listbox.insert(tk.END, theme_name)
        
        # Bouton pour appliquer le thème sélectionné
        apply_button = ttk.Button(predefined_frame, text="Appliquer le thème sélectionné", 
                                 command=self.apply_selected_theme)
        apply_button.pack(pady=5)
        
        # Frame pour la personnalisation des couleurs
        custom_frame = ttk.LabelFrame(main_frame, text="Personnalisation des couleurs")
        custom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Grille pour les sélecteurs de couleurs
        color_grid = ttk.Frame(custom_frame)
        color_grid.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Créer les sélecteurs de couleurs pour chaque élément
        self.color_vars = {}
        self.color_buttons = {}
        
        row = 0
        for color_key, color_name in [
            ("background", "Arrière-plan"),
            ("foreground", "Texte principal"),
            ("button_bg", "Arrière-plan des boutons"),
            ("button_fg", "Texte des boutons"),
            ("highlight_bg", "Arrière-plan de sélection"),
            ("highlight_fg", "Texte de sélection"),
            ("tab_bg", "Arrière-plan des onglets"),
            ("tab_fg", "Texte des onglets"),
            ("table_bg", "Arrière-plan des tableaux"),
            ("table_fg", "Texte des tableaux"),
            ("table_header_bg", "Arrière-plan des en-têtes"),
            ("table_header_fg", "Texte des en-têtes"),
            ("table_row_alt", "Lignes alternées")
        ]:
            ttk.Label(color_grid, text=color_name + ":").grid(row=row, column=0, sticky="w", padx=5, pady=2)
            
            # Variable pour stocker la couleur
            self.color_vars[color_key] = tk.StringVar(value=self.current_theme[color_key])
            
            # Entrée pour afficher la couleur
            color_entry = ttk.Entry(color_grid, textvariable=self.color_vars[color_key], width=10)
            color_entry.grid(row=row, column=1, padx=5, pady=2)
            
            # Bouton pour choisir la couleur
            color_button = ttk.Button(color_grid, text="Choisir", 
                                     command=lambda k=color_key: self.choose_color(k))
            color_button.grid(row=row, column=2, padx=5, pady=2)
            self.color_buttons[color_key] = color_button
            
            # Aperçu de la couleur
            preview = tk.Frame(color_grid, width=30, height=20, bg=self.current_theme[color_key])
            preview.grid(row=row, column=3, padx=5, pady=2)
            
            row += 1
        
        # Frame pour les boutons d'action
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)
        
        # Bouton pour appliquer les changements
        apply_custom_button = ttk.Button(buttons_frame, text="Appliquer les couleurs personnalisées", 
                                       command=self.apply_custom_theme)
        apply_custom_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour sauvegarder le thème personnalisé
        save_button = ttk.Button(buttons_frame, text="Sauvegarder comme nouveau thème", 
                               command=self.save_custom_theme)
        save_button.pack(side=tk.LEFT, padx=5)
        
        # Bouton pour réinitialiser au thème par défaut
        reset_button = ttk.Button(buttons_frame, text="Réinitialiser au thème par défaut", 
                                command=lambda: self.apply_theme(self.default_theme))
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Aperçu du thème
        preview_frame = ttk.LabelFrame(main_frame, text="Aperçu")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Créer un petit aperçu avec différents widgets
        self.preview_window = ttk.Frame(preview_frame)
        self.preview_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.update_preview()
    
    def choose_color(self, color_key):
        """Ouvre un sélecteur de couleur et met à jour la variable correspondante"""
        color = colorchooser.askcolor(initialcolor=self.color_vars[color_key].get())[1]
        if color:
            self.color_vars[color_key].set(color)
            # Mettre à jour l'aperçu de la couleur
            self.update_color_preview(color_key, color)
    
    def update_color_preview(self, color_key, color):
        """Met à jour l'aperçu de la couleur à côté du bouton"""
        # Trouver le widget d'aperçu (Frame) à côté du bouton
        button = self.color_buttons[color_key]
        preview = button.master.grid_slaves(row=button.grid_info()["row"], column=3)[0]
        preview.config(bg=color)
    
    def update_preview(self):
        """Met à jour l'aperçu du thème avec les couleurs actuelles"""
        # Supprimer les widgets précédents
        for widget in self.preview_window.winfo_children():
            widget.destroy()
        
        # Créer un aperçu avec différents widgets
        preview_frame = tk.Frame(self.preview_window, bg=self.current_theme["background"])
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        label = tk.Label(preview_frame, text="Exemple de texte", 
                        bg=self.current_theme["background"], 
                        fg=self.current_theme["foreground"])
        label.pack(pady=5)
        
        # Bouton
        button = tk.Button(preview_frame, text="Bouton exemple", 
                          bg=self.current_theme["button_bg"], 
                          fg=self.current_theme["button_fg"])
        button.pack(pady=5)
        
        # Onglets
        notebook = ttk.Notebook(preview_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tab1 = tk.Frame(notebook, bg=self.current_theme["tab_bg"])
        notebook.add(tab1, text="Onglet 1")
        
        tab2 = tk.Frame(notebook, bg=self.current_theme["tab_bg"])
        notebook.add(tab2, text="Onglet 2")
        
        # Tableau (simulé avec des labels)
        table_frame = tk.Frame(tab1, bg=self.current_theme["table_bg"])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # En-tête du tableau
        header_frame = tk.Frame(table_frame, bg=self.current_theme["table_header_bg"])
        header_frame.pack(fill=tk.X)
        
        tk.Label(header_frame, text="Colonne 1", bg=self.current_theme["table_header_bg"], 
                fg=self.current_theme["table_header_fg"], width=10).pack(side=tk.LEFT, padx=1)
        tk.Label(header_frame, text="Colonne 2", bg=self.current_theme["table_header_bg"], 
                fg=self.current_theme["table_header_fg"], width=10).pack(side=tk.LEFT, padx=1)
        
        # Lignes du tableau
        row1 = tk.Frame(table_frame, bg=self.current_theme["table_bg"])
        row1.pack(fill=tk.X)
        tk.Label(row1, text="Donnée 1", bg=self.current_theme["table_bg"], 
                fg=self.current_theme["table_fg"], width=10).pack(side=tk.LEFT, padx=1)
        tk.Label(row1, text="Donnée 2", bg=self.current_theme["table_bg"], 
                fg=self.current_theme["table_fg"], width=10).pack(side=tk.LEFT, padx=1)
        
        row2 = tk.Frame(table_frame, bg=self.current_theme["table_row_alt"])
        row2.pack(fill=tk.X)
        tk.Label(row2, text="Donnée 3", bg=self.current_theme["table_row_alt"], 
                fg=self.current_theme["table_fg"], width=10).pack(side=tk.LEFT, padx=1)
        tk.Label(row2, text="Donnée 4", bg=self.current_theme["table_row_alt"], 
                fg=self.current_theme["table_fg"], width=10).pack(side=tk.LEFT, padx=1)
    
    def apply_selected_theme(self):
        """Applique le thème sélectionné dans la liste"""
        selection = self.theme_listbox.curselection()
        if not selection:
            messagebox.showinfo("Information", "Veuillez sélectionner un thème dans la liste.")
            return
        
        theme_name = self.theme_listbox.get(selection[0])
        
        # Vérifier si c'est un thème prédéfini
        if theme_name in self.predefined_themes:
            theme = self.predefined_themes[theme_name]
        # Sinon, c'est un thème personnalisé
        elif hasattr(self, 'custom_themes') and theme_name in self.custom_themes:
            theme = self.custom_themes[theme_name]
        else:
            return
        
        # Appliquer le thème
        self.apply_theme(theme)
    
    def apply_custom_theme(self):
        """Applique les couleurs personnalisées"""
        custom_theme = {}
        for color_key in self.color_vars:
            custom_theme[color_key] = self.color_vars[color_key].get()
        
        self.apply_theme(custom_theme)
    
    def apply_theme(self, theme):
        """Applique le thème spécifié à l'application"""
        self.current_theme = theme.copy()
        
        # Mettre à jour les variables de couleur
        for color_key, color_value in theme.items():
            if color_key in self.color_vars:
                self.color_vars[color_key].set(color_value)
                self.update_color_preview(color_key, color_value)
        
        # Mettre à jour l'aperçu
        self.update_preview()
        
        # Appliquer le thème à l'application principale
        self.apply_theme_to_app()
    
    def apply_theme_to_app(self):
        """Applique le thème actuel à l'application principale"""
        # Définir les styles pour les widgets ttk
        style = ttk.Style(self.root)
        
        # Configurer les styles de base
        style.configure(".", 
                       background=self.current_theme["background"],
                       foreground=self.current_theme["foreground"])
        
        # Configurer les styles des boutons
        style.configure("TButton", 
                       background=self.current_theme["button_bg"],
                       foreground=self.current_theme["button_fg"])
        
        # Configurer les styles des onglets
        style.configure("TNotebook", 
                       background=self.current_theme["background"])
        style.configure("TNotebook.Tab", 
                       background=self.current_theme["tab_bg"],
                       foreground=self.current_theme["tab_fg"])
        
        # Configurer les styles des tableaux (Treeview)
        style.configure("Treeview", 
                       background=self.current_theme["table_bg"],
                       foreground=self.current_theme["table_fg"],
                       fieldbackground=self.current_theme["table_bg"])
        style.configure("Treeview.Heading", 
                       background=self.current_theme["table_header_bg"],
                       foreground=self.current_theme["table_header_fg"])
        
        # Configurer les couleurs de sélection
        style.map("Treeview", 
                 background=[("selected", self.current_theme["highlight_bg"])],
                 foreground=[("selected", self.current_theme["highlight_fg"])])
        
        # Configurer les frames
        style.configure("TFrame", background=self.current_theme["background"])
        style.configure("TLabelframe", background=self.current_theme["background"])
        style.configure("TLabelframe.Label", background=self.current_theme["background"],
                       foreground=self.current_theme["foreground"])
        
        # Configurer les labels
        style.configure("TLabel", background=self.current_theme["background"],
                       foreground=self.current_theme["foreground"])
        
        # Configurer les entrées
        style.configure("TEntry", fieldbackground=self.current_theme["table_bg"],
                       foreground=self.current_theme["table_fg"])
        
        # Configurer les combobox
        style.configure("TCombobox", fieldbackground=self.current_theme["table_bg"],
                       foreground=self.current_theme["table_fg"])
        
        # Sauvegarder le thème actuel comme thème par défaut
        self.save_current_theme()
    
    def save_custom_theme(self):
        """Sauvegarde le thème personnalisé actuel"""
        # Demander un nom pour le thème
        theme_name = tk.simpledialog.askstring("Nom du thème", "Entrez un nom pour ce thème:")
        if not theme_name:
            return
        
        # Créer le dictionnaire de thèmes personnalisés s'il n'existe pas
        if not hasattr(self, 'custom_themes'):
            self.custom_themes = {}
        
        # Sauvegarder le thème
        self.custom_themes[theme_name] = self.current_theme.copy()
        
        # Ajouter à la liste
        self.theme_listbox.insert(tk.END, theme_name)
        
        # Sauvegarder tous les thèmes
        self.save_themes()
        
        messagebox.showinfo("Succès", f"Le thème '{theme_name}' a été sauvegardé.")
    
    def save_current_theme(self):
        """Sauvegarde le thème actuel comme thème par défaut"""
        # Créer le répertoire de configuration s'il n'existe pas
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Sauvegarder le thème actuel
        with open(os.path.join(self.config_dir, "current_theme.json"), "w") as f:
            json.dump(self.current_theme, f, indent=4)
    
    def save_themes(self):
        """Sauvegarde tous les thèmes personnalisés"""
        # Créer le répertoire de configuration s'il n'existe pas
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Sauvegarder les thèmes personnalisés
        if hasattr(self, 'custom_themes'):
            with open(self.themes_file, "w") as f:
                json.dump(self.custom_themes, f, indent=4)
    
    def load_themes(self):
        """Charge les thèmes sauvegardés"""
        # Créer le répertoire de configuration s'il n'existe pas
        os.makedirs(self.config_dir, exist_ok=True)
        
        # Charger les thèmes personnalisés
        if os.path.exists(self.themes_file):
            try:
                with open(self.themes_file, "r") as f:
                    self.custom_themes = json.load(f)
            except:
                self.custom_themes = {}
        
        # Charger le thème actuel
        current_theme_file = os.path.join(self.config_dir, "current_theme.json")
        if os.path.exists(current_theme_file):
            try:
                with open(current_theme_file, "r") as f:
                    loaded_theme = json.load(f)
                    # Vérifier que toutes les clés nécessaires sont présentes
                    if all(key in loaded_theme for key in self.default_theme.keys()):
                        self.current_theme = loaded_theme
            except:
                pass  # Utiliser le thème par défaut en cas d'erreur
