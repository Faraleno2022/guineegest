import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime

class DistanceFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.load_distances()
        
    def create_widgets(self):
        # Frame pour le formulaire
        form_frame = ttk.LabelFrame(self, text="Enregistrement des distances parcourues")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Champs du formulaire
        ttk.Label(form_frame, text="ID Véhicule:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_vehicule = ttk.Combobox(form_frame, width=20)
        self.id_vehicule.grid(row=0, column=1, padx=5, pady=5)
        self.load_vehicules_ids()
        self.id_vehicule.bind("<<ComboboxSelected>>", self.on_vehicule_selected)
        
        ttk.Label(form_frame, text="Date début:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_debut = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_debut.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Km début:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.km_debut = ttk.Entry(form_frame, width=20)
        self.km_debut.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date fin:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.date_fin = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_fin.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Km fin:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.km_fin = ttk.Entry(form_frame, width=20)
        self.km_fin.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Distance parcourue:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.distance_parcourue = ttk.Entry(form_frame, width=20, state="readonly")
        self.distance_parcourue.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Type moteur:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.type_moteur = ttk.Combobox(form_frame, values=["Diesel", "Essence", "Moto"], width=17, state="readonly")
        self.type_moteur.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Limite annuelle (km):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.limite_annuelle = ttk.Entry(form_frame, width=20, state="readonly")
        self.limite_annuelle.grid(row=1, column=3, padx=5, pady=5)
        
        # Bouton pour calculer la distance
        ttk.Button(form_frame, text="Calculer distance", command=self.calculer_distance).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Boutons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_distance).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_distance).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_distance).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Effacer", command=self.clear_form).grid(row=0, column=3, padx=5)
        
        # Tableau des distances
        table_frame = ttk.LabelFrame(self, text="Liste des distances parcourues")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.distances_tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set)
        self.distances_tree["columns"] = ("ID", "ID_Vehicule", "Date_Debut", "Km_Debut", "Date_Fin", "Km_Fin", "Distance", "Type_Moteur", "Limite")
        
        # Format des colonnes
        self.distances_tree.column("#0", width=0, stretch=tk.NO)
        self.distances_tree.column("ID", anchor=tk.W, width=40)
        self.distances_tree.column("ID_Vehicule", anchor=tk.W, width=80)
        self.distances_tree.column("Date_Debut", anchor=tk.W, width=100)
        self.distances_tree.column("Km_Debut", anchor=tk.W, width=80)
        self.distances_tree.column("Date_Fin", anchor=tk.W, width=100)
        self.distances_tree.column("Km_Fin", anchor=tk.W, width=80)
        self.distances_tree.column("Distance", anchor=tk.W, width=100)
        self.distances_tree.column("Type_Moteur", anchor=tk.W, width=100)
        self.distances_tree.column("Limite", anchor=tk.W, width=100)
        
        # En-têtes
        self.distances_tree.heading("#0", text="", anchor=tk.W)
        self.distances_tree.heading("ID", text="ID", anchor=tk.W)
        self.distances_tree.heading("ID_Vehicule", text="ID Véhicule", anchor=tk.W)
        self.distances_tree.heading("Date_Debut", text="Date début", anchor=tk.W)
        self.distances_tree.heading("Km_Debut", text="Km début", anchor=tk.W)
        self.distances_tree.heading("Date_Fin", text="Date fin", anchor=tk.W)
        self.distances_tree.heading("Km_Fin", text="Km fin", anchor=tk.W)
        self.distances_tree.heading("Distance", text="Distance (km)", anchor=tk.W)
        self.distances_tree.heading("Type_Moteur", text="Type moteur", anchor=tk.W)
        self.distances_tree.heading("Limite", text="Limite (km)", anchor=tk.W)
        
        self.distances_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.distances_tree.yview)
        
        # Événement de sélection
        self.distances_tree.bind("<ButtonRelease-1>", self.select_distance)
        
        # Configuration du grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # ID caché pour les mises à jour
        self.current_id = None
    
    def load_vehicules_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Vehicule FROM Vehicules ORDER BY ID_Vehicule")
        vehicules = [row[0] for row in cursor.fetchall()]
        self.id_vehicule['values'] = vehicules
    
    def on_vehicule_selected(self, event):
        # Récupérer le type de moteur du véhicule sélectionné
        vehicule_id = self.id_vehicule.get()
        if vehicule_id:
            cursor = self.conn.cursor()
            cursor.execute("SELECT Type_Moteur FROM Vehicules WHERE ID_Vehicule = ?", (vehicule_id,))
            result = cursor.fetchone()
            if result:
                type_moteur = result[0]
                # Adapter le type de moteur pour correspondre aux valeurs autorisées dans DistancesParcourues
                if type_moteur == "Hybride" or type_moteur == "Électrique":
                    type_moteur = "Essence"  # Par défaut
                
                self.type_moteur.set(type_moteur)
                self.update_limite_annuelle()
                
                # Récupérer le dernier kilométrage enregistré
                cursor.execute("""
                SELECT Km_Fin FROM DistancesParcourues 
                WHERE ID_Vehicule = ? 
                ORDER BY Date_Fin DESC LIMIT 1
                """, (vehicule_id,))
                result = cursor.fetchone()
                if result:
                    self.km_debut.delete(0, tk.END)
                    self.km_debut.insert(0, result[0])
    
    def update_limite_annuelle(self):
        type_moteur = self.type_moteur.get()
        limite = 0
        
        if type_moteur == "Diesel":
            limite = 30000
        elif type_moteur == "Essence":
            limite = 15000
        elif type_moteur == "Moto":
            limite = 10000
        
        self.limite_annuelle.config(state="normal")
        self.limite_annuelle.delete(0, tk.END)
        self.limite_annuelle.insert(0, limite)
        self.limite_annuelle.config(state="readonly")
    
    def calculer_distance(self):
        try:
            km_debut = int(self.km_debut.get())
            km_fin = int(self.km_fin.get())
            
            if km_fin < km_debut:
                messagebox.showerror("Erreur", "Le kilométrage final doit être supérieur au kilométrage initial")
                return
            
            distance = km_fin - km_debut
            
            self.distance_parcourue.config(state="normal")
            self.distance_parcourue.delete(0, tk.END)
            self.distance_parcourue.insert(0, distance)
            self.distance_parcourue.config(state="readonly")
            
            # Mettre à jour la limite annuelle
            self.update_limite_annuelle()
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides pour les kilométrages")
    
    def load_distances(self):
        # Effacer les données existantes
        for item in self.distances_tree.get_children():
            self.distances_tree.delete(item)
        
        # Charger les données depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT ID, ID_Vehicule, Date_Debut, Km_Debut, Date_Fin, Km_Fin, Distance_Parcourue, Type_Moteur, Limite_Annuelle
        FROM DistancesParcourues
        ORDER BY Date_Fin DESC
        ''')
        
        for row in cursor.fetchall():
            self.distances_tree.insert("", tk.END, values=row)
    
    def select_distance(self, event):
        # Récupérer l'élément sélectionné
        selected_item = self.distances_tree.focus()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.distances_tree.item(selected_item, "values")
        if not values:
            return
        
        # Effacer le formulaire
        self.clear_form()
        
        # Remplir le formulaire
        self.current_id = values[0]
        self.id_vehicule.set(values[1])
        
        if values[2]:  # Date_Debut
            self.date_debut.set_date(datetime.strptime(values[2], "%Y-%m-%d"))
        
        self.km_debut.insert(0, values[3])
        
        if values[4]:  # Date_Fin
            self.date_fin.set_date(datetime.strptime(values[4], "%Y-%m-%d"))
        
        self.km_fin.insert(0, values[5])
        
        self.distance_parcourue.config(state="normal")
        self.distance_parcourue.insert(0, values[6])
        self.distance_parcourue.config(state="readonly")
        
        self.type_moteur.set(values[7])
        
        self.limite_annuelle.config(state="normal")
        self.limite_annuelle.insert(0, values[8])
        self.limite_annuelle.config(state="readonly")
    
    def clear_form(self):
        # Effacer tous les champs
        self.current_id = None
        self.id_vehicule.set("")
        self.km_debut.delete(0, tk.END)
        self.km_fin.delete(0, tk.END)
        
        self.distance_parcourue.config(state="normal")
        self.distance_parcourue.delete(0, tk.END)
        self.distance_parcourue.config(state="readonly")
        
        self.type_moteur.set("")
        
        self.limite_annuelle.config(state="normal")
        self.limite_annuelle.delete(0, tk.END)
        self.limite_annuelle.config(state="readonly")
    
    def add_distance(self):
        # Vérifier les champs obligatoires
        if not self.id_vehicule.get() or not self.km_debut.get() or not self.km_fin.get() or not self.type_moteur.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        try:
            # Calculer la distance si ce n'est pas déjà fait
            if not self.distance_parcourue.get():
                self.calculer_distance()
            
            # Insérer la distance
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO DistancesParcourues (
                ID_Vehicule, Date_Debut, Km_Debut, Date_Fin, Km_Fin, 
                Distance_Parcourue, Type_Moteur, Limite_Annuelle
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.id_vehicule.get(),
                self.date_debut.get(),
                self.km_debut.get(),
                self.date_fin.get(),
                self.km_fin.get(),
                self.distance_parcourue.get(),
                self.type_moteur.get(),
                self.limite_annuelle.get()
            ))
            
            self.conn.commit()
            
            # Vérifier si la distance dépasse la limite annuelle
            self.check_distance_alert(self.id_vehicule.get(), int(self.distance_parcourue.get()), int(self.limite_annuelle.get()))
            
            messagebox.showinfo("Succès", "Distance ajoutée avec succès")
            self.clear_form()
            self.load_distances()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", str(e))
    
    def update_distance(self):
        # Vérifier si une distance est sélectionnée
        if self.current_id:
            try:
                # Calculer la distance si ce n'est pas déjà fait
                if not self.distance_parcourue.get():
                    self.calculer_distance()
                
                # Mettre à jour la distance
                cursor = self.conn.cursor()
                cursor.execute('''
                UPDATE DistancesParcourues SET
                    ID_Vehicule = ?, Date_Debut = ?, Km_Debut = ?, Date_Fin = ?, Km_Fin = ?,
                    Distance_Parcourue = ?, Type_Moteur = ?, Limite_Annuelle = ?
                WHERE ID = ?
                ''', (
                    self.id_vehicule.get(),
                    self.date_debut.get(),
                    self.km_debut.get(),
                    self.date_fin.get(),
                    self.km_fin.get(),
                    self.distance_parcourue.get(),
                    self.type_moteur.get(),
                    self.limite_annuelle.get(),
                    self.current_id
                ))
                
                self.conn.commit()
                
                # Vérifier si la distance dépasse la limite annuelle
                self.check_distance_alert(self.id_vehicule.get(), int(self.distance_parcourue.get()), int(self.limite_annuelle.get()))
                
                messagebox.showinfo("Succès", "Distance mise à jour avec succès")
                self.clear_form()
                self.load_distances()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une distance")
    
    def delete_distance(self):
        # Vérifier si une distance est sélectionnée
        if self.current_id:
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette distance ?"):
                try:
                    # Supprimer la distance
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM DistancesParcourues WHERE ID = ?", (self.current_id,))
                    self.conn.commit()
                    messagebox.showinfo("Succès", "Distance supprimée avec succès")
                    self.clear_form()
                    self.load_distances()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une distance")
    
    def check_distance_alert(self, id_vehicule, distance, limite):
        """Vérifie si la distance parcourue dépasse la limite annuelle et crée une alerte si nécessaire"""
        # Calculer la distance totale parcourue cette année
        current_year = datetime.now().year
        start_date = f"{current_year}-01-01"
        end_date = f"{current_year}-12-31"
        
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT SUM(Distance_Parcourue) FROM DistancesParcourues
        WHERE ID_Vehicule = ? AND Date_Fin BETWEEN ? AND ?
        ''', (id_vehicule, start_date, end_date))
        
        result = cursor.fetchone()
        total_distance = result[0] if result[0] else 0
        
        # Si la distance totale dépasse la limite annuelle, créer une alerte
        if total_distance > limite:
            # Vérifier si une alerte existe déjà pour ce véhicule cette année
            cursor.execute('''
            SELECT COUNT(*) FROM Alertes
            WHERE ID_Vehicule = ? AND Type_Alerte = 'Distance' AND Date_Creation LIKE ?
            AND Statut = 'Active'
            ''', (id_vehicule, f"{current_year}%"))
            
            if cursor.fetchone()[0] == 0:
                # Créer une nouvelle alerte
                cursor.execute('''
                INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    id_vehicule,
                    'Distance',
                    f"Dépassement de la limite annuelle ({limite} km) - Distance actuelle: {total_distance} km",
                    datetime.now().strftime('%Y-%m-%d'),
                    'Élevé',
                    'Active'
                ))
                
                self.conn.commit()
                messagebox.warning("Alerte", f"Attention: Le véhicule {id_vehicule} a dépassé sa limite annuelle de kilométrage!")
