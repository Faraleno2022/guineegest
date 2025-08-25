import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime

class SecuriteFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.load_incidents()
        
    def create_widgets(self):
        # Frame pour le formulaire
        form_frame = ttk.LabelFrame(self, text="Enregistrement des incidents de sécurité")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Champs du formulaire
        ttk.Label(form_frame, text="ID Véhicule:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_vehicule = ttk.Combobox(form_frame, width=20)
        self.id_vehicule.grid(row=0, column=1, padx=5, pady=5)
        self.load_vehicules_ids()
        
        ttk.Label(form_frame, text="Date incident:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_incident = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_incident.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Type incident:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.type_incident = ttk.Combobox(form_frame, values=["Accident", "Incident", "Défaut critique"], width=17)
        self.type_incident.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Gravité:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.gravite = ttk.Combobox(form_frame, values=["Mineure", "Modérée", "Majeure", "Critique"], width=17)
        self.gravite.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Commentaires:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.commentaires = tk.Text(form_frame, width=40, height=5)
        self.commentaires.grid(row=4, column=1, columnspan=2, padx=5, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_incident).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_incident).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_incident).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Effacer", command=self.clear_form).grid(row=0, column=3, padx=5)
        
        # Tableau des incidents
        table_frame = ttk.LabelFrame(self, text="Liste des incidents de sécurité")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.incidents_tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set)
        self.incidents_tree["columns"] = ("ID", "ID_Vehicule", "Date_Incident", "Type_Incident", "Gravite")
        
        # Format des colonnes
        self.incidents_tree.column("#0", width=0, stretch=tk.NO)
        self.incidents_tree.column("ID", anchor=tk.W, width=40)
        self.incidents_tree.column("ID_Vehicule", anchor=tk.W, width=100)
        self.incidents_tree.column("Date_Incident", anchor=tk.W, width=120)
        self.incidents_tree.column("Type_Incident", anchor=tk.W, width=120)
        self.incidents_tree.column("Gravite", anchor=tk.W, width=120)
        
        # En-têtes
        self.incidents_tree.heading("#0", text="", anchor=tk.W)
        self.incidents_tree.heading("ID", text="ID", anchor=tk.W)
        self.incidents_tree.heading("ID_Vehicule", text="ID Véhicule", anchor=tk.W)
        self.incidents_tree.heading("Date_Incident", text="Date incident", anchor=tk.W)
        self.incidents_tree.heading("Type_Incident", text="Type incident", anchor=tk.W)
        self.incidents_tree.heading("Gravite", text="Gravité", anchor=tk.W)
        
        self.incidents_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.incidents_tree.yview)
        
        # Événement de sélection
        self.incidents_tree.bind("<ButtonRelease-1>", self.select_incident)
        
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
    
    def load_incidents(self):
        # Effacer les données existantes
        for item in self.incidents_tree.get_children():
            self.incidents_tree.delete(item)
        
        # Charger les données depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT ID, ID_Vehicule, Date_Incident, Type_Incident, Gravite
        FROM IncidentsSecurite
        ORDER BY Date_Incident DESC
        ''')
        
        for row in cursor.fetchall():
            self.incidents_tree.insert("", tk.END, values=row)
    
    def select_incident(self, event):
        # Récupérer l'élément sélectionné
        selected_item = self.incidents_tree.focus()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.incidents_tree.item(selected_item, "values")
        if not values:
            return
        
        # Effacer le formulaire
        self.clear_form()
        
        # Récupérer toutes les données de l'incident
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM IncidentsSecurite WHERE ID = ?
        ''', (values[0],))
        
        incident = cursor.fetchone()
        if not incident:
            return
        
        # Remplir le formulaire
        self.current_id = incident["ID"]
        self.id_vehicule.set(incident["ID_Vehicule"])
        
        if incident["Date_Incident"]:
            self.date_incident.set_date(datetime.strptime(incident["Date_Incident"], "%Y-%m-%d"))
        
        self.type_incident.set(incident["Type_Incident"])
        self.gravite.set(incident["Gravite"])
        self.commentaires.insert("1.0", incident["Commentaires"] or "")
    
    def clear_form(self):
        # Effacer tous les champs
        self.current_id = None
        self.id_vehicule.set("")
        self.type_incident.set("")
        self.gravite.set("")
        self.commentaires.delete("1.0", tk.END)
    
    def add_incident(self):
        # Vérifier les champs obligatoires
        if not self.id_vehicule.get() or not self.type_incident.get() or not self.gravite.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        try:
            # Insérer l'incident
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO IncidentsSecurite (
                ID_Vehicule, Date_Incident, Type_Incident, Gravite, Commentaires
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                self.id_vehicule.get(),
                self.date_incident.get(),
                self.type_incident.get(),
                self.gravite.get(),
                self.commentaires.get("1.0", tk.END).strip()
            ))
            
            self.conn.commit()
            
            # Créer une alerte pour l'incident
            self.create_incident_alert(
                self.id_vehicule.get(),
                self.type_incident.get(),
                self.gravite.get()
            )
            
            messagebox.showinfo("Succès", "Incident ajouté avec succès")
            self.clear_form()
            self.load_incidents()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", str(e))
    
    def update_incident(self):
        # Vérifier si un incident est sélectionné
        if self.current_id:
            try:
                # Mettre à jour l'incident
                cursor = self.conn.cursor()
                cursor.execute('''
                UPDATE IncidentsSecurite SET
                    ID_Vehicule = ?, Date_Incident = ?, Type_Incident = ?, 
                    Gravite = ?, Commentaires = ?
                WHERE ID = ?
                ''', (
                    self.id_vehicule.get(),
                    self.date_incident.get(),
                    self.type_incident.get(),
                    self.gravite.get(),
                    self.commentaires.get("1.0", tk.END).strip(),
                    self.current_id
                ))
                
                self.conn.commit()
                messagebox.showinfo("Succès", "Incident mis à jour avec succès")
                self.clear_form()
                self.load_incidents()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un incident")
    
    def delete_incident(self):
        # Vérifier si un incident est sélectionné
        if self.current_id:
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet incident ?"):
                try:
                    # Supprimer l'incident
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM IncidentsSecurite WHERE ID = ?", (self.current_id,))
                    self.conn.commit()
                    messagebox.showinfo("Succès", "Incident supprimé avec succès")
                    self.clear_form()
                    self.load_incidents()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un incident")
    
    def create_incident_alert(self, id_vehicule, type_incident, gravite):
        """Crée une alerte pour un incident de sécurité"""
        # Déterminer le niveau d'urgence en fonction du type d'incident et de la gravité
        niveau_urgence = "Critique"  # Par défaut pour tous les incidents de sécurité
        
        if type_incident == "Incident" and gravite in ["Mineure", "Modérée"]:
            niveau_urgence = "Élevé"
        
        # Créer une description pour l'alerte
        description = f"{type_incident} de gravité {gravite} signalé le {self.date_incident.get()}"
        
        # Insérer l'alerte
        cursor = self.conn.cursor()
        cursor.execute('''
        INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            id_vehicule,
            'Sécurité',
            description,
            datetime.now().strftime('%Y-%m-%d'),
            niveau_urgence,
            'Active'
        ))
        
        self.conn.commit()
        
        # Afficher un message d'alerte
        messagebox.showwarning("Alerte de sécurité", 
                              f"Une alerte de sécurité a été créée pour le véhicule {id_vehicule}.\n"
                              f"Type: {type_incident}\n"
                              f"Gravité: {gravite}\n"
                              f"Niveau d'urgence: {niveau_urgence}")
