import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime

class VehiculesFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.load_vehicules()
        
    def create_widgets(self):
        # Frame pour le formulaire
        form_frame = ttk.LabelFrame(self, text="Informations du véhicule")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Champs du formulaire
        ttk.Label(form_frame, text="ID Véhicule:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_vehicule = ttk.Entry(form_frame, width=20)
        self.id_vehicule.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Immatriculation:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.immatriculation = ttk.Entry(form_frame, width=20)
        self.immatriculation.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Marque:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.marque = ttk.Entry(form_frame, width=20)
        self.marque.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Modèle:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.modele = ttk.Entry(form_frame, width=20)
        self.modele.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Type de moteur:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.type_moteur = ttk.Combobox(form_frame, values=["Essence", "Diesel", "Hybride", "Électrique"], width=17)
        self.type_moteur.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Catégorie:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.categorie = ttk.Combobox(form_frame, values=["Voiture", "Moto", "4x4", "Camion", "Bus"], width=17)
        self.categorie.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date de mise en service:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.date_mise_service = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_mise_service.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date d'acquisition:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.date_acquisition = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_acquisition.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Kilométrage initial:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.kilometrage_initial = ttk.Entry(form_frame, width=20)
        self.kilometrage_initial.grid(row=2, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Affectation:").grid(row=3, column=2, sticky="w", padx=5, pady=5)
        self.affectation = ttk.Entry(form_frame, width=20)
        self.affectation.grid(row=3, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Statut actuel:").grid(row=4, column=2, sticky="w", padx=5, pady=5)
        self.statut_actuel = ttk.Combobox(form_frame, values=["Actif", "Maintenance", "Hors Service"], width=17)
        self.statut_actuel.grid(row=4, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Numéro de châssis:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.numero_chassis = ttk.Entry(form_frame, width=20)
        self.numero_chassis.grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Numéro moteur:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.numero_moteur = ttk.Entry(form_frame, width=20)
        self.numero_moteur.grid(row=7, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Observations:").grid(row=5, column=2, sticky="w", padx=5, pady=5)
        self.observations = tk.Text(form_frame, width=20, height=3)
        self.observations.grid(row=5, column=3, rowspan=3, padx=5, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=8, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_vehicule).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_vehicule).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_vehicule).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Effacer", command=self.clear_form).grid(row=0, column=3, padx=5)
        
        # Tableau des véhicules
        table_frame = ttk.LabelFrame(self, text="Liste des véhicules")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.vehicules_tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set)
        self.vehicules_tree["columns"] = ("ID", "Immatriculation", "Marque", "Modèle", "Type", "Catégorie", "Statut")
        
        # Format des colonnes
        self.vehicules_tree.column("#0", width=0, stretch=tk.NO)
        self.vehicules_tree.column("ID", anchor=tk.W, width=80)
        self.vehicules_tree.column("Immatriculation", anchor=tk.W, width=120)
        self.vehicules_tree.column("Marque", anchor=tk.W, width=100)
        self.vehicules_tree.column("Modèle", anchor=tk.W, width=100)
        self.vehicules_tree.column("Type", anchor=tk.W, width=100)
        self.vehicules_tree.column("Catégorie", anchor=tk.W, width=100)
        self.vehicules_tree.column("Statut", anchor=tk.W, width=100)
        
        # En-têtes
        self.vehicules_tree.heading("#0", text="", anchor=tk.W)
        self.vehicules_tree.heading("ID", text="ID", anchor=tk.W)
        self.vehicules_tree.heading("Immatriculation", text="Immatriculation", anchor=tk.W)
        self.vehicules_tree.heading("Marque", text="Marque", anchor=tk.W)
        self.vehicules_tree.heading("Modèle", text="Modèle", anchor=tk.W)
        self.vehicules_tree.heading("Type", text="Type Moteur", anchor=tk.W)
        self.vehicules_tree.heading("Catégorie", text="Catégorie", anchor=tk.W)
        self.vehicules_tree.heading("Statut", text="Statut", anchor=tk.W)
        
        self.vehicules_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.vehicules_tree.yview)
        
        # Événement de sélection
        self.vehicules_tree.bind("<ButtonRelease-1>", self.select_vehicule)
        
        # Configuration du grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
    
    def load_vehicules(self):
        # Effacer les données existantes
        for item in self.vehicules_tree.get_children():
            self.vehicules_tree.delete(item)
        
        # Charger les données depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT ID_Vehicule, Immatriculation, Marque, Modele, Type_Moteur, Categorie, Statut_Actuel
        FROM Vehicules
        ORDER BY ID_Vehicule
        ''')
        
        for row in cursor.fetchall():
            self.vehicules_tree.insert("", tk.END, values=row)
    
    def select_vehicule(self, event):
        # Récupérer l'élément sélectionné
        selected_item = self.vehicules_tree.focus()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.vehicules_tree.item(selected_item, "values")
        if not values:
            return
        
        # Effacer le formulaire
        self.clear_form()
        
        # Récupérer toutes les données du véhicule
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM Vehicules WHERE ID_Vehicule = ?
        ''', (values[0],))
        
        vehicule = cursor.fetchone()
        if not vehicule:
            return
        
        # Remplir le formulaire
        self.id_vehicule.insert(0, vehicule["ID_Vehicule"])
        self.immatriculation.insert(0, vehicule["Immatriculation"])
        self.marque.insert(0, vehicule["Marque"])
        self.modele.insert(0, vehicule["Modele"])
        self.type_moteur.set(vehicule["Type_Moteur"])
        self.categorie.set(vehicule["Categorie"])
        
        if vehicule["Date_Mise_Service"]:
            self.date_mise_service.set_date(datetime.strptime(vehicule["Date_Mise_Service"], "%Y-%m-%d"))
        
        if vehicule["Date_Acquisition"]:
            self.date_acquisition.set_date(datetime.strptime(vehicule["Date_Acquisition"], "%Y-%m-%d"))
        
        self.kilometrage_initial.insert(0, vehicule["Kilometrage_Initial"])
        self.affectation.insert(0, vehicule["Affectation"])
        self.statut_actuel.set(vehicule["Statut_Actuel"])
        self.numero_chassis.insert(0, vehicule["Numero_Chassis"])
        self.numero_moteur.insert(0, vehicule["Numero_Moteur"])
        self.observations.insert("1.0", vehicule["Observations"])
        
        # Désactiver l'ID (clé primaire)
        self.id_vehicule.config(state="disabled")
    
    def clear_form(self):
        # Effacer tous les champs
        self.id_vehicule.config(state="normal")
        self.id_vehicule.delete(0, tk.END)
        self.immatriculation.delete(0, tk.END)
        self.marque.delete(0, tk.END)
        self.modele.delete(0, tk.END)
        self.type_moteur.set("")
        self.categorie.set("")
        self.kilometrage_initial.delete(0, tk.END)
        self.affectation.delete(0, tk.END)
        self.statut_actuel.set("")
        self.numero_chassis.delete(0, tk.END)
        self.numero_moteur.delete(0, tk.END)
        self.observations.delete("1.0", tk.END)
    
    def add_vehicule(self):
        # Vérifier les champs obligatoires
        if not self.id_vehicule.get() or not self.immatriculation.get() or not self.marque.get() or not self.modele.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        # Vérifier si l'ID existe déjà
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Vehicules WHERE ID_Vehicule = ?", (self.id_vehicule.get(),))
        if cursor.fetchone()[0] > 0:
            messagebox.showerror("Erreur", "Cet ID de véhicule existe déjà")
            return
        
        try:
            # Insérer le véhicule
            cursor.execute('''
            INSERT INTO Vehicules (
                ID_Vehicule, Immatriculation, Marque, Modele, Type_Moteur, Categorie,
                Date_Mise_Service, Date_Acquisition, Kilometrage_Initial, Affectation,
                Statut_Actuel, Numero_Chassis, Numero_Moteur, Observations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.id_vehicule.get(),
                self.immatriculation.get(),
                self.marque.get(),
                self.modele.get(),
                self.type_moteur.get(),
                self.categorie.get(),
                self.date_mise_service.get(),
                self.date_acquisition.get(),
                self.kilometrage_initial.get() or 0,
                self.affectation.get(),
                self.statut_actuel.get(),
                self.numero_chassis.get(),
                self.numero_moteur.get(),
                self.observations.get("1.0", tk.END).strip()
            ))
            
            self.conn.commit()
            messagebox.showinfo("Succès", "Véhicule ajouté avec succès")
            self.clear_form()
            self.load_vehicules()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", str(e))
    
    def update_vehicule(self):
        # Vérifier si un véhicule est sélectionné
        if self.id_vehicule.cget("state") == "disabled":
            try:
                # Mettre à jour le véhicule
                cursor = self.conn.cursor()
                cursor.execute('''
                UPDATE Vehicules SET
                    Immatriculation = ?, Marque = ?, Modele = ?, Type_Moteur = ?, Categorie = ?,
                    Date_Mise_Service = ?, Date_Acquisition = ?, Kilometrage_Initial = ?, Affectation = ?,
                    Statut_Actuel = ?, Numero_Chassis = ?, Numero_Moteur = ?, Observations = ?
                WHERE ID_Vehicule = ?
                ''', (
                    self.immatriculation.get(),
                    self.marque.get(),
                    self.modele.get(),
                    self.type_moteur.get(),
                    self.categorie.get(),
                    self.date_mise_service.get(),
                    self.date_acquisition.get(),
                    self.kilometrage_initial.get() or 0,
                    self.affectation.get(),
                    self.statut_actuel.get(),
                    self.numero_chassis.get(),
                    self.numero_moteur.get(),
                    self.observations.get("1.0", tk.END).strip(),
                    self.id_vehicule.get()
                ))
                
                self.conn.commit()
                messagebox.showinfo("Succès", "Véhicule mis à jour avec succès")
                self.clear_form()
                self.load_vehicules()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un véhicule")
    
    def delete_vehicule(self):
        # Vérifier si un véhicule est sélectionné
        if self.id_vehicule.cget("state") == "disabled":
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce véhicule ?"):
                try:
                    # Supprimer le véhicule
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM Vehicules WHERE ID_Vehicule = ?", (self.id_vehicule.get(),))
                    self.conn.commit()
                    messagebox.showinfo("Succès", "Véhicule supprimé avec succès")
                    self.clear_form()
                    self.load_vehicules()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un véhicule")
