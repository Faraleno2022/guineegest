import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class AlertesFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.load_alertes()
        
    def create_widgets(self):
        # Frame pour les filtres
        filter_frame = ttk.LabelFrame(self, text="Filtres")
        filter_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Filtres
        ttk.Label(filter_frame, text="Véhicule:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filtre_vehicule = ttk.Combobox(filter_frame, width=20)
        self.filtre_vehicule.grid(row=0, column=1, padx=5, pady=5)
        self.load_vehicules_ids()
        
        ttk.Label(filter_frame, text="Type d'alerte:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.filtre_type = ttk.Combobox(filter_frame, width=20)
        self.filtre_type.grid(row=0, column=3, padx=5, pady=5)
        self.load_types_alertes()
        
        ttk.Label(filter_frame, text="Niveau d'urgence:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.filtre_urgence = ttk.Combobox(filter_frame, values=["", "Faible", "Moyen", "Élevé", "Critique"], width=20)
        self.filtre_urgence.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Statut:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.filtre_statut = ttk.Combobox(filter_frame, values=["", "Active", "Résolue", "Ignorée"], width=20)
        self.filtre_statut.grid(row=1, column=3, padx=5, pady=5)
        self.filtre_statut.set("Active")  # Par défaut, afficher les alertes actives
        
        # Bouton de filtrage
        ttk.Button(filter_frame, text="Filtrer", command=self.filter_alertes).grid(row=1, column=4, padx=5, pady=5)
        ttk.Button(filter_frame, text="Réinitialiser", command=self.reset_filters).grid(row=1, column=5, padx=5, pady=5)
        
        # Tableau des alertes
        table_frame = ttk.LabelFrame(self, text="Liste des alertes")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.alertes_tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set)
        self.alertes_tree["columns"] = ("ID", "ID_Vehicule", "Type_Alerte", "Description", "Date_Creation", "Niveau_Urgence", "Statut")
        
        # Format des colonnes
        self.alertes_tree.column("#0", width=0, stretch=tk.NO)
        self.alertes_tree.column("ID", anchor=tk.W, width=40)
        self.alertes_tree.column("ID_Vehicule", anchor=tk.W, width=100)
        self.alertes_tree.column("Type_Alerte", anchor=tk.W, width=120)
        self.alertes_tree.column("Description", anchor=tk.W, width=300)
        self.alertes_tree.column("Date_Creation", anchor=tk.W, width=100)
        self.alertes_tree.column("Niveau_Urgence", anchor=tk.W, width=100)
        self.alertes_tree.column("Statut", anchor=tk.W, width=80)
        
        # En-têtes
        self.alertes_tree.heading("#0", text="", anchor=tk.W)
        self.alertes_tree.heading("ID", text="ID", anchor=tk.W)
        self.alertes_tree.heading("ID_Vehicule", text="ID Véhicule", anchor=tk.W)
        self.alertes_tree.heading("Type_Alerte", text="Type d'alerte", anchor=tk.W)
        self.alertes_tree.heading("Description", text="Description", anchor=tk.W)
        self.alertes_tree.heading("Date_Creation", text="Date création", anchor=tk.W)
        self.alertes_tree.heading("Niveau_Urgence", text="Niveau d'urgence", anchor=tk.W)
        self.alertes_tree.heading("Statut", text="Statut", anchor=tk.W)
        
        self.alertes_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.alertes_tree.yview)
        
        # Événement de sélection
        self.alertes_tree.bind("<ButtonRelease-1>", self.select_alerte)
        
        # Frame pour les détails et actions
        details_frame = ttk.LabelFrame(self, text="Détails et actions")
        details_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        # Détails de l'alerte sélectionnée
        ttk.Label(details_frame, text="ID Alerte:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_alerte = ttk.Label(details_frame, text="")
        self.id_alerte.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Véhicule:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.detail_vehicule = ttk.Label(details_frame, text="")
        self.detail_vehicule.grid(row=0, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Type d'alerte:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.detail_type = ttk.Label(details_frame, text="")
        self.detail_type.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Niveau d'urgence:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.detail_urgence = ttk.Label(details_frame, text="")
        self.detail_urgence.grid(row=1, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Date création:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.detail_date = ttk.Label(details_frame, text="")
        self.detail_date.grid(row=2, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Statut:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.statut_alerte = ttk.Combobox(details_frame, values=["Active", "Résolue", "Ignorée"], width=15)
        self.statut_alerte.grid(row=2, column=3, sticky="w", padx=5, pady=5)
        
        ttk.Label(details_frame, text="Description:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.detail_description = tk.Text(details_frame, width=60, height=3, wrap=tk.WORD)
        self.detail_description.grid(row=3, column=1, columnspan=3, padx=5, pady=5)
        self.detail_description.config(state="disabled")
        
        ttk.Label(details_frame, text="Commentaire:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.commentaire = tk.Text(details_frame, width=60, height=3, wrap=tk.WORD)
        self.commentaire.grid(row=4, column=1, columnspan=3, padx=5, pady=5)
        
        # Boutons d'action
        action_frame = ttk.Frame(details_frame)
        action_frame.grid(row=5, column=0, columnspan=4, pady=10)
        
        ttk.Button(action_frame, text="Mettre à jour le statut", command=self.update_statut).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="Voir détails véhicule", command=self.voir_vehicule).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="Exporter alertes", command=self.export_alertes).grid(row=0, column=2, padx=5)
        
        # Configuration du grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # ID caché pour les mises à jour
        self.current_id = None
    
    def load_vehicules_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Vehicule FROM Vehicules ORDER BY ID_Vehicule")
        vehicules = [""] + [row[0] for row in cursor.fetchall()]
        self.filtre_vehicule['values'] = vehicules
    
    def load_types_alertes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT DISTINCT Type_Alerte FROM Alertes ORDER BY Type_Alerte")
        types = [""] + [row[0] for row in cursor.fetchall()]
        self.filtre_type['values'] = types
    
    def load_alertes(self):
        # Effacer les données existantes
        for item in self.alertes_tree.get_children():
            self.alertes_tree.delete(item)
        
        # Construire la requête SQL avec les filtres
        query = '''
        SELECT ID, ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut
        FROM Alertes
        WHERE 1=1
        '''
        params = []
        
        if self.filtre_vehicule.get():
            query += " AND ID_Vehicule = ?"
            params.append(self.filtre_vehicule.get())
        
        if self.filtre_type.get():
            query += " AND Type_Alerte = ?"
            params.append(self.filtre_type.get())
        
        if self.filtre_urgence.get():
            query += " AND Niveau_Urgence = ?"
            params.append(self.filtre_urgence.get())
        
        if self.filtre_statut.get():
            query += " AND Statut = ?"
            params.append(self.filtre_statut.get())
        
        query += " ORDER BY Date_Creation DESC"
        
        # Charger les données depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        
        # Appliquer un style selon le niveau d'urgence
        for row in cursor.fetchall():
            tag = row[5].lower()  # Niveau_Urgence comme tag
            self.alertes_tree.insert("", tk.END, values=row, tags=(tag,))
        
        # Configurer les tags pour les couleurs
        self.alertes_tree.tag_configure("critique", background="#ffcccc")
        self.alertes_tree.tag_configure("élevé", background="#ffe6cc")
        self.alertes_tree.tag_configure("moyen", background="#ffffcc")
        self.alertes_tree.tag_configure("faible", background="#e6ffcc")
    
    def filter_alertes(self):
        self.load_alertes()
    
    def reset_filters(self):
        self.filtre_vehicule.set("")
        self.filtre_type.set("")
        self.filtre_urgence.set("")
        self.filtre_statut.set("Active")
        self.load_alertes()
    
    def select_alerte(self, event):
        # Récupérer l'élément sélectionné
        selected_item = self.alertes_tree.focus()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.alertes_tree.item(selected_item, "values")
        if not values:
            return
        
        # Récupérer toutes les données de l'alerte
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM Alertes WHERE ID = ?
        ''', (values[0],))
        
        alerte = cursor.fetchone()
        if not alerte:
            return
        
        # Mettre à jour les détails
        self.current_id = alerte["ID"]
        self.id_alerte.config(text=str(alerte["ID"]))
        self.detail_vehicule.config(text=alerte["ID_Vehicule"])
        self.detail_type.config(text=alerte["Type_Alerte"])
        self.detail_urgence.config(text=alerte["Niveau_Urgence"])
        self.detail_date.config(text=alerte["Date_Creation"])
        self.statut_alerte.set(alerte["Statut"])
        
        # Mettre à jour la description
        self.detail_description.config(state="normal")
        self.detail_description.delete("1.0", tk.END)
        self.detail_description.insert("1.0", alerte["Description"])
        self.detail_description.config(state="disabled")
        
        # Mettre à jour le commentaire
        self.commentaire.delete("1.0", tk.END)
        if alerte["Commentaire"]:
            self.commentaire.insert("1.0", alerte["Commentaire"])
    
    def update_statut(self):
        # Vérifier si une alerte est sélectionnée
        if self.current_id:
            try:
                # Mettre à jour le statut et le commentaire
                cursor = self.conn.cursor()
                cursor.execute('''
                UPDATE Alertes SET
                    Statut = ?,
                    Commentaire = ?,
                    Date_Modification = ?
                WHERE ID = ?
                ''', (
                    self.statut_alerte.get(),
                    self.commentaire.get("1.0", tk.END).strip(),
                    datetime.now().strftime('%Y-%m-%d'),
                    self.current_id
                ))
                
                self.conn.commit()
                messagebox.showinfo("Succès", "Statut de l'alerte mis à jour avec succès")
                self.load_alertes()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une alerte")
    
    def voir_vehicule(self):
        # Vérifier si une alerte est sélectionnée
        if self.current_id:
            vehicule_id = self.detail_vehicule.cget("text")
            if vehicule_id:
                # Afficher les détails du véhicule dans une nouvelle fenêtre
                self.show_vehicule_details(vehicule_id)
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une alerte")
    
    def show_vehicule_details(self, vehicule_id):
        # Créer une nouvelle fenêtre pour les détails du véhicule
        details_window = tk.Toplevel(self)
        details_window.title(f"Détails du véhicule {vehicule_id}")
        details_window.geometry("600x400")
        
        # Récupérer les détails du véhicule
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM Vehicules WHERE ID_Vehicule = ?
        ''', (vehicule_id,))
        
        vehicule = cursor.fetchone()
        if not vehicule:
            messagebox.showerror("Erreur", f"Véhicule {vehicule_id} non trouvé")
            details_window.destroy()
            return
        
        # Afficher les détails
        frame = ttk.Frame(details_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        for key in vehicule.keys():
            if key != "ID" and not key.startswith("sqlite_"):
                ttk.Label(frame, text=f"{key}:", font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=2)
                ttk.Label(frame, text=str(vehicule[key])).grid(row=row, column=1, sticky="w", padx=5, pady=2)
                row += 1
        
        # Récupérer les alertes liées à ce véhicule
        cursor.execute('''
        SELECT Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut
        FROM Alertes
        WHERE ID_Vehicule = ?
        ORDER BY Date_Creation DESC
        ''', (vehicule_id,))
        
        alertes = cursor.fetchall()
        
        # Afficher les alertes liées
        if alertes:
            ttk.Label(frame, text="Alertes associées:", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, sticky="w", padx=5, pady=10)
            row += 1
            
            alertes_tree = ttk.Treeview(frame)
            alertes_tree["columns"] = ("Type", "Description", "Date", "Niveau", "Statut")
            
            alertes_tree.column("#0", width=0, stretch=tk.NO)
            alertes_tree.column("Type", anchor=tk.W, width=100)
            alertes_tree.column("Description", anchor=tk.W, width=200)
            alertes_tree.column("Date", anchor=tk.W, width=80)
            alertes_tree.column("Niveau", anchor=tk.W, width=80)
            alertes_tree.column("Statut", anchor=tk.W, width=80)
            
            alertes_tree.heading("#0", text="", anchor=tk.W)
            alertes_tree.heading("Type", text="Type", anchor=tk.W)
            alertes_tree.heading("Description", text="Description", anchor=tk.W)
            alertes_tree.heading("Date", text="Date", anchor=tk.W)
            alertes_tree.heading("Niveau", text="Niveau", anchor=tk.W)
            alertes_tree.heading("Statut", text="Statut", anchor=tk.W)
            
            alertes_tree.grid(row=row, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
            
            for alerte in alertes:
                alertes_tree.insert("", tk.END, values=alerte)
            
            frame.rowconfigure(row, weight=1)
        
        # Bouton pour fermer
        ttk.Button(frame, text="Fermer", command=details_window.destroy).grid(row=row+1, column=0, columnspan=2, pady=10)
        
        frame.columnconfigure(1, weight=1)
    
    def export_alertes(self):
        """Exporte les alertes filtrées dans un fichier CSV"""
        try:
            import csv
            from tkinter import filedialog
            
            # Demander où enregistrer le fichier
            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Exporter les alertes"
            )
            
            if not file_path:
                return
            
            # Construire la requête SQL avec les filtres
            query = '''
            SELECT ID, ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut, Commentaire
            FROM Alertes
            WHERE 1=1
            '''
            params = []
            
            if self.filtre_vehicule.get():
                query += " AND ID_Vehicule = ?"
                params.append(self.filtre_vehicule.get())
            
            if self.filtre_type.get():
                query += " AND Type_Alerte = ?"
                params.append(self.filtre_type.get())
            
            if self.filtre_urgence.get():
                query += " AND Niveau_Urgence = ?"
                params.append(self.filtre_urgence.get())
            
            if self.filtre_statut.get():
                query += " AND Statut = ?"
                params.append(self.filtre_statut.get())
            
            query += " ORDER BY Date_Creation DESC"
            
            # Récupérer les données
            cursor = self.conn.cursor()
            cursor.execute(query, params)
            alertes = cursor.fetchall()
            
            # Écrire dans le fichier CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # En-têtes
                writer.writerow(["ID", "ID_Vehicule", "Type_Alerte", "Description", "Date_Creation", "Niveau_Urgence", "Statut", "Commentaire"])
                
                # Données
                for alerte in alertes:
                    writer.writerow([alerte["ID"], alerte["ID_Vehicule"], alerte["Type_Alerte"], 
                                    alerte["Description"], alerte["Date_Creation"], 
                                    alerte["Niveau_Urgence"], alerte["Statut"], 
                                    alerte["Commentaire"] or ""])
            
            messagebox.showinfo("Succès", f"Les alertes ont été exportées avec succès vers {file_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur d'exportation", str(e))
