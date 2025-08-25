import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta
import calendar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Tableau de Bord - KPIs", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame pour les filtres
        filter_frame = ttk.LabelFrame(main_frame, text="Filtres")
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Filtre par véhicule
        ttk.Label(filter_frame, text="Véhicule:").grid(row=0, column=0, padx=5, pady=5)
        self.vehicule_filter = ttk.Combobox(filter_frame, width=15)
        self.vehicule_filter.grid(row=0, column=1, padx=5, pady=5)
        self.load_vehicules()
        
        # Filtre par période
        ttk.Label(filter_frame, text="Période:").grid(row=0, column=2, padx=5, pady=5)
        self.periode_filter = ttk.Combobox(filter_frame, width=15, values=["Dernier mois", "3 derniers mois", "6 derniers mois", "Année en cours", "Année précédente"])
        self.periode_filter.grid(row=0, column=3, padx=5, pady=5)
        self.periode_filter.current(0)
        
        # Bouton pour appliquer les filtres
        ttk.Button(filter_frame, text="Appliquer", command=self.update_dashboard).grid(row=0, column=4, padx=5, pady=5)
        
        # Frame pour les graphiques
        self.graphs_frame = ttk.Frame(main_frame)
        self.graphs_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Créer les graphiques initiaux
        self.create_graphs()
        
    def load_vehicules(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Vehicule FROM Vehicules ORDER BY ID_Vehicule")
        vehicules = [row[0] for row in cursor.fetchall()]
        vehicules.insert(0, "Tous les véhicules")
        self.vehicule_filter['values'] = vehicules
        self.vehicule_filter.current(0)
        
    def update_dashboard(self):
        # Effacer les graphiques existants
        for widget in self.graphs_frame.winfo_children():
            widget.destroy()
        
        # Recréer les graphiques avec les filtres appliqués
        self.create_graphs()
        
    def create_graphs(self):
        # Récupérer les valeurs des filtres
        vehicule = self.vehicule_filter.get()
        periode = self.periode_filter.get()
        
        # Calculer les dates de début et de fin en fonction de la période sélectionnée
        end_date = datetime.now()
        if periode == "Dernier mois":
            start_date = end_date - timedelta(days=30)
        elif periode == "3 derniers mois":
            start_date = end_date - timedelta(days=90)
        elif periode == "6 derniers mois":
            start_date = end_date - timedelta(days=180)
        elif periode == "Année en cours":
            start_date = datetime(end_date.year, 1, 1)
        elif periode == "Année précédente":
            start_date = datetime(end_date.year - 1, 1, 1)
            end_date = datetime(end_date.year - 1, 12, 31)
        else:
            start_date = end_date - timedelta(days=30)
        
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        # Créer un cadre pour chaque ligne de graphiques
        row1_frame = ttk.Frame(self.graphs_frame)
        row1_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        row2_frame = ttk.Frame(self.graphs_frame)
        row2_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Graphique 1: Disponibilité des véhicules
        self.create_disponibilite_graph(row1_frame, vehicule, start_date_str, end_date_str)
        
        # Graphique 2: Utilisation des actifs
        self.create_utilisation_graph(row1_frame, vehicule, start_date_str, end_date_str)
        
        # Graphique 3: Coûts de fonctionnement
        self.create_couts_fonctionnement_graph(row2_frame, vehicule, start_date_str, end_date_str)
        
        # Graphique 4: Incidents de sécurité
        self.create_securite_graph(row2_frame, vehicule, start_date_str, end_date_str)
        
    def create_disponibilite_graph(self, parent, vehicule, start_date, end_date):
        # Créer un cadre pour le graphique
        frame = ttk.LabelFrame(parent, text="Disponibilité des véhicules (%)")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Récupérer les données
        cursor = self.conn.cursor()
        
        if vehicule == "Tous les véhicules":
            cursor.execute("""
                SELECT ID_Vehicule, Periode, Disponibilite_Pourcentage 
                FROM DisponibiliteVehicule 
                WHERE Periode BETWEEN ? AND ?
                ORDER BY Periode
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT ID_Vehicule, Periode, Disponibilite_Pourcentage 
                FROM DisponibiliteVehicule 
                WHERE ID_Vehicule = ? AND Periode BETWEEN ? AND ?
                ORDER BY Periode
            """, (vehicule, start_date, end_date))
        
        data = cursor.fetchall()
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(5, 4))
        
        if data:
            # Organiser les données par véhicule
            vehicules = {}
            for row in data:
                if row[0] not in vehicules:
                    vehicules[row[0]] = {'periodes': [], 'disponibilite': []}
                vehicules[row[0]]['periodes'].append(row[1])
                vehicules[row[0]]['disponibilite'].append(row[2])
            
            # Tracer les lignes pour chaque véhicule
            for veh, values in vehicules.items():
                ax.plot(values['periodes'], values['disponibilite'], marker='o', label=veh)
            
            ax.set_xlabel('Période')
            ax.set_ylabel('Disponibilité (%)')
            ax.set_ylim(0, 100)
            ax.grid(True)
            ax.legend()
            
            # Rotation des étiquettes de l'axe x pour une meilleure lisibilité
            plt.xticks(rotation=45)
            plt.tight_layout()
        else:
            ax.text(0.5, 0.5, "Aucune donnée disponible pour la période sélectionnée", 
                   horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        
        # Intégrer le graphique dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_utilisation_graph(self, parent, vehicule, start_date, end_date):
        # Créer un cadre pour le graphique
        frame = ttk.LabelFrame(parent, text="Utilisation des actifs (%)")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Récupérer les données
        cursor = self.conn.cursor()
        
        if vehicule == "Tous les véhicules":
            cursor.execute("""
                SELECT ID_Vehicule, Periode, Utilisation_Pourcentage 
                FROM UtilisationActifs 
                WHERE Periode BETWEEN ? AND ?
                ORDER BY Periode
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT ID_Vehicule, Periode, Utilisation_Pourcentage 
                FROM UtilisationActifs 
                WHERE ID_Vehicule = ? AND Periode BETWEEN ? AND ?
                ORDER BY Periode
            """, (vehicule, start_date, end_date))
        
        data = cursor.fetchall()
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(5, 4))
        
        if data:
            # Organiser les données par véhicule
            vehicules = {}
            for row in data:
                if row[0] not in vehicules:
                    vehicules[row[0]] = {'periodes': [], 'utilisation': []}
                vehicules[row[0]]['periodes'].append(row[1])
                vehicules[row[0]]['utilisation'].append(row[2])
            
            # Tracer les lignes pour chaque véhicule
            for veh, values in vehicules.items():
                ax.plot(values['periodes'], values['utilisation'], marker='o', label=veh)
            
            ax.set_xlabel('Période')
            ax.set_ylabel('Utilisation (%)')
            ax.set_ylim(0, 100)
            ax.grid(True)
            ax.legend()
            
            # Rotation des étiquettes de l'axe x pour une meilleure lisibilité
            plt.xticks(rotation=45)
            plt.tight_layout()
        else:
            ax.text(0.5, 0.5, "Aucune donnée disponible pour la période sélectionnée", 
                   horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        
        # Intégrer le graphique dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_couts_fonctionnement_graph(self, parent, vehicule, start_date, end_date):
        # Créer un cadre pour le graphique
        frame = ttk.LabelFrame(parent, text="Coûts de fonctionnement par type")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Récupérer les données
        cursor = self.conn.cursor()
        
        if vehicule == "Tous les véhicules":
            cursor.execute("""
                SELECT Type_Cout, SUM(Montant) as Total
                FROM CoutsFonctionnement 
                WHERE Date BETWEEN ? AND ?
                GROUP BY Type_Cout
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT Type_Cout, SUM(Montant) as Total
                FROM CoutsFonctionnement 
                WHERE ID_Vehicule = ? AND Date BETWEEN ? AND ?
                GROUP BY Type_Cout
            """, (vehicule, start_date, end_date))
        
        data = cursor.fetchall()
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(5, 4))
        
        if data:
            types = [row[0] for row in data]
            montants = [row[1] for row in data]
            
            # Créer un graphique à barres
            bars = ax.bar(types, montants, color='skyblue')
            
            # Ajouter les valeurs au-dessus des barres
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                        f'{height:.2f}€', ha='center', va='bottom')
            
            ax.set_xlabel('Type de coût')
            ax.set_ylabel('Montant total (€)')
            ax.set_title('Répartition des coûts de fonctionnement')
            
            # Rotation des étiquettes de l'axe x pour une meilleure lisibilité
            plt.xticks(rotation=45)
            plt.tight_layout()
        else:
            ax.text(0.5, 0.5, "Aucune donnée disponible pour la période sélectionnée", 
                   horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        
        # Intégrer le graphique dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_securite_graph(self, parent, vehicule, start_date, end_date):
        # Créer un cadre pour le graphique
        frame = ttk.LabelFrame(parent, text="Incidents de sécurité par type")
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Récupérer les données
        cursor = self.conn.cursor()
        
        if vehicule == "Tous les véhicules":
            cursor.execute("""
                SELECT Type_Incident, COUNT(*) as Total
                FROM IncidentsSecurite 
                WHERE Date_Incident BETWEEN ? AND ?
                GROUP BY Type_Incident
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT Type_Incident, COUNT(*) as Total
                FROM IncidentsSecurite 
                WHERE ID_Vehicule = ? AND Date_Incident BETWEEN ? AND ?
                GROUP BY Type_Incident
            """, (vehicule, start_date, end_date))
        
        data = cursor.fetchall()
        
        # Créer le graphique
        fig, ax = plt.subplots(figsize=(5, 4))
        
        if data:
            types = [row[0] for row in data]
            counts = [row[1] for row in data]
            
            # Créer un graphique circulaire
            ax.pie(counts, labels=types, autopct='%1.1f%%', startangle=90, shadow=True)
            ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
            ax.set_title('Répartition des incidents de sécurité')
            
            plt.tight_layout()
        else:
            ax.text(0.5, 0.5, "Aucune donnée disponible pour la période sélectionnée", 
                   horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        
        # Intégrer le graphique dans Tkinter
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
