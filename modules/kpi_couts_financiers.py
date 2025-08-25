import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime

class CoutsFinanciersFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.load_couts()
        
    def create_widgets(self):
        # Frame pour le formulaire
        form_frame = ttk.LabelFrame(self, text="Enregistrement des coûts financiers")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Champs du formulaire
        ttk.Label(form_frame, text="ID Véhicule:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_vehicule = ttk.Combobox(form_frame, width=20)
        self.id_vehicule.grid(row=0, column=1, padx=5, pady=5)
        self.load_vehicules_ids()
        self.id_vehicule.bind("<<ComboboxSelected>>", self.on_vehicule_selected)
        
        ttk.Label(form_frame, text="Date:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.date_cout = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_cout.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Type de coût:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.type_cout = ttk.Combobox(form_frame, values=["Achat", "Leasing", "Amortissement", "Intérêts", "Dépréciation", "Autre"], width=17)
        self.type_cout.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Montant (€):").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.montant = ttk.Entry(form_frame, width=20)
        self.montant.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Kilométrage:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.kilometrage = ttk.Entry(form_frame, width=20)
        self.kilometrage.grid(row=4, column=1, padx=5, pady=5)
        self.kilometrage.bind("<KeyRelease>", self.calculer_cout_km)
        
        ttk.Label(form_frame, text="Coût par km (€):").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.cout_km = ttk.Entry(form_frame, width=20, state="readonly")
        self.cout_km.grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Période d'amortissement (mois):").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.periode_amortissement = ttk.Entry(form_frame, width=20)
        self.periode_amortissement.grid(row=6, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Description:").grid(row=7, column=0, sticky="w", padx=5, pady=5)
        self.description = tk.Text(form_frame, width=40, height=3)
        self.description.grid(row=7, column=1, columnspan=2, padx=5, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=8, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_cout).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_cout).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_cout).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Effacer", command=self.clear_form).grid(row=0, column=3, padx=5)
        
        # Tableau des coûts
        table_frame = ttk.LabelFrame(self, text="Liste des coûts financiers")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.couts_tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set)
        self.couts_tree["columns"] = ("ID", "ID_Vehicule", "Date", "Type_Cout", "Montant", "Kilometrage", "Cout_Km", "Periode_Amortissement")
        
        # Format des colonnes
        self.couts_tree.column("#0", width=0, stretch=tk.NO)
        self.couts_tree.column("ID", anchor=tk.W, width=40)
        self.couts_tree.column("ID_Vehicule", anchor=tk.W, width=100)
        self.couts_tree.column("Date", anchor=tk.W, width=100)
        self.couts_tree.column("Type_Cout", anchor=tk.W, width=100)
        self.couts_tree.column("Montant", anchor=tk.W, width=100)
        self.couts_tree.column("Kilometrage", anchor=tk.W, width=100)
        self.couts_tree.column("Cout_Km", anchor=tk.W, width=100)
        self.couts_tree.column("Periode_Amortissement", anchor=tk.W, width=150)
        
        # En-têtes
        self.couts_tree.heading("#0", text="", anchor=tk.W)
        self.couts_tree.heading("ID", text="ID", anchor=tk.W)
        self.couts_tree.heading("ID_Vehicule", text="ID Véhicule", anchor=tk.W)
        self.couts_tree.heading("Date", text="Date", anchor=tk.W)
        self.couts_tree.heading("Type_Cout", text="Type de coût", anchor=tk.W)
        self.couts_tree.heading("Montant", text="Montant (€)", anchor=tk.W)
        self.couts_tree.heading("Kilometrage", text="Kilométrage", anchor=tk.W)
        self.couts_tree.heading("Cout_Km", text="Coût/km (€)", anchor=tk.W)
        self.couts_tree.heading("Periode_Amortissement", text="Période amort. (mois)", anchor=tk.W)
        
        self.couts_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.couts_tree.yview)
        
        # Événement de sélection
        self.couts_tree.bind("<ButtonRelease-1>", self.select_cout)
        
        # Configuration du grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # ID caché pour les mises à jour
        self.current_id = None
        
        # Dictionnaire pour stocker les seuils de coût par type de véhicule
        self.seuils_cout = {
            "Berline": 0.10,  # €/km pour les coûts financiers
            "SUV": 0.12,
            "Utilitaire": 0.15,
            "Camion": 0.20
        }
    
    def load_vehicules_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Vehicule FROM Vehicules ORDER BY ID_Vehicule")
        vehicules = [row[0] for row in cursor.fetchall()]
        self.id_vehicule['values'] = vehicules
    
    def on_vehicule_selected(self, event):
        # Récupérer le dernier kilométrage connu pour ce véhicule
        vehicule_id = self.id_vehicule.get()
        if vehicule_id:
            cursor = self.conn.cursor()
            
            # Chercher d'abord dans la table DistancesParcourues
            cursor.execute("""
            SELECT Kilometrage_Final FROM DistancesParcourues 
            WHERE ID_Vehicule = ? 
            ORDER BY Date_Fin DESC LIMIT 1
            """, (vehicule_id,))
            
            result = cursor.fetchone()
            if result:
                self.kilometrage.delete(0, tk.END)
                self.kilometrage.insert(0, result[0])
            else:
                # Si pas trouvé, chercher dans la table Vehicules
                cursor.execute("""
                SELECT Kilometrage_Initial FROM Vehicules 
                WHERE ID_Vehicule = ?
                """, (vehicule_id,))
                
                result = cursor.fetchone()
                if result:
                    self.kilometrage.delete(0, tk.END)
                    self.kilometrage.insert(0, result[0])
            
            # Pré-remplir la période d'amortissement en fonction du type de véhicule
            cursor.execute("""
            SELECT Type FROM Vehicules 
            WHERE ID_Vehicule = ?
            """, (vehicule_id,))
            
            result = cursor.fetchone()
            if result:
                type_vehicule = result[0]
                periode = 36  # Valeur par défaut (3 ans)
                
                if type_vehicule == "Berline":
                    periode = 48  # 4 ans
                elif type_vehicule == "SUV":
                    periode = 60  # 5 ans
                elif type_vehicule == "Utilitaire":
                    periode = 36  # 3 ans
                elif type_vehicule == "Camion":
                    periode = 72  # 6 ans
                
                self.periode_amortissement.delete(0, tk.END)
                self.periode_amortissement.insert(0, periode)
    
    def calculer_cout_km(self, event):
        try:
            montant_str = self.montant.get()
            kilometrage_str = self.kilometrage.get()
            
            if montant_str and kilometrage_str:
                montant = float(montant_str)
                kilometrage = float(kilometrage_str)
                
                # Récupérer le kilométrage initial du véhicule
                cursor = self.conn.cursor()
                cursor.execute("""
                SELECT Kilometrage_Initial FROM Vehicules 
                WHERE ID_Vehicule = ?
                """, (self.id_vehicule.get(),))
                
                result = cursor.fetchone()
                if result:
                    kilometrage_initial = float(result[0])
                    distance_parcourue = kilometrage - kilometrage_initial
                    
                    if distance_parcourue > 0:
                        cout_km = montant / distance_parcourue
                        
                        # Mettre à jour le champ cout_km
                        self.cout_km.config(state="normal")
                        self.cout_km.delete(0, tk.END)
                        self.cout_km.insert(0, round(cout_km, 4))
                        self.cout_km.config(state="readonly")
                    else:
                        self.cout_km.config(state="normal")
                        self.cout_km.delete(0, tk.END)
                        self.cout_km.insert(0, "N/A")
                        self.cout_km.config(state="readonly")
                
        except (ValueError, ZeroDivisionError):
            self.cout_km.config(state="normal")
            self.cout_km.delete(0, tk.END)
            self.cout_km.insert(0, "N/A")
            self.cout_km.config(state="readonly")
    
    def load_couts(self):
        # Effacer les données existantes
        for item in self.couts_tree.get_children():
            self.couts_tree.delete(item)
        
        # Charger les données depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT ID, ID_Vehicule, Date, Type_Cout, Montant, Kilometrage, Cout_Par_Km, Periode_Amortissement
        FROM CoutsFinanciers
        ORDER BY Date DESC
        ''')
        
        for row in cursor.fetchall():
            self.couts_tree.insert("", tk.END, values=row)
    
    def select_cout(self, event):
        # Récupérer l'élément sélectionné
        selected_item = self.couts_tree.focus()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.couts_tree.item(selected_item, "values")
        if not values:
            return
        
        # Effacer le formulaire
        self.clear_form()
        
        # Récupérer toutes les données du coût
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM CoutsFinanciers WHERE ID = ?
        ''', (values[0],))
        
        cout = cursor.fetchone()
        if not cout:
            return
        
        # Remplir le formulaire
        self.current_id = cout["ID"]
        self.id_vehicule.set(cout["ID_Vehicule"])
        
        if cout["Date"]:
            self.date_cout.set_date(datetime.strptime(cout["Date"], "%Y-%m-%d"))
        
        self.type_cout.set(cout["Type_Cout"])
        self.montant.delete(0, tk.END)
        self.montant.insert(0, cout["Montant"])
        self.kilometrage.delete(0, tk.END)
        self.kilometrage.insert(0, cout["Kilometrage"])
        
        self.cout_km.config(state="normal")
        self.cout_km.delete(0, tk.END)
        self.cout_km.insert(0, cout["Cout_Km"])
        self.cout_km.config(state="readonly")
        
        self.periode_amortissement.delete(0, tk.END)
        if cout["Periode_Amortissement"]:
            self.periode_amortissement.insert(0, cout["Periode_Amortissement"])
        
        self.description.delete("1.0", tk.END)
        self.description.insert("1.0", cout["Description"] or "")
    
    def clear_form(self):
        # Effacer tous les champs
        self.current_id = None
        self.id_vehicule.set("")
        self.type_cout.set("")
        self.montant.delete(0, tk.END)
        self.kilometrage.delete(0, tk.END)
        
        self.cout_km.config(state="normal")
        self.cout_km.delete(0, tk.END)
        self.cout_km.config(state="readonly")
        
        self.periode_amortissement.delete(0, tk.END)
        self.description.delete("1.0", tk.END)
    
    def add_cout(self):
        # Vérifier les champs obligatoires
        if not self.id_vehicule.get() or not self.type_cout.get() or not self.montant.get() or not self.kilometrage.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        try:
            # Calculer le coût par km si ce n'est pas déjà fait
            if not self.cout_km.get():
                self.calculer_cout_km(None)
            
            # Insérer le coût
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO CoutsFinanciers (
                ID_Vehicule, Date, Type_Cout, Montant, Kilometrage, Cout_Km, Periode_Amortissement, Description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.id_vehicule.get(),
                self.date_cout.get(),
                self.type_cout.get(),
                float(self.montant.get()),
                float(self.kilometrage.get()),
                self.cout_km.get() if self.cout_km.get() != "N/A" else None,
                int(self.periode_amortissement.get()) if self.periode_amortissement.get() else None,
                self.description.get("1.0", tk.END).strip()
            ))
            
            self.conn.commit()
            
            # Vérifier si le coût est anormal
            self.check_cout_alert(
                self.id_vehicule.get(),
                self.type_cout.get(),
                float(self.montant.get()),
                float(self.kilometrage.get()),
                float(self.cout_km.get()) if self.cout_km.get() != "N/A" else None
            )
            
            messagebox.showinfo("Succès", "Coût financier ajouté avec succès")
            self.clear_form()
            self.load_couts()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", str(e))
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides pour le montant et le kilométrage")
    
    def update_cout(self):
        # Vérifier si un coût est sélectionné
        if self.current_id:
            try:
                # Calculer le coût par km si ce n'est pas déjà fait
                if not self.cout_km.get():
                    self.calculer_cout_km(None)
                
                # Mettre à jour le coût
                cursor = self.conn.cursor()
                cursor.execute('''
                UPDATE CoutsFinanciers SET
                    ID_Vehicule = ?, Date = ?, Type_Cout = ?, Montant = ?, 
                    Kilometrage = ?, Cout_Km = ?, Periode_Amortissement = ?, Description = ?
                WHERE ID = ?
                ''', (
                    self.id_vehicule.get(),
                    self.date_cout.get(),
                    self.type_cout.get(),
                    float(self.montant.get()),
                    float(self.kilometrage.get()),
                    self.cout_km.get() if self.cout_km.get() != "N/A" else None,
                    int(self.periode_amortissement.get()) if self.periode_amortissement.get() else None,
                    self.description.get("1.0", tk.END).strip(),
                    self.current_id
                ))
                
                self.conn.commit()
                
                # Vérifier si le coût est anormal
                self.check_cout_alert(
                    self.id_vehicule.get(),
                    self.type_cout.get(),
                    float(self.montant.get()),
                    float(self.kilometrage.get()),
                    float(self.cout_km.get()) if self.cout_km.get() != "N/A" else None
                )
                
                messagebox.showinfo("Succès", "Coût financier mis à jour avec succès")
                self.clear_form()
                self.load_couts()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erreur de base de données", str(e))
            except ValueError:
                messagebox.showerror("Erreur", "Veuillez entrer des valeurs numériques valides pour le montant et le kilométrage")
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un coût")
    
    def delete_cout(self):
        # Vérifier si un coût est sélectionné
        if self.current_id:
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce coût financier ?"):
                try:
                    # Supprimer le coût
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM CoutsFinanciers WHERE ID = ?", (self.current_id,))
                    self.conn.commit()
                    messagebox.showinfo("Succès", "Coût financier supprimé avec succès")
                    self.clear_form()
                    self.load_couts()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un coût")
    
    def check_cout_alert(self, id_vehicule, type_cout, montant, kilometrage, cout_km):
        """Vérifie si le coût financier est anormal et crée une alerte si nécessaire"""
        if cout_km is None:
            return
        
        cursor = self.conn.cursor()
        
        # Récupérer le type de véhicule
        cursor.execute("""
        SELECT Type FROM Vehicules WHERE ID_Vehicule = ?
        """, (id_vehicule,))
        
        result = cursor.fetchone()
        if not result:
            return
        
        type_vehicule = result[0]
        
        # Vérifier si le coût dépasse le seuil pour ce type de véhicule
        seuil = self.seuils_cout.get(type_vehicule, 0.10)  # Valeur par défaut si type inconnu
        
        if cout_km > seuil * 1.3:  # 30% au-dessus du seuil
            # Créer une alerte
            cursor.execute('''
            INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                id_vehicule,
                'Coût financier excessif',
                f"Coût financier élevé ({cout_km:.4f} €/km) pour {type_cout} le {self.date_cout.get()}",
                datetime.now().strftime('%Y-%m-%d'),
                'Élevé',
                'Active'
            ))
            
            self.conn.commit()
            messagebox.warning("Alerte", f"Attention: Coût financier élevé pour le véhicule {id_vehicule}!")
