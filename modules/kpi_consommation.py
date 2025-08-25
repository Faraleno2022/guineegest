import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime

class ConsommationFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.load_consommations()
        
    def create_widgets(self):
        # Frame pour le formulaire
        form_frame = ttk.LabelFrame(self, text="Enregistrement des consommations de carburant")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Champs du formulaire
        ttk.Label(form_frame, text="ID Véhicule:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_vehicule = ttk.Combobox(form_frame, width=20)
        self.id_vehicule.grid(row=0, column=1, padx=5, pady=5)
        self.load_vehicules_ids()
        self.id_vehicule.bind("<<ComboboxSelected>>", self.on_vehicule_selected)
        
        ttk.Label(form_frame, text="Date plein 1:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_plein1 = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_plein1.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Km plein 1:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.km_plein1 = ttk.Entry(form_frame, width=20)
        self.km_plein1.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date plein 2:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.date_plein2 = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_plein2.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Km plein 2:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.km_plein2 = ttk.Entry(form_frame, width=20)
        self.km_plein2.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Litres ajoutés:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.litres_ajoutes = ttk.Entry(form_frame, width=20)
        self.litres_ajoutes.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Distance parcourue:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.distance_parcourue = ttk.Entry(form_frame, width=20, state="readonly")
        self.distance_parcourue.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Consommation (L/100km):").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.consommation_100km = ttk.Entry(form_frame, width=20, state="readonly")
        self.consommation_100km.grid(row=1, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Consommation constructeur:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.consommation_constructeur = ttk.Entry(form_frame, width=20)
        self.consommation_constructeur.grid(row=2, column=3, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Écart constructeur:").grid(row=3, column=2, sticky="w", padx=5, pady=5)
        self.ecart_constructeur = ttk.Entry(form_frame, width=20, state="readonly")
        self.ecart_constructeur.grid(row=3, column=3, padx=5, pady=5)
        
        # Bouton pour calculer la consommation
        ttk.Button(form_frame, text="Calculer consommation", command=self.calculer_consommation).grid(row=6, column=0, columnspan=2, pady=10)
        
        # Boutons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_consommation).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_consommation).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_consommation).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Effacer", command=self.clear_form).grid(row=0, column=3, padx=5)
        
        # Tableau des consommations
        table_frame = ttk.LabelFrame(self, text="Liste des consommations de carburant")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.consommations_tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set)
        self.consommations_tree["columns"] = ("ID", "ID_Vehicule", "Date_Plein1", "Km_Plein1", 
                                             "Date_Plein2", "Km_Plein2", "Litres", "Distance", 
                                             "Consommation", "Cons_Constructeur", "Ecart")
        
        # Format des colonnes
        self.consommations_tree.column("#0", width=0, stretch=tk.NO)
        self.consommations_tree.column("ID", anchor=tk.W, width=40)
        self.consommations_tree.column("ID_Vehicule", anchor=tk.W, width=80)
        self.consommations_tree.column("Date_Plein1", anchor=tk.W, width=100)
        self.consommations_tree.column("Km_Plein1", anchor=tk.W, width=80)
        self.consommations_tree.column("Date_Plein2", anchor=tk.W, width=100)
        self.consommations_tree.column("Km_Plein2", anchor=tk.W, width=80)
        self.consommations_tree.column("Litres", anchor=tk.W, width=80)
        self.consommations_tree.column("Distance", anchor=tk.W, width=80)
        self.consommations_tree.column("Consommation", anchor=tk.W, width=100)
        self.consommations_tree.column("Cons_Constructeur", anchor=tk.W, width=120)
        self.consommations_tree.column("Ecart", anchor=tk.W, width=80)
        
        # En-têtes
        self.consommations_tree.heading("#0", text="", anchor=tk.W)
        self.consommations_tree.heading("ID", text="ID", anchor=tk.W)
        self.consommations_tree.heading("ID_Vehicule", text="ID Véhicule", anchor=tk.W)
        self.consommations_tree.heading("Date_Plein1", text="Date plein 1", anchor=tk.W)
        self.consommations_tree.heading("Km_Plein1", text="Km plein 1", anchor=tk.W)
        self.consommations_tree.heading("Date_Plein2", text="Date plein 2", anchor=tk.W)
        self.consommations_tree.heading("Km_Plein2", text="Km plein 2", anchor=tk.W)
        self.consommations_tree.heading("Litres", text="Litres", anchor=tk.W)
        self.consommations_tree.heading("Distance", text="Distance", anchor=tk.W)
        self.consommations_tree.heading("Consommation", text="Conso. (L/100km)", anchor=tk.W)
        self.consommations_tree.heading("Cons_Constructeur", text="Conso. constructeur", anchor=tk.W)
        self.consommations_tree.heading("Ecart", text="Écart", anchor=tk.W)
        
        self.consommations_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.consommations_tree.yview)
        
        # Événement de sélection
        self.consommations_tree.bind("<ButtonRelease-1>", self.select_consommation)
        
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
        # Récupérer les informations du véhicule sélectionné
        vehicule_id = self.id_vehicule.get()
        if vehicule_id:
            cursor = self.conn.cursor()
            
            # Récupérer le dernier kilométrage enregistré
            cursor.execute("""
            SELECT Km_Fin FROM DistancesParcourues 
            WHERE ID_Vehicule = ? 
            ORDER BY Date_Fin DESC LIMIT 1
            """, (vehicule_id,))
            result = cursor.fetchone()
            if result:
                self.km_plein1.delete(0, tk.END)
                self.km_plein1.insert(0, result[0])
            
            # Récupérer la consommation constructeur si elle existe
            cursor.execute("""
            SELECT Consommation_Constructeur FROM ConsommationCarburant 
            WHERE ID_Vehicule = ? 
            ORDER BY Date_Plein2 DESC LIMIT 1
            """, (vehicule_id,))
            result = cursor.fetchone()
            if result and result[0]:
                self.consommation_constructeur.delete(0, tk.END)
                self.consommation_constructeur.insert(0, result[0])
    
    def calculer_consommation(self):
        try:
            km_plein1 = int(self.km_plein1.get())
            km_plein2 = int(self.km_plein2.get())
            litres_ajoutes = float(self.litres_ajoutes.get())
            
            if km_plein2 <= km_plein1:
                messagebox.showerror("Erreur", "Le kilométrage du plein 2 doit être supérieur au kilométrage du plein 1")
                return
            
            if litres_ajoutes <= 0:
                messagebox.showerror("Erreur", "La quantité de carburant ajoutée doit être positive")
                return
            
            # Calcul de la distance parcourue
            distance = km_plein2 - km_plein1
            
            # Calcul de la consommation aux 100 km
            consommation = (litres_ajoutes * 100) / distance
            
            # Mise à jour des champs
            self.distance_parcourue.config(state="normal")
            self.distance_parcourue.delete(0, tk.END)
            self.distance_parcourue.insert(0, distance)
            self.distance_parcourue.config(state="readonly")
            
            self.consommation_100km.config(state="normal")
            self.consommation_100km.delete(0, tk.END)
            self.consommation_100km.insert(0, round(consommation, 2))
            self.consommation_100km.config(state="readonly")
            
            # Calcul de l'écart avec la consommation constructeur
            if self.consommation_constructeur.get():
                try:
                    cons_constructeur = float(self.consommation_constructeur.get())
                    ecart = consommation - cons_constructeur
                    
                    self.ecart_constructeur.config(state="normal")
                    self.ecart_constructeur.delete(0, tk.END)
                    self.ecart_constructeur.insert(0, round(ecart, 2))
                    self.ecart_constructeur.config(state="readonly")
                except ValueError:
                    pass
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides")
    
    def load_consommations(self):
        # Effacer les données existantes
        for item in self.consommations_tree.get_children():
            self.consommations_tree.delete(item)
        
        # Charger les données depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT ID, ID_Vehicule, Date_Plein1, Km_Plein1, Date_Plein2, Km_Plein2, 
               Litres_Ajoutes, Distance_Parcourue, Consommation_100km, 
               Consommation_Constructeur, Ecart_Constructeur
        FROM ConsommationCarburant
        ORDER BY Date_Plein2 DESC
        ''')
        
        for row in cursor.fetchall():
            self.consommations_tree.insert("", tk.END, values=row)
    
    def select_consommation(self, event):
        # Récupérer l'élément sélectionné
        selected_item = self.consommations_tree.focus()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.consommations_tree.item(selected_item, "values")
        if not values:
            return
        
        # Effacer le formulaire
        self.clear_form()
        
        # Remplir le formulaire
        self.current_id = values[0]
        self.id_vehicule.set(values[1])
        
        if values[2]:  # Date_Plein1
            self.date_plein1.set_date(datetime.strptime(values[2], "%Y-%m-%d"))
        
        self.km_plein1.insert(0, values[3])
        
        if values[4]:  # Date_Plein2
            self.date_plein2.set_date(datetime.strptime(values[4], "%Y-%m-%d"))
        
        self.km_plein2.insert(0, values[5])
        self.litres_ajoutes.insert(0, values[6])
        
        self.distance_parcourue.config(state="normal")
        self.distance_parcourue.insert(0, values[7])
        self.distance_parcourue.config(state="readonly")
        
        self.consommation_100km.config(state="normal")
        self.consommation_100km.insert(0, values[8])
        self.consommation_100km.config(state="readonly")
        
        if values[9]:  # Consommation_Constructeur
            self.consommation_constructeur.insert(0, values[9])
        
        if values[10]:  # Ecart_Constructeur
            self.ecart_constructeur.config(state="normal")
            self.ecart_constructeur.insert(0, values[10])
            self.ecart_constructeur.config(state="readonly")
    
    def clear_form(self):
        # Effacer tous les champs
        self.current_id = None
        self.id_vehicule.set("")
        self.km_plein1.delete(0, tk.END)
        self.km_plein2.delete(0, tk.END)
        self.litres_ajoutes.delete(0, tk.END)
        
        self.distance_parcourue.config(state="normal")
        self.distance_parcourue.delete(0, tk.END)
        self.distance_parcourue.config(state="readonly")
        
        self.consommation_100km.config(state="normal")
        self.consommation_100km.delete(0, tk.END)
        self.consommation_100km.config(state="readonly")
        
        self.consommation_constructeur.delete(0, tk.END)
        
        self.ecart_constructeur.config(state="normal")
        self.ecart_constructeur.delete(0, tk.END)
        self.ecart_constructeur.config(state="readonly")
    
    def add_consommation(self):
        # Vérifier les champs obligatoires
        if not self.id_vehicule.get() or not self.km_plein1.get() or not self.km_plein2.get() or not self.litres_ajoutes.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        try:
            # Calculer la consommation si ce n'est pas déjà fait
            if not self.consommation_100km.get():
                self.calculer_consommation()
            
            # Insérer la consommation
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO ConsommationCarburant (
                ID_Vehicule, Date_Plein1, Km_Plein1, Date_Plein2, Km_Plein2, 
                Litres_Ajoutes, Distance_Parcourue, Consommation_100km, 
                Consommation_Constructeur, Ecart_Constructeur
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.id_vehicule.get(),
                self.date_plein1.get(),
                self.km_plein1.get(),
                self.date_plein2.get(),
                self.km_plein2.get(),
                self.litres_ajoutes.get(),
                self.distance_parcourue.get(),
                self.consommation_100km.get(),
                self.consommation_constructeur.get() or None,
                self.ecart_constructeur.get() or None
            ))
            
            self.conn.commit()
            
            # Vérifier si la consommation est anormale
            self.check_consommation_alert(
                self.id_vehicule.get(), 
                float(self.consommation_100km.get()), 
                float(self.consommation_constructeur.get()) if self.consommation_constructeur.get() else 0
            )
            
            messagebox.showinfo("Succès", "Consommation ajoutée avec succès")
            self.clear_form()
            self.load_consommations()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", str(e))
    
    def update_consommation(self):
        # Vérifier si une consommation est sélectionnée
        if self.current_id:
            try:
                # Calculer la consommation si ce n'est pas déjà fait
                if not self.consommation_100km.get():
                    self.calculer_consommation()
                
                # Mettre à jour la consommation
                cursor = self.conn.cursor()
                cursor.execute('''
                UPDATE ConsommationCarburant SET
                    ID_Vehicule = ?, Date_Plein1 = ?, Km_Plein1 = ?, Date_Plein2 = ?, Km_Plein2 = ?,
                    Litres_Ajoutes = ?, Distance_Parcourue = ?, Consommation_100km = ?,
                    Consommation_Constructeur = ?, Ecart_Constructeur = ?
                WHERE ID = ?
                ''', (
                    self.id_vehicule.get(),
                    self.date_plein1.get(),
                    self.km_plein1.get(),
                    self.date_plein2.get(),
                    self.km_plein2.get(),
                    self.litres_ajoutes.get(),
                    self.distance_parcourue.get(),
                    self.consommation_100km.get(),
                    self.consommation_constructeur.get() or None,
                    self.ecart_constructeur.get() or None,
                    self.current_id
                ))
                
                self.conn.commit()
                
                # Vérifier si la consommation est anormale
                self.check_consommation_alert(
                    self.id_vehicule.get(), 
                    float(self.consommation_100km.get()), 
                    float(self.consommation_constructeur.get()) if self.consommation_constructeur.get() else 0
                )
                
                messagebox.showinfo("Succès", "Consommation mise à jour avec succès")
                self.clear_form()
                self.load_consommations()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une consommation")
    
    def delete_consommation(self):
        # Vérifier si une consommation est sélectionnée
        if self.current_id:
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cette consommation ?"):
                try:
                    # Supprimer la consommation
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM ConsommationCarburant WHERE ID = ?", (self.current_id,))
                    self.conn.commit()
                    messagebox.showinfo("Succès", "Consommation supprimée avec succès")
                    self.clear_form()
                    self.load_consommations()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner une consommation")
    
    def check_consommation_alert(self, id_vehicule, consommation, consommation_constructeur):
        """Vérifie si la consommation est anormale et crée une alerte si nécessaire"""
        if consommation_constructeur > 0:
            # Alerte si consommation > norme constructeur + 3 L/100km
            if consommation > (consommation_constructeur + 3):
                # Vérifier si une alerte existe déjà pour ce véhicule ce mois-ci
                current_month = datetime.now().strftime('%Y-%m')
                
                cursor = self.conn.cursor()
                cursor.execute('''
                SELECT COUNT(*) FROM Alertes
                WHERE ID_Vehicule = ? AND Type_Alerte = 'Consommation' AND Date_Creation LIKE ?
                AND Statut = 'Active'
                ''', (id_vehicule, f"{current_month}%"))
                
                if cursor.fetchone()[0] == 0:
                    # Créer une nouvelle alerte
                    cursor.execute('''
                    INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        id_vehicule,
                        'Consommation',
                        f"Consommation anormale: {consommation:.2f} L/100km (norme: {consommation_constructeur:.2f} L/100km)",
                        datetime.now().strftime('%Y-%m-%d'),
                        'Moyen',
                        'Active'
                    ))
                    
                    self.conn.commit()
                    messagebox.warning("Alerte", f"Attention: Consommation anormale pour le véhicule {id_vehicule}!")
            
            # Vérifier les variations soudaines de consommation
            cursor = self.conn.cursor()
            cursor.execute('''
            SELECT AVG(Consommation_100km) FROM ConsommationCarburant
            WHERE ID_Vehicule = ? AND ID != ?
            ORDER BY Date_Plein2 DESC LIMIT 3
            ''', (id_vehicule, self.current_id or 0))
            
            result = cursor.fetchone()
            if result[0]:
                avg_consommation = result[0]
                # Si la consommation actuelle est 20% supérieure à la moyenne des 3 dernières
                if consommation > (avg_consommation * 1.2):
                    # Vérifier si une alerte existe déjà pour ce véhicule ce mois-ci
                    current_month = datetime.now().strftime('%Y-%m')
                    
                    cursor.execute('''
                    SELECT COUNT(*) FROM Alertes
                    WHERE ID_Vehicule = ? AND Type_Alerte = 'Variation Consommation' AND Date_Creation LIKE ?
                    AND Statut = 'Active'
                    ''', (id_vehicule, f"{current_month}%"))
                    
                    if cursor.fetchone()[0] == 0:
                        # Créer une nouvelle alerte
                        cursor.execute('''
                        INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            id_vehicule,
                            'Variation Consommation',
                            f"Variation soudaine de consommation: {consommation:.2f} L/100km (moyenne: {avg_consommation:.2f} L/100km)",
                            datetime.now().strftime('%Y-%m-%d'),
                            'Moyen',
                            'Active'
                        ))
                        
                        self.conn.commit()
                        messagebox.warning("Alerte", f"Attention: Variation soudaine de consommation pour le véhicule {id_vehicule}!")
