"""
Module de gestion des notifications par email.

Ce module permet de configurer et d'envoyer des notifications par email à partir d'une application Tkinter.
Il utilise la bibliothèque smtplib pour envoyer les emails et la bibliothèque json pour stocker les paramètres de configuration.

Auteur : [Votre nom]
Date : [Votre date]
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import threading
import time
import json
import os

class NotificationsFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.config_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "email_config.json")
        self.load_config()
        self.create_widgets()
        
    def load_config(self):
        # Charger la configuration email ou créer une configuration par défaut
        self.config = {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "username": "",
            "password": "",
            "from_email": "",
            "recipients": [],
            "notification_levels": ["Critique", "Élevé"],
            "enabled": False,
            "check_interval": 3600  # en secondes (1 heure)
        }
        
        # Créer le dossier config s'il n'existe pas
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if not os.path.exists(os.path.join(config_dir, "config")):
                os.makedirs(os.path.join(config_dir, "config"))
            
        # Charger la configuration existante si elle existe
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    self.config.update(loaded_config)
            except Exception as e:
                messagebox.showerror("Erreur", f"Impossible de charger la configuration email: {str(e)}")
                
    def save_config(self):
        # Enregistrer la configuration dans le fichier
        config_dir = os.path.dirname(self.config_file)
        if not os.path.exists(config_dir):
            config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            if not os.path.exists(os.path.join(config_dir, "config")):
                os.makedirs(os.path.join(config_dir, "config"))
            
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'enregistrer la configuration email: {str(e)}")
            
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Configuration des Notifications Email", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame pour la configuration SMTP
        smtp_frame = ttk.LabelFrame(main_frame, text="Configuration du serveur SMTP")
        smtp_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Serveur SMTP
        ttk.Label(smtp_frame, text="Serveur SMTP:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.smtp_server = ttk.Entry(smtp_frame, width=30)
        self.smtp_server.grid(row=0, column=1, padx=5, pady=5)
        self.smtp_server.insert(0, self.config["smtp_server"])
        
        # Port SMTP
        ttk.Label(smtp_frame, text="Port SMTP:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.smtp_port = ttk.Entry(smtp_frame, width=10)
        self.smtp_port.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.smtp_port.insert(0, str(self.config["smtp_port"]))
        
        # Nom d'utilisateur
        ttk.Label(smtp_frame, text="Nom d'utilisateur:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.username = ttk.Entry(smtp_frame, width=30)
        self.username.grid(row=2, column=1, padx=5, pady=5)
        self.username.insert(0, self.config["username"])
        
        # Mot de passe
        ttk.Label(smtp_frame, text="Mot de passe:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.password = ttk.Entry(smtp_frame, width=30, show="*")
        self.password.grid(row=3, column=1, padx=5, pady=5)
        self.password.insert(0, self.config["password"])
        
        # Email expéditeur
        ttk.Label(smtp_frame, text="Email expéditeur:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.from_email = ttk.Entry(smtp_frame, width=30)
        self.from_email.grid(row=4, column=1, padx=5, pady=5)
        self.from_email.insert(0, self.config["from_email"])
        
        # Bouton de test
        ttk.Button(smtp_frame, text="Tester la connexion", command=self.test_smtp_connection).grid(row=5, column=0, columnspan=2, pady=10)
        
        # Frame pour les destinataires
        recipients_frame = ttk.LabelFrame(main_frame, text="Destinataires des notifications")
        recipients_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Liste des destinataires
        ttk.Label(recipients_frame, text="Emails (séparés par des virgules):").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.recipients = ttk.Entry(recipients_frame, width=50)
        self.recipients.grid(row=0, column=1, padx=5, pady=5)
        self.recipients.insert(0, ", ".join(self.config["recipients"]))
        
        # Frame pour les options de notification
        options_frame = ttk.LabelFrame(main_frame, text="Options de notification")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Activer les notifications
        self.enabled_var = tk.BooleanVar(value=self.config["enabled"])
        ttk.Checkbutton(options_frame, text="Activer les notifications par email", variable=self.enabled_var).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        # Intervalle de vérification
        ttk.Label(options_frame, text="Intervalle de vérification (secondes):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.check_interval = ttk.Entry(options_frame, width=10)
        self.check_interval.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        self.check_interval.insert(0, str(self.config["check_interval"]))
        
        # Niveaux d'urgence à notifier
        ttk.Label(options_frame, text="Niveaux d'urgence à notifier:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        
        levels_frame = ttk.Frame(options_frame)
        levels_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        self.level_vars = {}
        urgency_levels = ["Critique", "Élevé", "Moyen", "Faible"]
        
        for i, level in enumerate(urgency_levels):
            var = tk.BooleanVar(value=level in self.config["notification_levels"])
            self.level_vars[level] = var
            ttk.Checkbutton(levels_frame, text=level, variable=var).grid(row=0, column=i, padx=5)
        
        # Boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Enregistrer", command=self.save_settings).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Envoyer notification de test", command=self.send_test_notification).pack(side=tk.LEFT, padx=5)
        
        # Frame pour l'historique des notifications
        history_frame = ttk.LabelFrame(main_frame, text="Historique des notifications envoyées")
        history_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview pour l'historique
        columns = ("date", "recipient", "subject", "status")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings")
        
        self.history_tree.heading("date", text="Date")
        self.history_tree.heading("recipient", text="Destinataire")
        self.history_tree.heading("subject", text="Sujet")
        self.history_tree.heading("status", text="Statut")
        
        self.history_tree.column("date", width=150)
        self.history_tree.column("recipient", width=200)
        self.history_tree.column("subject", width=300)
        self.history_tree.column("status", width=100)
        
        self.history_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar pour le Treeview
        scrollbar = ttk.Scrollbar(self.history_tree, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Démarrer le thread de vérification des alertes si activé
        if self.config["enabled"]:
            self.start_alert_check_thread()
            
    def test_smtp_connection(self):
        # Récupérer les valeurs des champs
        server = self.smtp_server.get()
        port = int(self.smtp_port.get())
        username = self.username.get()
        password = self.password.get()
        
        if not server or not port or not username or not password:
            messagebox.showerror("Erreur", "Veuillez remplir tous les champs de configuration SMTP.")
            return
        
        try:
            # Tester la connexion SMTP
            server = smtplib.SMTP(server, port)
            server.ehlo()
            server.starttls()
            server.login(username, password)
            server.quit()
            
            messagebox.showinfo("Succès", "Connexion au serveur SMTP réussie!")
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de la connexion au serveur SMTP: {str(e)}")
            
    def save_settings(self):
        # Récupérer les valeurs des champs
        self.config["smtp_server"] = self.smtp_server.get()
        self.config["smtp_port"] = int(self.smtp_port.get())
        self.config["username"] = self.username.get()
        self.config["password"] = self.password.get()
        self.config["from_email"] = self.from_email.get()
        self.config["recipients"] = [email.strip() for email in self.recipients.get().split(",")]
        self.config["enabled"] = self.enabled_var.get()
        self.config["check_interval"] = int(self.check_interval.get())
        
        # Récupérer les niveaux d'urgence sélectionnés
        self.config["notification_levels"] = [level for level, var in self.level_vars.items() if var.get()]
        
        # Enregistrer la configuration
        self.save_config()
        
        # Démarrer ou arrêter le thread de vérification des alertes
        if self.config["enabled"]:
            self.start_alert_check_thread()
        
        messagebox.showinfo("Succès", "Configuration des notifications enregistrée avec succès!")
        
    def send_test_notification(self):
        # Envoyer un email de test
        if not self.config["recipients"]:
            messagebox.showerror("Erreur", "Aucun destinataire configuré.")
            return
            
        try:
            subject = "Test de notification - Gestion de Parc Automobile"
            body = f"""
            <html>
            <body>
                <h2>Test de notification</h2>
                <p>Ceci est un test du système de notification par email de l'application de Gestion de Parc Automobile.</p>
                <p>Si vous recevez cet email, la configuration est correcte.</p>
                <p>Date et heure: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """
            
            self.send_email(subject, body, self.config["recipients"])
            messagebox.showinfo("Succès", "Email de test envoyé avec succès!")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Échec de l'envoi de l'email de test: {str(e)}")
            
    def send_email(self, subject, body, recipients):
        # Envoyer un email
        server = self.config["smtp_server"]
        port = self.config["smtp_port"]
        username = self.config["username"]
        password = self.config["password"]
        from_email = self.config["from_email"]
        
        if not server or not port or not username or not password or not from_email:
            raise Exception("Configuration SMTP incomplète")
            
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = ", ".join(recipients)
        msg['Subject'] = subject
        
        # Ajouter le corps du message en HTML
        msg.attach(MIMEText(body, 'html'))
        
        # Envoyer l'email
        server = smtplib.SMTP(server, port)
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        server.quit()
        
        # Ajouter à l'historique
        self.add_to_history(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                           ", ".join(recipients), subject, "Envoyé")
                           
    def add_to_history(self, date, recipient, subject, status):
        # Ajouter une entrée à l'historique des notifications
        self.history_tree.insert("", "end", values=(date, recipient, subject, status))
        
    def start_alert_check_thread(self):
        # Démarrer un thread pour vérifier périodiquement les alertes
        self.stop_thread = False
        self.check_thread = threading.Thread(target=self.alert_check_loop)
        self.check_thread.daemon = True
        self.check_thread.start()
        
    def alert_check_loop(self):
        # Boucle de vérification des alertes
        while not self.stop_thread:
            if self.config["enabled"]:
                self.check_for_alerts()
            time.sleep(self.config["check_interval"])
            
    def check_for_alerts(self):
        # Vérifier les alertes non notifiées
        try:
            cursor = self.conn.cursor()
            
            # Récupérer les alertes non notifiées avec un niveau d'urgence correspondant
            cursor.execute("""
                SELECT ID_Alerte, ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence
                FROM Alertes
                WHERE Notifie = 0 AND Niveau_Urgence IN ({})
                ORDER BY Date_Creation DESC
            """.format(','.join(['?'] * len(self.config["notification_levels"]))), self.config["notification_levels"])
            
            alerts = cursor.fetchall()
            
            if alerts:
                # Préparer le contenu de l'email
                subject = f"Alertes Parc Automobile - {len(alerts)} nouvelle(s) alerte(s)"
                
                body = f"""
                <html>
                <body>
                    <h2>Nouvelles alertes du système de gestion de parc automobile</h2>
                    <p>{len(alerts)} nouvelle(s) alerte(s) ont été détectées et nécessitent votre attention.</p>
                    <table border="1" cellpadding="5" cellspacing="0">
                        <tr style="background-color: #f0f0f0;">
                            <th>Véhicule</th>
                            <th>Type d'alerte</th>
                            <th>Description</th>
                            <th>Date</th>
                            <th>Niveau d'urgence</th>
                        </tr>
                """
                
                for alert in alerts:
                    # Définir la couleur en fonction du niveau d'urgence
                    color = "#ffffff"  # blanc par défaut
                    if alert[5] == "Critique":
                        color = "#ffcccc"  # rouge clair
                    elif alert[5] == "Élevé":
                        color = "#ffffcc"  # jaune clair
                    
                    body += f"""
                        <tr style="background-color: {color};">
                            <td>{alert[1]}</td>
                            <td>{alert[2]}</td>
                            <td>{alert[3]}</td>
                            <td>{alert[4]}</td>
                            <td>{alert[5]}</td>
                        </tr>
                    """
                
                body += """
                    </table>
                    <p>Veuillez vous connecter à l'application pour plus de détails.</p>
                </body>
                </html>
                """
                
                # Envoyer l'email
                self.send_email(subject, body, self.config["recipients"])
                
                # Marquer les alertes comme notifiées
                for alert in alerts:
                    cursor.execute("UPDATE Alertes SET Notifie = 1 WHERE ID_Alerte = ?", (alert[0],))
                
                self.conn.commit()
                
        except Exception as e:
            print(f"Erreur lors de la vérification des alertes: {str(e)}")
            
    def stop_check_thread(self):
        # Arrêter le thread de vérification des alertes
        if hasattr(self, 'check_thread') and self.check_thread.is_alive():
            self.stop_thread = True
            self.check_thread.join(timeout=1.0)
            
    def __del__(self):
        # S'assurer que le thread est arrêté lors de la destruction de l'objet
        self.stop_check_thread()
        # Créer le dossier config s'il n'existe pas
        config_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if not os.path.exists(os.path.join(config_dir, "config")):
            os.makedirs(os.path.join(config_dir, "config"))
