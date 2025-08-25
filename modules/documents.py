import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from tkcalendar import DateEntry
from datetime import datetime, timedelta
import os
import shutil

class DocumentsFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        self.load_documents()
        
        # Créer le dossier pour stocker les documents si nécessaire
        self.documents_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "documents")
        if not os.path.exists(self.documents_folder):
            os.makedirs(self.documents_folder)
        
    def create_widgets(self):
        # Frame pour le formulaire
        form_frame = ttk.LabelFrame(self, text="Gestion des documents administratifs")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Champs du formulaire
        ttk.Label(form_frame, text="ID Véhicule:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.id_vehicule = ttk.Combobox(form_frame, width=20)
        self.id_vehicule.grid(row=0, column=1, padx=5, pady=5)
        self.load_vehicules_ids()
        
        ttk.Label(form_frame, text="Type de document:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.type_document = ttk.Combobox(form_frame, values=[
            "Carte grise", "Assurance", "Contrôle technique", "Vignette", 
            "Permis de conduire", "Certificat d'entretien", "Autre"
        ], width=20)
        self.type_document.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Numéro:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.numero = ttk.Entry(form_frame, width=20)
        self.numero.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date d'émission:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.date_emission = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_emission.grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Date d'expiration:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.date_expiration = DateEntry(form_frame, width=17, background='darkblue', foreground='white', date_pattern='yyyy-mm-dd')
        self.date_expiration.grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Fichier:").grid(row=5, column=0, sticky="w", padx=5, pady=5)
        file_frame = ttk.Frame(form_frame)
        file_frame.grid(row=5, column=1, padx=5, pady=5, sticky="w")
        
        self.fichier_path = ttk.Entry(file_frame, width=30)
        self.fichier_path.pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(file_frame, text="Parcourir", command=self.browse_file).pack(side=tk.LEFT)
        
        ttk.Label(form_frame, text="Commentaires:").grid(row=6, column=0, sticky="w", padx=5, pady=5)
        self.commentaires = tk.Text(form_frame, width=40, height=3)
        self.commentaires.grid(row=6, column=1, columnspan=2, padx=5, pady=5)
        
        # Boutons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=7, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Ajouter", command=self.add_document).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Modifier", command=self.update_document).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Supprimer", command=self.delete_document).grid(row=0, column=2, padx=5)
        ttk.Button(button_frame, text="Effacer", command=self.clear_form).grid(row=0, column=3, padx=5)
        ttk.Button(button_frame, text="Ouvrir", command=self.open_document).grid(row=0, column=4, padx=5)
        
        # Tableau des documents
        table_frame = ttk.LabelFrame(self, text="Liste des documents administratifs")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        self.documents_tree = ttk.Treeview(table_frame, yscrollcommand=scrollbar.set)
        self.documents_tree["columns"] = ("ID", "ID_Vehicule", "Type_Document", "Numero", "Date_Emission", "Date_Expiration", "Fichier")
        
        # Format des colonnes
        self.documents_tree.column("#0", width=0, stretch=tk.NO)
        self.documents_tree.column("ID", anchor=tk.W, width=40)
        self.documents_tree.column("ID_Vehicule", anchor=tk.W, width=100)
        self.documents_tree.column("Type_Document", anchor=tk.W, width=120)
        self.documents_tree.column("Numero", anchor=tk.W, width=120)
        self.documents_tree.column("Date_Emission", anchor=tk.W, width=100)
        self.documents_tree.column("Date_Expiration", anchor=tk.W, width=100)
        self.documents_tree.column("Fichier", anchor=tk.W, width=200)
        
        # En-têtes
        self.documents_tree.heading("#0", text="", anchor=tk.W)
        self.documents_tree.heading("ID", text="ID", anchor=tk.W)
        self.documents_tree.heading("ID_Vehicule", text="ID Véhicule", anchor=tk.W)
        self.documents_tree.heading("Type_Document", text="Type de document", anchor=tk.W)
        self.documents_tree.heading("Numero", text="Numéro", anchor=tk.W)
        self.documents_tree.heading("Date_Emission", text="Date d'émission", anchor=tk.W)
        self.documents_tree.heading("Date_Expiration", text="Date d'expiration", anchor=tk.W)
        self.documents_tree.heading("Fichier", text="Fichier", anchor=tk.W)
        
        self.documents_tree.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.documents_tree.yview)
        
        # Événement de sélection
        self.documents_tree.bind("<ButtonRelease-1>", self.select_document)
        
        # Configuration du grid
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        
        # ID caché pour les mises à jour
        self.current_id = None
        self.current_file_path = None
    
    def load_vehicules_ids(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Vehicule FROM Vehicules ORDER BY ID_Vehicule")
        vehicules = [row[0] for row in cursor.fetchall()]
        self.id_vehicule['values'] = vehicules
    
    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="Sélectionner un document",
            filetypes=[
                ("Documents", "*.pdf;*.doc;*.docx;*.jpg;*.jpeg;*.png"),
                ("PDF", "*.pdf"),
                ("Word", "*.doc;*.docx"),
                ("Images", "*.jpg;*.jpeg;*.png"),
                ("Tous les fichiers", "*.*")
            ]
        )
        
        if file_path:
            self.fichier_path.delete(0, tk.END)
            self.fichier_path.insert(0, file_path)
    
    def load_documents(self):
        # Effacer les données existantes
        for item in self.documents_tree.get_children():
            self.documents_tree.delete(item)
        
        # Charger les données depuis la base de données
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT ID, ID_Vehicule, Type_Document, Numero, Date_Emission, Date_Expiration, Fichier
        FROM DocumentsAdministratifs
        ORDER BY Date_Expiration
        ''')
        
        for row in cursor.fetchall():
            # Appliquer un style selon la date d'expiration
            expiration_date = datetime.strptime(row[5], "%Y-%m-%d") if row[5] else None
            
            if expiration_date:
                today = datetime.now()
                days_left = (expiration_date - today).days
                
                if days_left < 0:
                    tag = "expired"
                elif days_left < 30:
                    tag = "expiring_soon"
                else:
                    tag = "valid"
            else:
                tag = "valid"
            
            self.documents_tree.insert("", tk.END, values=row, tags=(tag,))
        
        # Configurer les tags pour les couleurs
        self.documents_tree.tag_configure("expired", background="#ffcccc")
        self.documents_tree.tag_configure("expiring_soon", background="#ffffcc")
        self.documents_tree.tag_configure("valid", background="#e6ffcc")
        
        # Vérifier les documents qui expirent bientôt et créer des alertes
        self.check_expiring_documents()
    
    def select_document(self, event):
        # Récupérer l'élément sélectionné
        selected_item = self.documents_tree.focus()
        if not selected_item:
            return
        
        # Récupérer les valeurs
        values = self.documents_tree.item(selected_item, "values")
        if not values:
            return
        
        # Effacer le formulaire
        self.clear_form()
        
        # Récupérer toutes les données du document
        cursor = self.conn.cursor()
        cursor.execute('''
        SELECT * FROM DocumentsAdministratifs WHERE ID = ?
        ''', (values[0],))
        
        document = cursor.fetchone()
        if not document:
            return
        
        # Remplir le formulaire
        self.current_id = document["ID"]
        self.id_vehicule.set(document["ID_Vehicule"])
        self.type_document.set(document["Type_Document"])
        self.numero.insert(0, document["Numero"] or "")
        
        if document["Date_Emission"]:
            self.date_emission.set_date(datetime.strptime(document["Date_Emission"], "%Y-%m-%d"))
        
        if document["Date_Expiration"]:
            self.date_expiration.set_date(datetime.strptime(document["Date_Expiration"], "%Y-%m-%d"))
        
        self.fichier_path.insert(0, document["Fichier"] or "")
        self.current_file_path = document["Fichier"]
        
        self.commentaires.insert("1.0", document["Commentaires"] or "")
    
    def clear_form(self):
        # Effacer tous les champs
        self.current_id = None
        self.current_file_path = None
        self.id_vehicule.set("")
        self.type_document.set("")
        self.numero.delete(0, tk.END)
        self.fichier_path.delete(0, tk.END)
        self.commentaires.delete("1.0", tk.END)
    
    def add_document(self):
        # Vérifier les champs obligatoires
        if not self.id_vehicule.get() or not self.type_document.get():
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs obligatoires")
            return
        
        try:
            # Copier le fichier dans le dossier documents si un fichier est spécifié
            fichier_destination = None
            if self.fichier_path.get():
                fichier_source = self.fichier_path.get()
                if os.path.exists(fichier_source):
                    # Créer un sous-dossier pour le véhicule si nécessaire
                    vehicule_folder = os.path.join(self.documents_folder, self.id_vehicule.get())
                    if not os.path.exists(vehicule_folder):
                        os.makedirs(vehicule_folder)
                    
                    # Générer un nom de fichier unique
                    fichier_nom = f"{self.type_document.get().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(fichier_source)[1]}"
                    fichier_destination = os.path.join(vehicule_folder, fichier_nom)
                    
                    # Copier le fichier
                    shutil.copy2(fichier_source, fichier_destination)
            
            # Insérer le document
            cursor = self.conn.cursor()
            cursor.execute('''
            INSERT INTO DocumentsAdministratifs (
                ID_Vehicule, Type_Document, Numero, Date_Emission, Date_Expiration, Fichier, Commentaires
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.id_vehicule.get(),
                self.type_document.get(),
                self.numero.get(),
                self.date_emission.get(),
                self.date_expiration.get(),
                fichier_destination,
                self.commentaires.get("1.0", tk.END).strip()
            ))
            
            self.conn.commit()
            
            # Vérifier si le document expire bientôt
            self.check_document_expiration(
                self.id_vehicule.get(),
                self.type_document.get(),
                self.date_expiration.get()
            )
            
            messagebox.showinfo("Succès", "Document ajouté avec succès")
            self.clear_form()
            self.load_documents()
            
        except sqlite3.Error as e:
            messagebox.showerror("Erreur de base de données", str(e))
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    
    def update_document(self):
        # Vérifier si un document est sélectionné
        if self.current_id:
            try:
                # Gérer le fichier si un nouveau fichier est spécifié
                fichier_destination = self.current_file_path
                if self.fichier_path.get() and self.fichier_path.get() != self.current_file_path:
                    fichier_source = self.fichier_path.get()
                    if os.path.exists(fichier_source):
                        # Créer un sous-dossier pour le véhicule si nécessaire
                        vehicule_folder = os.path.join(self.documents_folder, self.id_vehicule.get())
                        if not os.path.exists(vehicule_folder):
                            os.makedirs(vehicule_folder)
                        
                        # Générer un nom de fichier unique
                        fichier_nom = f"{self.type_document.get().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}{os.path.splitext(fichier_source)[1]}"
                        fichier_destination = os.path.join(vehicule_folder, fichier_nom)
                        
                        # Copier le fichier
                        shutil.copy2(fichier_source, fichier_destination)
                        
                        # Supprimer l'ancien fichier si nécessaire
                        if self.current_file_path and os.path.exists(self.current_file_path):
                            try:
                                os.remove(self.current_file_path)
                            except:
                                pass
                
                # Mettre à jour le document
                cursor = self.conn.cursor()
                cursor.execute('''
                UPDATE DocumentsAdministratifs SET
                    ID_Vehicule = ?, Type_Document = ?, Numero = ?, 
                    Date_Emission = ?, Date_Expiration = ?, Fichier = ?, Commentaires = ?
                WHERE ID = ?
                ''', (
                    self.id_vehicule.get(),
                    self.type_document.get(),
                    self.numero.get(),
                    self.date_emission.get(),
                    self.date_expiration.get(),
                    fichier_destination,
                    self.commentaires.get("1.0", tk.END).strip(),
                    self.current_id
                ))
                
                self.conn.commit()
                
                # Vérifier si le document expire bientôt
                self.check_document_expiration(
                    self.id_vehicule.get(),
                    self.type_document.get(),
                    self.date_expiration.get()
                )
                
                messagebox.showinfo("Succès", "Document mis à jour avec succès")
                self.clear_form()
                self.load_documents()
                
            except sqlite3.Error as e:
                messagebox.showerror("Erreur de base de données", str(e))
            except Exception as e:
                messagebox.showerror("Erreur", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un document")
    
    def delete_document(self):
        # Vérifier si un document est sélectionné
        if self.current_id:
            if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer ce document ?"):
                try:
                    # Supprimer le fichier si nécessaire
                    if self.current_file_path and os.path.exists(self.current_file_path):
                        try:
                            os.remove(self.current_file_path)
                        except:
                            pass
                    
                    # Supprimer le document
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM DocumentsAdministratifs WHERE ID = ?", (self.current_id,))
                    self.conn.commit()
                    messagebox.showinfo("Succès", "Document supprimé avec succès")
                    self.clear_form()
                    self.load_documents()
                    
                except sqlite3.Error as e:
                    messagebox.showerror("Erreur de base de données", str(e))
        else:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un document")
    
    def open_document(self):
        # Vérifier si un document est sélectionné
        selected_item = self.documents_tree.focus()
        if not selected_item:
            messagebox.showerror("Erreur", "Veuillez d'abord sélectionner un document")
            return
        
        # Récupérer le chemin du fichier
        values = self.documents_tree.item(selected_item, "values")
        if not values or not values[6]:
            messagebox.showerror("Erreur", "Aucun fichier associé à ce document")
            return
        
        fichier = values[6]
        
        # Vérifier si le fichier existe
        if not os.path.exists(fichier):
            messagebox.showerror("Erreur", "Le fichier n'existe pas")
            return
        
        # Ouvrir le fichier avec l'application par défaut
        try:
            import subprocess
            if os.name == 'nt':  # Windows
                os.startfile(fichier)
            elif os.name == 'posix':  # macOS, Linux
                subprocess.call(('xdg-open', fichier))
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier: {str(e)}")
    
    def check_expiring_documents(self):
        """Vérifie tous les documents qui expirent bientôt et crée des alertes"""
        today = datetime.now()
        cursor = self.conn.cursor()
        
        # Récupérer tous les documents qui expirent dans les 30 jours
        cursor.execute('''
        SELECT ID_Vehicule, Type_Document, Date_Expiration
        FROM DocumentsAdministratifs
        WHERE Date_Expiration IS NOT NULL
        ''')
        
        for document in cursor.fetchall():
            self.check_document_expiration(
                document["ID_Vehicule"],
                document["Type_Document"],
                document["Date_Expiration"]
            )
    
    def check_document_expiration(self, id_vehicule, type_document, date_expiration):
        """Vérifie si un document expire bientôt et crée une alerte si nécessaire"""
        if not date_expiration:
            return
        
        try:
            expiration_date = datetime.strptime(date_expiration, "%Y-%m-%d")
            today = datetime.now()
            days_left = (expiration_date - today).days
            
            cursor = self.conn.cursor()
            
            # Document expiré
            if days_left < 0:
                # Vérifier si une alerte existe déjà
                cursor.execute('''
                SELECT COUNT(*) FROM Alertes
                WHERE ID_Vehicule = ? AND Type_Alerte = 'Document expiré' AND Description LIKE ?
                AND Statut = 'Active'
                ''', (id_vehicule, f"%{type_document}%"))
                
                if cursor.fetchone()[0] == 0:
                    # Créer une alerte
                    cursor.execute('''
                    INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        id_vehicule,
                        'Document expiré',
                        f"Le document {type_document} a expiré le {date_expiration}",
                        datetime.now().strftime('%Y-%m-%d'),
                        'Critique',
                        'Active'
                    ))
                    
                    self.conn.commit()
                    messagebox.warning("Alerte", f"Attention: Le document {type_document} pour le véhicule {id_vehicule} a expiré!")
            
            # Document qui expire bientôt (dans les 30 jours)
            elif days_left <= 30:
                # Vérifier si une alerte existe déjà
                cursor.execute('''
                SELECT COUNT(*) FROM Alertes
                WHERE ID_Vehicule = ? AND Type_Alerte = 'Document expirant' AND Description LIKE ?
                AND Statut = 'Active'
                ''', (id_vehicule, f"%{type_document}%"))
                
                if cursor.fetchone()[0] == 0:
                    # Créer une alerte
                    cursor.execute('''
                    INSERT INTO Alertes (ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ''', (
                        id_vehicule,
                        'Document expirant',
                        f"Le document {type_document} expire dans {days_left} jours ({date_expiration})",
                        datetime.now().strftime('%Y-%m-%d'),
                        'Élevé',
                        'Active'
                    ))
                    
                    self.conn.commit()
                    messagebox.warning("Alerte", f"Attention: Le document {type_document} pour le véhicule {id_vehicule} expire dans {days_left} jours!")
        
        except Exception as e:
            print(f"Erreur lors de la vérification de l'expiration du document: {str(e)}")
