import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from datetime import datetime, timedelta
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import matplotlib.pyplot as plt
import io

class RapportsFrame(ttk.Frame):
    def __init__(self, parent, conn):
        super().__init__(parent)
        self.conn = conn
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Titre
        title_label = ttk.Label(main_frame, text="Génération de Rapports", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Frame pour les options de rapport
        options_frame = ttk.LabelFrame(main_frame, text="Options du rapport")
        options_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Type de rapport
        ttk.Label(options_frame, text="Type de rapport:").grid(row=0, column=0, padx=5, pady=5)
        self.rapport_type = ttk.Combobox(options_frame, width=20, values=[
            "Rapport mensuel", 
            "Rapport trimestriel", 
            "Rapport annuel", 
            "Rapport de véhicule", 
            "Rapport d'incidents", 
            "Rapport de coûts"
        ])
        self.rapport_type.grid(row=0, column=1, padx=5, pady=5)
        self.rapport_type.current(0)
        
        # Véhicule (pour rapport de véhicule)
        ttk.Label(options_frame, text="Véhicule:").grid(row=1, column=0, padx=5, pady=5)
        self.vehicule_select = ttk.Combobox(options_frame, width=20)
        self.vehicule_select.grid(row=1, column=1, padx=5, pady=5)
        self.load_vehicules()
        
        # Période
        ttk.Label(options_frame, text="Période:").grid(row=2, column=0, padx=5, pady=5)
        periode_frame = ttk.Frame(options_frame)
        periode_frame.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        
        self.periode_type = ttk.Combobox(periode_frame, width=15, values=[
            "Mois courant", 
            "Mois précédent", 
            "Trimestre courant", 
            "Trimestre précédent", 
            "Année courante", 
            "Année précédente", 
            "Personnalisée"
        ])
        self.periode_type.pack(side=tk.LEFT, padx=(0, 5))
        self.periode_type.current(0)
        self.periode_type.bind("<<ComboboxSelected>>", self.toggle_custom_period)
        
        # Frame pour période personnalisée (initialement caché)
        self.custom_period_frame = ttk.Frame(options_frame)
        self.custom_period_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        self.custom_period_frame.grid_remove()
        
        ttk.Label(self.custom_period_frame, text="Du:").pack(side=tk.LEFT, padx=(0, 5))
        self.date_debut = ttk.Entry(self.custom_period_frame, width=10)
        self.date_debut.pack(side=tk.LEFT, padx=(0, 5))
        self.date_debut.insert(0, datetime.now().replace(day=1).strftime('%Y-%m-%d'))
        
        ttk.Label(self.custom_period_frame, text="Au:").pack(side=tk.LEFT, padx=(5, 5))
        self.date_fin = ttk.Entry(self.custom_period_frame, width=10)
        self.date_fin.pack(side=tk.LEFT, padx=(0, 5))
        self.date_fin.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # Options d'inclusion
        options_include_frame = ttk.LabelFrame(options_frame, text="Inclure dans le rapport")
        options_include_frame.grid(row=4, column=0, columnspan=2, padx=5, pady=5, sticky="w")
        
        self.include_graphs = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_include_frame, text="Graphiques", variable=self.include_graphs).grid(row=0, column=0, padx=5, pady=2, sticky="w")
        
        self.include_tables = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_include_frame, text="Tableaux de données", variable=self.include_tables).grid(row=0, column=1, padx=5, pady=2, sticky="w")
        
        self.include_alerts = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_include_frame, text="Alertes", variable=self.include_alerts).grid(row=0, column=2, padx=5, pady=2, sticky="w")
        
        self.include_summary = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_include_frame, text="Résumé exécutif", variable=self.include_summary).grid(row=1, column=0, padx=5, pady=2, sticky="w")
        
        self.include_recommendations = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_include_frame, text="Recommandations", variable=self.include_recommendations).grid(row=1, column=1, padx=5, pady=2, sticky="w")
        
        # Boutons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Aperçu", command=self.preview_report).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Générer PDF", command=self.generate_pdf).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Planifier", command=self.schedule_report).pack(side=tk.LEFT, padx=5)
        
        # Frame pour l'aperçu
        preview_frame = ttk.LabelFrame(main_frame, text="Aperçu du rapport")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Zone de texte pour l'aperçu
        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=20)
        self.preview_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def load_vehicules(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT ID_Vehicule FROM Vehicules ORDER BY ID_Vehicule")
        vehicules = [row[0] for row in cursor.fetchall()]
        vehicules.insert(0, "Tous les véhicules")
        self.vehicule_select['values'] = vehicules
        self.vehicule_select.current(0)
        
    def toggle_custom_period(self, event=None):
        if self.periode_type.get() == "Personnalisée":
            self.custom_period_frame.grid()
        else:
            self.custom_period_frame.grid_remove()
            
    def get_period_dates(self):
        periode = self.periode_type.get()
        today = datetime.now()
        
        if periode == "Mois courant":
            start_date = today.replace(day=1)
            end_date = today
        elif periode == "Mois précédent":
            if today.month == 1:
                start_date = today.replace(year=today.year-1, month=12, day=1)
                end_date = today.replace(year=today.year-1, month=12, day=31)
            else:
                start_date = today.replace(month=today.month-1, day=1)
                last_day = calendar.monthrange(today.year, today.month-1)[1]
                end_date = today.replace(month=today.month-1, day=last_day)
        elif periode == "Trimestre courant":
            current_quarter = (today.month - 1) // 3 + 1
            start_month = (current_quarter - 1) * 3 + 1
            start_date = today.replace(month=start_month, day=1)
            end_date = today
        elif periode == "Trimestre précédent":
            current_quarter = (today.month - 1) // 3 + 1
            prev_quarter = current_quarter - 1 if current_quarter > 1 else 4
            prev_quarter_year = today.year if current_quarter > 1 else today.year - 1
            start_month = (prev_quarter - 1) * 3 + 1
            end_month = start_month + 2
            start_date = datetime(prev_quarter_year, start_month, 1)
            last_day = calendar.monthrange(prev_quarter_year, end_month)[1]
            end_date = datetime(prev_quarter_year, end_month, last_day)
        elif periode == "Année courante":
            start_date = today.replace(month=1, day=1)
            end_date = today
        elif periode == "Année précédente":
            start_date = datetime(today.year - 1, 1, 1)
            end_date = datetime(today.year - 1, 12, 31)
        elif periode == "Personnalisée":
            try:
                start_date = datetime.strptime(self.date_debut.get(), '%Y-%m-%d')
                end_date = datetime.strptime(self.date_fin.get(), '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Erreur", "Format de date invalide. Utilisez YYYY-MM-DD.")
                return None, None
        
        return start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')
            
    def preview_report(self):
        start_date, end_date = self.get_period_dates()
        if not start_date or not end_date:
            return
            
        vehicule = self.vehicule_select.get()
        rapport_type = self.rapport_type.get()
        
        # Effacer l'aperçu précédent
        self.preview_text.delete(1.0, tk.END)
        
        # Générer l'aperçu du rapport
        self.preview_text.insert(tk.END, f"RAPPORT: {rapport_type}\n", "title")
        self.preview_text.insert(tk.END, f"Période: {start_date} à {end_date}\n", "subtitle")
        self.preview_text.insert(tk.END, f"Véhicule: {vehicule}\n\n", "subtitle")
        
        # Résumé exécutif
        if self.include_summary.get():
            self.preview_text.insert(tk.END, "RÉSUMÉ EXÉCUTIF\n", "heading")
            self.preview_text.insert(tk.END, "Ce rapport présente une analyse des performances de la flotte ")
            if vehicule != "Tous les véhicules":
                self.preview_text.insert(tk.END, f"pour le véhicule {vehicule} ")
            self.preview_text.insert(tk.END, f"pour la période du {start_date} au {end_date}.\n\n")
            
            # Ajouter des statistiques de base
            self.add_summary_stats()
        
        # Tableaux de données
        if self.include_tables.get():
            self.preview_text.insert(tk.END, "DONNÉES DÉTAILLÉES\n", "heading")
            self.preview_text.insert(tk.END, "[Les tableaux de données seront inclus dans le PDF final]\n\n")
        
        # Alertes
        if self.include_alerts.get():
            self.preview_text.insert(tk.END, "ALERTES\n", "heading")
            self.add_alerts_preview(vehicule, start_date, end_date)
        
        # Recommandations
        if self.include_recommendations.get():
            self.preview_text.insert(tk.END, "RECOMMANDATIONS\n", "heading")
            self.add_recommendations_preview(vehicule, start_date, end_date)
        
        # Configurer les styles de texte
        self.preview_text.tag_configure("title", font=("Arial", 16, "bold"))
        self.preview_text.tag_configure("subtitle", font=("Arial", 12))
        self.preview_text.tag_configure("heading", font=("Arial", 14, "bold"))
        
    def add_summary_stats(self):
        # Cette fonction ajouterait des statistiques résumées à l'aperçu
        # Dans une implémentation réelle, vous récupéreriez ces données de la base de données
        self.preview_text.insert(tk.END, "Statistiques clés:\n")
        self.preview_text.insert(tk.END, "- Disponibilité moyenne: 92%\n")
        self.preview_text.insert(tk.END, "- Utilisation moyenne: 78%\n")
        self.preview_text.insert(tk.END, "- Coût total de fonctionnement: 12,450€\n")
        self.preview_text.insert(tk.END, "- Incidents de sécurité: 3\n\n")
        
    def add_alerts_preview(self, vehicule, start_date, end_date):
        cursor = self.conn.cursor()
        
        if vehicule == "Tous les véhicules":
            cursor.execute("""
                SELECT ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut
                FROM Alertes
                WHERE Date_Creation BETWEEN ? AND ?
                ORDER BY Date_Creation DESC
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut
                FROM Alertes
                WHERE ID_Vehicule = ? AND Date_Creation BETWEEN ? AND ?
                ORDER BY Date_Creation DESC
            """, (vehicule, start_date, end_date))
            
        alerts = cursor.fetchall()
        
        if alerts:
            for alert in alerts:
                self.preview_text.insert(tk.END, f"- {alert[0]} | {alert[1]} | {alert[3]} | {alert[4]} | {alert[5]}\n")
                self.preview_text.insert(tk.END, f"  {alert[2]}\n\n")
        else:
            self.preview_text.insert(tk.END, "Aucune alerte pour la période sélectionnée.\n\n")
            
    def add_recommendations_preview(self, vehicule, start_date, end_date):
        # Dans une implémentation réelle, vous pourriez générer des recommandations basées sur les données
        self.preview_text.insert(tk.END, "Basé sur l'analyse des données, nous recommandons:\n")
        self.preview_text.insert(tk.END, "1. Optimiser la planification des maintenances préventives\n")
        self.preview_text.insert(tk.END, "2. Revoir la politique d'utilisation des véhicules sous-utilisés\n")
        self.preview_text.insert(tk.END, "3. Mettre en place une formation supplémentaire sur la sécurité\n\n")
        
    def generate_pdf(self):
        start_date, end_date = self.get_period_dates()
        if not start_date or not end_date:
            return
            
        vehicule = self.vehicule_select.get()
        rapport_type = self.rapport_type.get()
        
        # Demander à l'utilisateur où enregistrer le PDF
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            initialfile=f"{rapport_type.replace(' ', '_')}_{start_date}_to_{end_date}.pdf"
        )
        
        if not file_path:
            return
            
        try:
            # Créer le document PDF
            doc = SimpleDocTemplate(file_path, pagesize=A4)
            styles = getSampleStyleSheet()
            elements = []
            
            # Titre
            title_style = styles["Title"]
            elements.append(Paragraph(f"{rapport_type}", title_style))
            elements.append(Spacer(1, 0.25*inch))
            
            # Sous-titre
            subtitle_style = styles["Heading2"]
            elements.append(Paragraph(f"Période: {start_date} à {end_date}", subtitle_style))
            elements.append(Paragraph(f"Véhicule: {vehicule}", subtitle_style))
            elements.append(Spacer(1, 0.5*inch))
            
            # Résumé exécutif
            if self.include_summary.get():
                elements.append(Paragraph("RÉSUMÉ EXÉCUTIF", styles["Heading1"]))
                elements.append(Paragraph(
                    f"Ce rapport présente une analyse des performances de la flotte "
                    f"{'pour le véhicule ' + vehicule if vehicule != 'Tous les véhicules' else ''} "
                    f"pour la période du {start_date} au {end_date}.",
                    styles["Normal"]
                ))
                elements.append(Spacer(1, 0.25*inch))
                
                # Statistiques clés
                elements.append(Paragraph("Statistiques clés:", styles["Heading3"]))
                stats_data = [
                    ["Métrique", "Valeur"],
                    ["Disponibilité moyenne", "92%"],
                    ["Utilisation moyenne", "78%"],
                    ["Coût total de fonctionnement", "12,450€"],
                    ["Incidents de sécurité", "3"]
                ]
                stats_table = Table(stats_data, colWidths=[3*inch, 1.5*inch])
                stats_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                elements.append(stats_table)
                elements.append(Spacer(1, 0.5*inch))
            
            # Graphiques
            if self.include_graphs.get():
                elements.append(Paragraph("GRAPHIQUES", styles["Heading1"]))
                elements.append(Spacer(1, 0.25*inch))
                
                # Créer et ajouter des graphiques
                # Dans une implémentation réelle, vous créeriez des graphiques matplotlib et les convertiriez en images
                elements.append(Paragraph("Les graphiques seront générés ici", styles["Normal"]))
                elements.append(Spacer(1, 0.5*inch))
            
            # Tableaux de données
            if self.include_tables.get():
                elements.append(Paragraph("DONNÉES DÉTAILLÉES", styles["Heading1"]))
                elements.append(Spacer(1, 0.25*inch))
                
                # Ajouter des tableaux de données
                # Dans une implémentation réelle, vous récupéreriez ces données de la base de données
                elements.append(Paragraph("Les tableaux de données seront générés ici", styles["Normal"]))
                elements.append(Spacer(1, 0.5*inch))
            
            # Alertes
            if self.include_alerts.get():
                elements.append(Paragraph("ALERTES", styles["Heading1"]))
                elements.append(Spacer(1, 0.25*inch))
                
                cursor = self.conn.cursor()
                
                if vehicule == "Tous les véhicules":
                    cursor.execute("""
                        SELECT ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut
                        FROM Alertes
                        WHERE Date_Creation BETWEEN ? AND ?
                        ORDER BY Date_Creation DESC
                    """, (start_date, end_date))
                else:
                    cursor.execute("""
                        SELECT ID_Vehicule, Type_Alerte, Description, Date_Creation, Niveau_Urgence, Statut
                        FROM Alertes
                        WHERE ID_Vehicule = ? AND Date_Creation BETWEEN ? AND ?
                        ORDER BY Date_Creation DESC
                    """, (vehicule, start_date, end_date))
                    
                alerts = cursor.fetchall()
                
                if alerts:
                    alerts_data = [["Véhicule", "Type", "Date", "Urgence", "Statut", "Description"]]
                    for alert in alerts:
                        alerts_data.append([alert[0], alert[1], alert[3], alert[4], alert[5], alert[2]])
                    
                    alerts_table = Table(alerts_data, colWidths=[0.8*inch, 1*inch, 0.8*inch, 0.8*inch, 0.8*inch, 2*inch])
                    alerts_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(alerts_table)
                else:
                    elements.append(Paragraph("Aucune alerte pour la période sélectionnée.", styles["Normal"]))
                
                elements.append(Spacer(1, 0.5*inch))
            
            # Recommandations
            if self.include_recommendations.get():
                elements.append(Paragraph("RECOMMANDATIONS", styles["Heading1"]))
                elements.append(Spacer(1, 0.25*inch))
                
                elements.append(Paragraph("Basé sur l'analyse des données, nous recommandons:", styles["Normal"]))
                elements.append(Paragraph("1. Optimiser la planification des maintenances préventives", styles["Normal"]))
                elements.append(Paragraph("2. Revoir la politique d'utilisation des véhicules sous-utilisés", styles["Normal"]))
                elements.append(Paragraph("3. Mettre en place une formation supplémentaire sur la sécurité", styles["Normal"]))
            
            # Générer le PDF
            doc.build(elements)
            
            messagebox.showinfo("Succès", f"Le rapport a été généré avec succès et enregistré à:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erreur", f"Une erreur est survenue lors de la génération du PDF:\n{str(e)}")
    
    def schedule_report(self):
        # Ouvrir une fenêtre pour planifier des rapports automatiques
        schedule_window = tk.Toplevel(self)
        schedule_window.title("Planifier des rapports")
        schedule_window.geometry("400x300")
        
        ttk.Label(schedule_window, text="Planification de rapports automatiques", font=("Arial", 12, "bold")).pack(pady=10)
        
        # Options de planification
        options_frame = ttk.Frame(schedule_window)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(options_frame, text="Fréquence:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        frequency = ttk.Combobox(options_frame, width=15, values=["Quotidien", "Hebdomadaire", "Mensuel"])
        frequency.grid(row=0, column=1, padx=5, pady=5)
        frequency.current(2)
        
        ttk.Label(options_frame, text="Jour:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        day = ttk.Combobox(options_frame, width=15, values=["1", "15", "Dernier jour"])
        day.grid(row=1, column=1, padx=5, pady=5)
        day.current(0)
        
        ttk.Label(options_frame, text="Heure:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        hour = ttk.Combobox(options_frame, width=15, values=["00:00", "08:00", "12:00", "18:00"])
        hour.grid(row=2, column=1, padx=5, pady=5)
        hour.current(1)
        
        ttk.Label(options_frame, text="Format:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        format_var = ttk.Combobox(options_frame, width=15, values=["PDF", "Excel", "Les deux"])
        format_var.grid(row=3, column=1, padx=5, pady=5)
        format_var.current(0)
        
        ttk.Label(options_frame, text="Envoyer par email:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        email_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, variable=email_var).grid(row=4, column=1, padx=5, pady=5, sticky="w")
        
        ttk.Label(options_frame, text="Email(s):").grid(row=5, column=0, padx=5, pady=5, sticky="w")
        email_entry = ttk.Entry(options_frame, width=30)
        email_entry.grid(row=5, column=1, padx=5, pady=5)
        email_entry.insert(0, "admin@example.com")
        
        # Boutons
        buttons_frame = ttk.Frame(schedule_window)
        buttons_frame.pack(pady=10)
        
        ttk.Button(buttons_frame, text="Planifier", command=lambda: self.save_schedule(
            frequency.get(), day.get(), hour.get(), format_var.get(), email_var.get(), email_entry.get(), schedule_window
        )).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(buttons_frame, text="Annuler", command=schedule_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def save_schedule(self, frequency, day, hour, format_var, send_email, email, window):
        # Dans une implémentation réelle, vous enregistreriez ces paramètres dans la base de données
        # et configureriez un service pour exécuter les rapports selon le calendrier
        messagebox.showinfo("Planification", 
                           f"Rapport planifié avec succès:\n"
                           f"Fréquence: {frequency}\n"
                           f"Jour: {day}\n"
                           f"Heure: {hour}\n"
                           f"Format: {format_var}\n"
                           f"Envoi par email: {'Oui' if send_email else 'Non'}\n"
                           f"Email: {email if send_email else 'N/A'}")
        window.destroy()
        
    def show_scheduling_tab(self):
        """Méthode appelée depuis le menu principal pour afficher directement l'interface de planification des rapports"""
        self.schedule_report()