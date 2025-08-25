import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import calendar

class DisponibiliteFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.load_disponibilites()
        
    def create_widgets(self):
        # Frame pour le formulaire
        form_frame = ttk.LabelFrame(self, text="Enregistrement de la disponibilité des véhicules")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Champs du formulaire
        ttk.Label(form_frame, text="ID Véhicule:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_vehicule = ttk.Combobox(form_frame, width=20)
        self.id_vehicule.grid(row=0, column=1, padx=5, pady=5)
        self.load_vehicules_ids()
        
        ttk.Label(form_frame, text="Période (mois/année):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        
        # Frame pour la période (mois/année)
        periode_frame = ttk.Frame(form_frame)
        periode_frame.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        # Combobox pour le mois
        self.mois = ttk.Combobox(periode_frame, values=[str(i).zfill(2) for i in range(1, 13)], width=5)
        self.mois.pack(side=tk.LEFT, padx=(0, 5))
        self.mois.bind("<<ComboboxSelected>>", self.update_jours_total)
        
        # Combobox pour l'année
        current_year = datetime.now().year
        self.annee = ttk.Combobox(periode_frame, values=[str(i) for i in range(current_year-5, current_year+2)], width=6)
        self.annee.pack(side=tk.LEFT)
        self.annee.set(str(current_year))
        self.annee.bind("<<ComboboxSelected>>", self.update_jours_total)
        
        ttk.Label(form_frame, text="Jours total période:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.jours_total = ttk.Entry(form_frame, width=20, state="readonly")
        self.jours_total.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Jours hors service:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.jours_hors_service = ttk.Entry(form_frame, width=20)
        self.jours_hors_service.grid(row=3, column=1, padx=5, pady=5)
        self.jours_hors_service.bind("<KeyRelease>", self.calculer_disponibilite)
        
        ttk.Label(form_frame, text="Disponibilité (%):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.disponibilite = ttk.Entry(form_frame, width=20, state="readonly")
        self.disponibilite.grid(row=4, column=1, padx=5, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_disponibilite).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_disponibilite).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_disponibilite).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Effacer", command=self.clear_form).grid(row=0, column=3, padx=5)
        
        # Tableau des disponibilités
        table_frame = ttk.LabelFrame(self, text="Liste des disponibilités des véhicules")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.disponibilites_tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set)
        self.disponibilites_tree["columns"] = ("ID", "ID_Vehicule", "Periode", "Jours_Total", "Jours_Hors_Service", "Disponibilite")
        
        # Format des colonnes
        self.disponibilites_tree.column("#0", width=0, stretch=tk.NO)
        self.disponibilites_tree.column("ID", anchor=tk.W, width=40)
        self.disponibilites_tree.column("ID_Vehicule", anchor=tk.W, width=100)
        self.disponibilites_tree.column("Periode", anchor=tk.W, width=120)
        self.disponibilites_tree.column("Jours_Total", anchor=tk.W, width=100)
        self.disponibilites_tree.column("Jours_Hors_Service", anchor=tk.W, width=120)
        self.disponibilites_tree.column("Disponibilite", anchor=tk.W, width=120)
        
        # En-têtes
        self.disponibilites_tree.heading("#0", text="", anchor=tk.W)
        self.disponibilites_tree.heading("ID", text="ID", anchor=tk.W)
        self.disponibilites_tree.heading("ID_Vehicule", text="ID Véhicule", anchor=tk.W)
        self.disponibilites_tree.heading("Periode", text="Période", anchor=tk.W)
        self.disponibilites_tree.heading("Jours_Total", text="Jours total", anchor=tk.W)
        self.disponibilites_tree.heading("Jours_Hors_Service", text="Jours hors service", anchor=tk.W)
        self.disponibilites_tree.heading("Disponibilite", text="Disponibilité (%)", anchor=tk.W)
        
        self.disponibilites_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.disponibilites_tree.yview)
        
        # Événement de sélection
        self.disponibilites_tree.bind("<ButtonRelease-1>", self.select_disponibilite)
        
        # Configuration du grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # ID caché pour les mises à jour
        self.current_id = None
        
        # Initialiser le mois courant
        current_month = datetime.now().month
        self.mois.set(str(current_month).zfill(2))
        
        # Initialiser le nombre de jours
        self.update_jours_total(None)
    
    def load_vehicules_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Vehicule FROM Vehicules ORDER BY ID_Vehicule")
        vehicules = [row[0] for row in cursor.fetchall()]
        self.id_vehicule['values'] = vehicules
    
    def update_jours_total(self, event):
        try:
            mois = int(self.mois.get())
            annee = int(self.annee.get())
            
            # Obtenir le nombre de jours dans le mois
            jours_dans_mois = calendar.monthrange(annee, mois)[1]
            
            # Mettre à jour le champ jours_total
            self.jours_total.config(state="normal")
            self.jours_total.delete(0, tk.END)
            self.jours_total.insert(0, jours_dans_mois)
            self.jours_total.config(state="readonly")
            
            # Recalculer la disponibilité
            self.calculer_disponibilite(None)
            
        except (ValueError, IndexError):
            pass
    
    def calculer_disponibilite(self, event):
        try:
            jours_total = int(self.jours_total.get())
            jours_hors_service_str = self.jours_hors_service.get()
            
            if jours_hors_service_str:
                jours_hors_service = int(jours_hors_service_str)
                
                if jours_hors_service > jours_total:
                    messagebox.showerror("Erreur", "Le nombre de jours hors service ne peut pas dépasser le nombre total de jours")
                    self.jours_hors_service.delete(0, tk.END)
                    return
                
                # Calculer la disponibilité en pourcentage
                disponibilite = ((jours_total - jours_hors_service) / jours_total) * 100
                
                # Mettre à jour le champ disponibilité
                self.disponibilite.config(state="normal")
                self.disponibilite.delete(0, tk.END)
                self.disponibilite.insert(0, round(disponibilite, 2))
                self.disponibilite.config(state="readonly")
            else:
                # Effacer le champ disponibilité si jours_hors_service est vide
                self.disponibilite.config(state="normal")
                self.disponibilite.delete(0, tk.END)
                self.disponibilite.config(state="readonly")
                
        except (ValueError, ZeroDivisionError):
            pass
    
    def load_disponibilites(self):
        # Effacer les données existantes
        for item in self.disponibilites_tree.get_children():
            self.disponibilites_tree.delete(item)
        
        # Charger les données depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT ID, ID_Vehicule, Periode, Jours_Total_Periode, Jours_Hors_Service, Disponibilite_Pourcentage
        FROM DisponibiliteVehicule
        ORDER BY Periode DESC
        ''')
        
        for row in cursor.fetchall():
            self.disponibilites_tree.insert("", tk.END, values=row)
    
    def select_disponibilite(self, event):
        # Récupérer l'élément sélectionné
        selected_item = self.disponibilites_tree.focus()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.disponibilites_tree.item(selected_item, "values")
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
        
        self.jours_total.config(state="normal")
        self.jours_total.insert(0, values[3])
        self.jours_total.config(state="readonly")
        
        self.jours_hors_service.insert(0, values[4])
        
        self.disponibilite.config(state="normal")
        self.disponibilite.insert(0, values[5])
        self.disponibilite.config(state="readonly")
    
    def clear_form(self):
        # Effacer tous les champs
        self.current_id = None
        self.id_vehicule.set("")
        
        # Ne pas effacer le mois et l'année, juste mettre à jour le nombre de jours
        self.update_jours_total(None)
        
        self.jours_hors_service.delete(0, tk.END)
        
        self.disponibilite.config(state="normal")
        self.disponibilite.delete(0, tk.END)
        self.disponibilite.config(state="readonly")
    
    def add_disponibilite(self):
        # Vérifier les champs obligatoires
        if not self.id_vehicule.get() or not self.mois.get() or not self.annee.get() or not self.jours_hors_service.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        # Vérifier si une entrée existe déjà pour ce véhicule et cette période
        periode = f"{self.mois.get()}/{self.annee.get()}"
        
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT COUNT(*) FROM DisponibiliteVehicule
        WHERE ID_Vehicule = ? AND Periode = ?
        ''', (self.id_vehicule.get(), periode))
        
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Erreur", "Une entrée existe déjà pour ce véhicule et cette période")
            return
        
        try:
            # Calculer la disponibilité si ce n'est pas déjà fait
            if not self.disponibilite.get():
                self.calculer_disponibilite(None)
            
            # Insérer la disponibilité
            cursor.execute('''
            INSERT INTO DisponibiliteVehicule (
                ID_Vehicule, Periode, Jours_Total_Periode, Jours_Hors_Service, Disponibilite_Pourcentage
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                self.id_vehicule.get(),
                periode,
                self.jours_total.get(),
                self.jours_hors_service.get(),
                self.disponibilite.get()
            ))
            
            self.conn.commit()
            
            # Vérifier si la disponibilité est faible
            self.check_disponibilite_alert(self.id_vehicule.get(), float(self.disponibilite.get()), int(self.jours_hors_service.get()))
            
            messagebox.showinfo("Succès", "Disponibilité ajoutée avec succès")
            self.clear_form()
            self.load_disponibilites()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", str(e))
    
    def update_disponibilite(self):
        # Vérifier si une disponibilité est sélectionnée
        if self.current_id:
            try:
                # Calculer la disponibilité si ce n'est pas déjà fait
                if not self.disponibilite.get():
                    self.calculer_disponibilite(None)
                
                # Mettre à jour la période
                periode = f"{self.mois.get()}/{self.annee.get()}"
                
                # Mettre à jour la disponibilité
                cursor = self.conn.cursor()
                cursor.execute('''
                UPDATE DisponibiliteVehicule SET
                    ID_Vehicule = ?, Periode = ?, Jours_Total_Periode = ?, 
                    Jours_Hors_Service = ?, Disponibilite_Pourcentage = ?
                WHERE ID = ?
                ''', (
                    self.id_vehicule.get(),
                    periode,
                    self.jours_total.get(),
                    self.jours_hors_service.get(),
                    self.disponibilite.get(),
                    self.current_id
                ))
                
                self.conn.commit()
                
                # Vérifier si la disponibilité est faible
                self.check_disponibilite_alert(self.id_vehicule.get(), float(self.disponibilite.get()), int(self.jours_hors_service.get()))
                
                messagebox.showinfo("Succès", "Disponibilité mise à jour avec succès")
                self.clear_form()
                self.load_disponibilites()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une disponibilité")
    
    def delete_disponibilite(self):
        # Vérifier si une disponibilité est sélectionnée
        if self.current_id:
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette disponibilité ?"):
                try:
                    # Supprimer la disponibilité
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM DisponibiliteVehicule WHERE ID = ?", (self.current_id,))
                    self.conn.commit()
                    messagebox.showinfo("Succès", "Disponibilité supprimée avec succès")
                    self.clear_form()
                    self.load_disponibilites()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une disponibilité")
    
    def check_disponibilite_alert(self, id_vehicule, disponibilite, jours_hors_service):
        """Vérifie si la disponibilité est faible et crée une alerte si nécessaire"""
        # Alerte si disponibilité < 80%
        if disponibilite < 80:
            cursor = self.conn.cursor()
            periode = f"{self.mois.get()}/{self.annee.get()}"
            
            # Vérifier si une alerte existe déjà pour ce véhicule et cette période
            cursor.execute('''
            SELECT COUNT(*) FROM Alertes
            WHERE ID_Vehicule = ? AND Type_Alerte = 'Disponibilité' AND Description LIKE ?
            AND Statut = 'Active'
            ''', (id_vehicule, f"%{periode}%"))
            
            if cursor.fetchone()[0] == 0:
                # Créer une nouvelle alerte
                cursor.execute('''
                INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    id_vehicule,
                    'Disponibilité',
                    f"Faible disponibilité ({disponibilite:.2f}%) pour la période {periode}",
                    datetime.now().strftime('%Y-%m-%d'),
                    'Élevé',
                    'Active'
                ))
                
                self.conn.commit()
                messagebox.warning("Alerte", f"Attention: Faible disponibilité pour le véhicule {id_vehicule}!")
        
        # Alerte si un véhicule est en garage > 3 jours consécutifs
        if jours_hors_service > 3:
            cursor = self.conn.cursor()
            periode = f"{self.mois.get()}/{self.annee.get()}"
            
            # Vérifier si une alerte existe déjà pour ce véhicule et cette période
            cursor.execute('''
            SELECT COUNT(*) FROM Alertes
            WHERE ID_Vehicule = ? AND Type_Alerte = 'Immobilisation' AND Description LIKE ?
            AND Statut = 'Active'
            ''', (id_vehicule, f"%{periode}%"))
            
            if cursor.fetchone()[0] == 0:
                # Créer une nouvelle alerte
                cursor.execute('''
                INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    id_vehicule,
                    'Immobilisation',
                    f"Immobilisation prolongée ({jours_hors_service} jours) pour la période {periode}",
                    datetime.now().strftime('%Y-%m-%d'),
                    'Moyen',
                    'Active'
                ))
                
                self.conn.commit()
                messagebox.warning("Alerte", f"Attention: Immobilisation prolongée pour le véhicule {id_vehicule}!")
