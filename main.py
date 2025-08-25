import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from datetime import datetime, timedelta
import sys

# Ajout du chemin pour les modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import des modules personnalisés
from modules.database import create_database, initialize_database
from modules.vehicules import VehiculesFrame
from modules.kpi_distance import DistanceFrame
from modules.kpi_consommation import ConsommationFrame
from modules.kpi_disponibilite import DisponibiliteFrame
from modules.kpi_utilisation import UtilisationFrame
from modules.kpi_securite import SecuriteFrame
from modules.kpi_couts_fonctionnement import CoutsFonctionnementFrame
from modules.kpi_couts_financiers import CoutsFinanciersFrame
from modules.alertes import AlertesFrame
from modules.documents import DocumentsFrame
from modules.dashboard import DashboardFrame
from modules.rapports import RapportsFrame
from modules.notifications import NotificationsFrame
from modules.themes import ThemesFrame

class GestionParcApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestion de Parc Automobile")
        self.geometry("1200x700")
        self.configure(bg="#f0f0f0")
        
        # Création de la base de données si elle n'existe pas
        if not os.path.exists("parc_auto.db"):
            create_database()
            initialize_database()
        
        # Connexion à la base de données
        self.conn = sqlite3.connect("parc_auto.db")
        self.conn.row_factory = sqlite3.Row
        
        # Création du menu principal
        self.create_menu()
        
        # Création du notebook (onglets)
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Création des onglets
        self.vehicules_frame = VehiculesFrame(self.notebook, self.conn)
        self.distance_frame = DistanceFrame(self.notebook, self.conn)
        self.consommation_frame = ConsommationFrame(self.notebook, self.conn)
        self.disponibilite_frame = DisponibiliteFrame(self.notebook, self.conn)
        self.utilisation_frame = UtilisationFrame(self.notebook, self.conn)
        self.securite_frame = SecuriteFrame(self.notebook, self.conn)
        self.couts_fonctionnement_frame = CoutsFonctionnementFrame(self.notebook, self.conn)
        self.couts_financiers_frame = CoutsFinanciersFrame(self.notebook, self.conn)
        self.alertes_frame = AlertesFrame(self.notebook, self.conn)
        self.documents_frame = DocumentsFrame(self.notebook, self.conn)
        self.dashboard_frame = DashboardFrame(self.notebook, self.conn)
        self.rapports_frame = RapportsFrame(self.notebook, self.conn)
        self.notifications_frame = NotificationsFrame(self.notebook, self.conn)
        self.themes_frame = ThemesFrame(self.notebook, self)
        
        # Ajout des onglets au notebook
        self.notebook.add(self.vehicules_frame, text="Véhicules")
        self.notebook.add(self.dashboard_frame, text="Tableau de bord")
        self.notebook.add(self.distance_frame, text="KPI 1: Distance")
        self.notebook.add(self.consommation_frame, text="KPI 2: Consommation")
        self.notebook.add(self.disponibilite_frame, text="KPI 3: Disponibilité")
        self.notebook.add(self.utilisation_frame, text="KPI 4: Utilisation")
        self.notebook.add(self.securite_frame, text="KPI 5: Sécurité")
        self.notebook.add(self.couts_fonctionnement_frame, text="KPI 6: Coût Fonctionnement")
        self.notebook.add(self.couts_financiers_frame, text="KPI 7: Coût Financier")
        self.notebook.add(self.alertes_frame, text="Alertes")
        self.notebook.add(self.documents_frame, text="Documents")
        self.notebook.add(self.rapports_frame, text="Rapports")
        self.notebook.add(self.notifications_frame, text="Notifications")
        self.notebook.add(self.themes_frame, text="Thèmes")
        
        # Barre de statut
        self.status_bar = tk.Label(self, text="Prêt", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Vérification des alertes au démarrage
        self.after(1000, self.check_alerts)
    
    def create_menu(self):
        menubar = tk.Menu(self)
        
        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exporter les données", command=self.export_data)
        file_menu.add_command(label="Importer des données", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.quit)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        
        # Menu Rapports
        reports_menu = tk.Menu(menubar, tearoff=0)
        reports_menu.add_command(label="Générer un rapport", command=self.show_reports_tab)
        reports_menu.add_command(label="Planifier des rapports", command=self.show_reports_scheduling)
        menubar.add_cascade(label="Rapports", menu=reports_menu)
        
        # Menu Notifications
        notifications_menu = tk.Menu(menubar, tearoff=0)
        notifications_menu.add_command(label="Configurer les notifications", command=self.show_notifications_tab)
        notifications_menu.add_command(label="Envoyer une notification de test", command=self.send_test_notification)
        menubar.add_cascade(label="Notifications", menu=notifications_menu)
        
        # Menu Tableau de bord
        dashboard_menu = tk.Menu(menubar, tearoff=0)
        dashboard_menu.add_command(label="Afficher le tableau de bord", command=self.show_dashboard_tab)
        menubar.add_cascade(label="Tableau de bord", menu=dashboard_menu)
        
        # Menu Thèmes
        themes_menu = tk.Menu(menubar, tearoff=0)
        themes_menu.add_command(label="Personnaliser l'interface", command=self.show_themes_tab)
        menubar.add_cascade(label="Thèmes", menu=themes_menu)
        
        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="Documentation", command=self.show_documentation)
        help_menu.add_command(label="À propos", command=self.show_about)
        menubar.add_cascade(label="Aide", menu=help_menu)
        
        self.config(menu=menubar)
    
    def export_data(self):
        messagebox.showinfo("Export", "Fonctionnalité d'exportation à implémenter")
    
    def import_data(self):
        messagebox.showinfo("Import", "Fonctionnalité d'importation à implémenter")
    
    def show_reports_tab(self):
        # Afficher l'onglet des rapports
        self.notebook.select(self.rapports_frame)
    
    def show_reports_scheduling(self):
        # Afficher l'onglet des rapports et sélectionner l'onglet de planification
        self.notebook.select(self.rapports_frame)
        self.rapports_frame.show_scheduling_tab()
        
    def show_notifications_tab(self):
        # Afficher l'onglet des notifications
        self.notebook.select(self.notifications_frame)
        
    def send_test_notification(self):
        # Afficher l'onglet des notifications et envoyer une notification de test
        self.notebook.select(self.notifications_frame)
        self.notifications_frame.send_test_notification()
        
    def show_dashboard_tab(self):
        # Afficher l'onglet du tableau de bord
        self.notebook.select(self.dashboard_frame)
    
    def show_themes_tab(self):
        # Afficher l'onglet de personnalisation des thèmes
        self.notebook.select(self.themes_frame)
    
    def show_documentation(self):
        messagebox.showinfo("Documentation", "Documentation à implémenter")
    
    def show_about(self):
        messagebox.showinfo("À propos", "Gestion de Parc Automobile v1.0\n© 2025")
    
    def check_alerts(self):
        # Vérification des alertes toutes les heures
        # Vérifier les documents qui expirent bientôt
        self.documents_frame.check_expiring_documents()
        
        # Vérifier si les notifications sont activées et envoyer si nécessaire
        if hasattr(self, 'notifications_frame') and self.notifications_frame.config.get("enabled", False):
            self.notifications_frame.check_for_alerts()
            
        self.after(3600000, self.check_alerts)  # 3600000 ms = 1 heure
    
    def on_closing(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter?"):
            # Arrêter le thread de vérification des notifications s'il est actif
            if hasattr(self, 'notifications_frame'):
                self.notifications_frame.stop_check_thread()
                
            if self.conn:
                self.conn.close()
            self.destroy()

if __name__ == "__main__":
    app = GestionParcApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
