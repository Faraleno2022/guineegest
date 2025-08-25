import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import calendar

class UtilisationFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.load_utilisations()
        
    def create_widgets(self):
        # Frame pour le formulaire
        form_frame = ttk.LabelFrame(self, text="Enregistrement de l'utilisation des actifs")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Champs du formulaire
        ttk.Label(form_frame, text="ID Véhicule:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_vehicule = ttk.Combobox(form_frame, width=20)
        self.id_vehicule.grid(row=0, column=1, padx=5, pady=5)
        self.load_vehicules_ids()
        self.id_vehicule.bind("<<ComboboxSelected>>", self.on_vehicule_selected)
        
        ttk.Label(form_frame, text="Période (mois/année):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        # Frame pour la période (mois/année)
        periode_frame = ttk.Frame(form_frame)
        periode_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Combobox pour le mois
        self.mois = ttk.Combobox(periode_frame, values=[str(i).zfill(2) for i in range(1, 13)], width=5)
        self.mois.pack(side=tk.LEFT, padx=(0, 5))
        
        # Combobox pour l'année
        current_year = datetime.now().year
        self.annee = ttk.Combobox(periode_frame, values=[str(i) for i in range(current_year-5, current_year+2)], width=6)
        self.annee.pack(side=tk.LEFT)
        self.annee.set(str(current_year))
        
        ttk.Label(form_frame, text="Jours disponibles:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.jours_disponibles = ttk.Entry(form_frame, width=20)
        self.jours_disponibles.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Jours utilisés:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.jours_utilises = ttk.Entry(form_frame, width=20)
        self.jours_utilises.grid(row=3, column=1, padx=5, pady=5)
        self.jours_utilises.bind("<KeyRelease>", self.calculer_utilisation)
        
        ttk.Label(form_frame, text="Utilisation (%):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.utilisation = ttk.Entry(form_frame, width=20, state="readonly")
        self.utilisation.grid(row=4, column=1, padx=5, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_utilisation).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_utilisation).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_utilisation).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Effacer", command=self.clear_form).grid(row=0, column=3, padx=5)
        
        # Tableau des utilisations
        table_frame = ttk.LabelFrame(self, text="Liste des utilisations des actifs")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.utilisations_tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set)
        self.utilisations_tree["columns"] = ("ID", "ID_Vehicule", "Periode", "Jours_Disponibles", "Jours_Utilises", "Utilisation")
        
        # Format des colonnes
        self.utilisations_tree.column("#0", width=0, stretch=tk.NO)
        self.utilisations_tree.column("ID", anchor=tk.W, width=40)
        self.utilisations_tree.column("ID_Vehicule", anchor=tk.W, width=100)
        self.utilisations_tree.column("Periode", anchor=tk.W, width=120)
        self.utilisations_tree.column("Jours_Disponibles", anchor=tk.W, width=120)
        self.utilisations_tree.column("Jours_Utilises", anchor=tk.W, width=120)
        self.utilisations_tree.column("Utilisation", anchor=tk.W, width=120)
        
        # En-têtes
        self.utilisations_tree.heading("#0", text="", anchor=tk.W)
        self.utilisations_tree.heading("ID", text="ID", anchor=tk.W)
        self.utilisations_tree.heading("ID_Vehicule", text="ID Véhicule", anchor=tk.W)
        self.utilisations_tree.heading("Periode", text="Période", anchor=tk.W)
        self.utilisations_tree.heading("Jours_Disponibles", text="Jours disponibles", anchor=tk.W)
        self.utilisations_tree.heading("Jours_Utilises", text="Jours utilisés", anchor=tk.W)
        self.utilisations_tree.heading("Utilisation", text="Utilisation (%)", anchor=tk.W)
        
        self.utilisations_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.utilisations_tree.yview)
        
        # Événement de sélection
        self.utilisations_tree.bind("<ButtonRelease-1>", self.select_utilisation)
        
        # Configuration du grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # ID caché pour les mises à jour
        self.current_id = None
        
        # Initialiser le mois courant
        current_month = datetime.now().month
        self.mois.set(str(current_month).zfill(2))
    
    def load_vehicules_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Vehicule FROM Vehicules ORDER BY ID_Vehicule")
        vehicules = [row[0] for row in cursor.fetchall()]
        self.id_vehicule['values'] = vehicules
    
    def on_vehicule_selected(self, event):
        # Récupérer les jours disponibles pour le véhicule sélectionné
        vehicule_id = self.id_vehicule.get()
        periode = f"{self.mois.get()}/{self.annee.get()}"
        
        if vehicule_id:
            cursor = self.conn.cursor()
            
            # Récupérer les jours disponibles depuis la table DisponibiliteVehicule
            cursor.execute("""
            SELECT Jours_Total_Periode - Jours_Hors_Service 
            FROM DisponibiliteVehicule 
            WHERE ID_Vehicule = ? AND Periode = ?
            """, (vehicule_id, periode))
            
            result = cursor.fetchone()
            if result:
                self.jours_disponibles.delete(0, tk.END)
                self.jours_disponibles.insert(0, result[0])
            else:
                # Si pas de données de disponibilité, utiliser le nombre de jours dans le mois
                try:
                    mois = int(self.mois.get())
                    annee = int(self.annee.get())
                    jours_dans_mois = calendar.monthrange(annee, mois)[1]
                    self.jours_disponibles.delete(0, tk.END)
                    self.jours_disponibles.insert(0, jours_dans_mois)
                except (ValueError, IndexError):
                    pass
    
    def calculer_utilisation(self, event):
        try:
            jours_disponibles = int(self.jours_disponibles.get())
            jours_utilises_str = self.jours_utilises.get()
            
            if jours_utilises_str:
                jours_utilises = int(jours_utilises_str)
                
                if jours_utilises > jours_disponibles:
                    messagebox.showerror("Erreur", "Le nombre de jours utilisés ne peut pas dépasser le nombre de jours disponibles")
                    self.jours_utilises.delete(0, tk.END)
                    return
                
                # Calculer l'utilisation en pourcentage
                utilisation = (jours_utilises / jours_disponibles) * 100
                
                # Mettre à jour le champ utilisation
                self.utilisation.config(state="normal")
                self.utilisation.delete(0, tk.END)
                self.utilisation.insert(0, round(utilisation, 2))
                self.utilisation.config(state="readonly")
            else:
                # Effacer le champ utilisation si jours_utilises est vide
                self.utilisation.config(state="normal")
                self.utilisation.delete(0, tk.END)
                self.utilisation.config(state="readonly")
                
        except (ValueError, ZeroDivisionError):
            pass
    
    def load_utilisations(self):
        # Effacer les données existantes
        for item in self.utilisations_tree.get_children():
            self.utilisations_tree.delete(item)
        
        # Charger les données depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT ID, ID_Vehicule, Periode, Jours_Disponibles, Jours_Utilises, Utilisation_Pourcentage
        FROM UtilisationActifs
        ORDER BY Periode DESC
        ''')
        
        for row in cursor.fetchall():
            self.utilisations_tree.insert("", tk.END, values=row)
    
    def select_utilisation(self, event):
        # Récupérer l'élément sélectionné
        selected_item = self.utilisations_tree.focus()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.utilisations_tree.item(selected_item, "values")
        if not values:
            return
        
        # Effacer le formulaire
        self.clear_form()
        
        # Remplir le formulaire
        self.current_id = values[0]
        self.id_vehicule.set(values[1])
        
        # Extraire le mois et l'année de la période (format MM/YYYY)
        periode = values[2].split('/')
        if len(periode) == 2:
            self.mois.set(periode[0])
            self.annee.set(periode[1])
        
        self.jours_disponibles.insert(0, values[3])
        self.jours_utilises.insert(0, values[4])
        
        self.utilisation.config(state="normal")
        self.utilisation.insert(0, values[5])
        self.utilisation.config(state="readonly")
    
    def clear_form(self):
        # Effacer tous les champs
        self.current_id = None
        self.id_vehicule.set("")
        
        # Ne pas effacer le mois et l'année
        self.jours_disponibles.delete(0, tk.END)
        self.jours_utilises.delete(0, tk.END)
        
        self.utilisation.config(state="normal")
        self.utilisation.delete(0, tk.END)
        self.utilisation.config(state="readonly")
    
    def add_utilisation(self):
        # Vérifier les champs obligatoires
        if not self.id_vehicule.get() or not self.mois.get() or not self.annee.get() or not self.jours_disponibles.get() or not self.jours_utilises.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        # Vérifier si une entrée existe déjà pour ce véhicule et cette période
        periode = f"{self.mois.get()}/{self.annee.get()}"
        
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM UtilisationActifs
        WHERE ID_Vehicule = ? AND Periode = ?
        ''', (self.id_vehicule.get(), periode))
        
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Erreur", "Une entrée existe déjà pour ce véhicule et cette période")
            return
        
        try:
            # Calculer l'utilisation si ce n'est pas déjà fait
            if not self.utilisation.get():
                self.calculer_utilisation(None)
            
            # Insérer l'utilisation
            cursor.execute('''
            INSERT INTO UtilisationActifs (
                ID_Vehicule, Periode, Jours_Disponibles, Jours_Utilises, Utilisation_Pourcentage
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                self.id_vehicule.get(),
                periode,
                self.jours_disponibles.get(),
                self.jours_utilises.get(),
                self.utilisation.get()
            ))
            
            self.conn.commit()
            
            # Vérifier si l'utilisation est anormale
            self.check_utilisation_alert(self.id_vehicule.get(), float(self.utilisation.get()))
            
            messagebox.showinfo("Succès", "Utilisation ajoutée avec succès")
            self.clear_form()
            self.load_utilisations()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", str(e))
    
    def update_utilisation(self):
        # Vérifier si une utilisation est sélectionnée
        if self.current_id:
            try:
                # Calculer l'utilisation si ce n'est pas déjà fait
                if not self.utilisation.get():
                    self.calculer_utilisation(None)
                
                # Mettre à jour la période
                periode = f"{self.mois.get()}/{self.annee.get()}"
                
                # Mettre à jour l'utilisation
                cursor = self.conn.cursor()
                cursor.execute('''
                UPDATE UtilisationActifs SET
                    ID_Vehicule = ?, Periode = ?, Jours_Disponibles = ?, 
                    Jours_Utilises = ?, Utilisation_Pourcentage = ?
                WHERE ID = ?
                ''', (
                    self.id_vehicule.get(),
                    periode,
                    self.jours_disponibles.get(),
                    self.jours_utilises.get(),
                    self.utilisation.get(),
                    self.current_id
                ))
                
                self.conn.commit()
                
                # Vérifier si l'utilisation est anormale
                self.check_utilisation_alert(self.id_vehicule.get(), float(self.utilisation.get()))
                
                messagebox.showinfo("Succès", "Utilisation mise à jour avec succès")
                self.clear_form()
                self.load_utilisations()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une utilisation")
    
    def delete_utilisation(self):
        # Vérifier si une utilisation est sélectionnée
        if self.current_id:
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette utilisation ?"):
                try:
                    # Supprimer l'utilisation
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM UtilisationActifs WHERE ID = ?", (self.current_id,))
                    self.conn.commit()
                    messagebox.showinfo("Succès", "Utilisation supprimée avec succès")
                    self.clear_form()
                    self.load_utilisations()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une utilisation")
    
    def check_utilisation_alert(self, id_vehicule, utilisation):
        """Vérifie si l'utilisation est anormale et crée une alerte si nécessaire"""
        cursor = self.conn.cursor()
        periode = f"{self.mois.get()}/{self.annee.get()}"
        
        # Alerte si utilisation < 70%
        if utilisation < 70:
            # Vérifier si une alerte existe déjà pour ce véhicule et cette période
            cursor.execute('''
            SELECT COUNT(*) FROM Alertes
            WHERE ID_Vehicule = ? AND Type_Alerte = 'Sous-utilisation' AND Description LIKE ?
            AND Statut = 'Active'
            ''', (id_vehicule, f"%{periode}%"))
            
            if cursor.fetchone()[0] == 0:
                # Créer une nouvelle alerte
                cursor.execute('''
                INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    id_vehicule,
                    'Sous-utilisation',
                    f"Faible utilisation ({utilisation:.2f}%) pour la période {periode}",
                    datetime.now().strftime('%Y-%m-%d'),
                    'Moyen',
                    'Active'
                ))
                
                self.conn.commit()
                messagebox.warning("Alerte", f"Attention: Faible utilisation pour le véhicule {id_vehicule}!")
        
        # Alerte si utilisation > 95%
        elif utilisation > 95:
            # Vérifier si une alerte existe déjà pour ce véhicule et cette période
            cursor.execute('''
            SELECT COUNT(*) FROM Alertes
            WHERE ID_Vehicule = ? AND Type_Alerte = 'Sur-utilisation' AND Description LIKE ?
            AND Statut = 'Active'
            ''', (id_vehicule, f"%{periode}%"))
            
            if cursor.fetchone()[0] == 0:
                # Créer une nouvelle alerte
                cursor.execute('''
                INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    id_vehicule,
                    'Sur-utilisation',
                    f"Utilisation excessive ({utilisation:.2f}%) pour la période {periode}",
                    datetime.now().strftime('%Y-%m-%d'),
                    'Moyen',
                    'Active'
                ))
                
                self.conn.commit()
                messagebox.warning("Alerte", f"Attention: Utilisation excessive pour le véhicule {id_vehicule}!")
