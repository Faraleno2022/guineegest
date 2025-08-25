import sqlite3
from datetime import datetime

def create_database():
    """Crée la base de données et les tables nécessaires"""
    conn = sqlite3.connect("parc_auto.db")
    cursor = conn.cursor()
    
    # Table des véhicules
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Vehicules (
        ID_Vehicule TEXT PRIMARY KEY,
        Immatriculation TEXT NOT NULL,
        Marque TEXT NOT NULL,
        Modele TEXT NOT NULL,
        Type_Moteur TEXT CHECK(Type_Moteur IN ('Essence', 'Diesel', 'Hybride', 'Électrique')),
        Categorie TEXT CHECK(Categorie IN ('Voiture', 'Moto', '4x4', 'Camion', 'Bus')),
        Date_Mise_Service TEXT,
        Date_Acquisition TEXT,
        Kilometrage_Initial INTEGER,
        Affectation TEXT,
        Statut_Actuel TEXT CHECK(Statut_Actuel IN ('Actif', 'Maintenance', 'Hors Service')),
        Numero_Chassis TEXT,
        Numero_Moteur TEXT,
        Observations TEXT
    )
    ''')
    
    # Table des documents administratifs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DocumentsAdministratifs (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Vehicule TEXT,
        Type_Document TEXT,
        Numero TEXT,
        Date_Emission TEXT,
        Date_Expiration TEXT,
        Fichier TEXT,
        Commentaires TEXT,
        FOREIGN KEY (ID_Vehicule) REFERENCES Vehicules(ID_Vehicule)
    )
    ''')
    
    # KPI 1 - Distance parcourue
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DistancesParcourues (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Vehicule TEXT,
        Date_Debut TEXT,
        Km_Debut INTEGER,
        Date_Fin TEXT,
        Km_Fin INTEGER,
        Distance_Parcourue INTEGER,
        Type_Moteur TEXT CHECK(Type_Moteur IN ('Diesel', 'Essence', 'Moto')),
        Limite_Annuelle INTEGER,
        FOREIGN KEY (ID_Vehicule) REFERENCES Vehicules(ID_Vehicule)
    )
    ''')
    
    # KPI 2 - Consommation de carburant
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS ConsommationCarburant (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Vehicule TEXT,
        Date_Plein1 TEXT,
        Km_Plein1 INTEGER,
        Date_Plein2 TEXT,
        Km_Plein2 INTEGER,
        Litres_Ajoutes REAL,
        Distance_Parcourue INTEGER,
        Consommation_100km REAL,
        Consommation_Constructeur REAL,
        Ecart_Constructeur REAL,
        FOREIGN KEY (ID_Vehicule) REFERENCES Vehicules(ID_Vehicule)
    )
    ''')
    
    # KPI 3 - Disponibilité
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS DisponibiliteVehicule (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Vehicule TEXT,
        Periode TEXT,
        Jours_Total_Periode INTEGER,
        Jours_Hors_Service INTEGER,
        Disponibilite_Pourcentage REAL,
        FOREIGN KEY (ID_Vehicule) REFERENCES Vehicules(ID_Vehicule)
    )
    ''')
    
    # KPI 4 - Utilisation des actifs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS UtilisationActifs (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Vehicule TEXT,
        Periode TEXT,
        Jours_Disponibles INTEGER,
        Jours_Utilises INTEGER,
        Utilisation_Pourcentage REAL,
        FOREIGN KEY (ID_Vehicule) REFERENCES Vehicules(ID_Vehicule)
    )
    ''')
    
    # KPI 5 - Sécurité
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS IncidentsSecurite (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Vehicule TEXT,
        Date_Incident TEXT,
        Type_Incident TEXT CHECK(Type_Incident IN ('Accident', 'Incident', 'Défaut critique')),
        Gravite TEXT,
        Commentaires TEXT,
        FOREIGN KEY (ID_Vehicule) REFERENCES Vehicules(ID_Vehicule)
    )
    ''')
    
    # KPI 6 - Coût de fonctionnement par kilomètre
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CoutsFonctionnement (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Vehicule TEXT,
        Date TEXT,
        Type_Cout TEXT,
        Montant REAL,
        Kilometrage INTEGER,
        Cout_Par_Km REAL,
        Description TEXT,
        FOREIGN KEY (ID_Vehicule) REFERENCES Vehicules(ID_Vehicule)
    )
    ''')
    
    # KPI 7 - Coût financier par kilomètre
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS CoutsFinanciers (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Vehicule TEXT,
        Date TEXT,
        Type_Cout TEXT,
        Montant REAL,
        Kilometrage INTEGER,
        Cout_Par_Km REAL,
        Periode_Amortissement INTEGER,
        Description TEXT,
        FOREIGN KEY (ID_Vehicule) REFERENCES Vehicules(ID_Vehicule)
    )
    ''')
    
    # Table des alertes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Alertes (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_Vehicule TEXT,
        Type_Alerte TEXT,
        Description TEXT,
        Date_Creation TEXT,
        Niveau_Urgence TEXT CHECK(Niveau_Urgence IN ('Faible', 'Moyen', 'Élevé', 'Critique')),
        Statut TEXT CHECK(Statut IN ('Active', 'Résolue', 'Ignorée')),
        FOREIGN KEY (ID_Vehicule) REFERENCES Vehicules(ID_Vehicule)
    )
    ''')
    
    conn.commit()
    conn.close()

def initialize_database():
    """Initialise la base de données avec des données d'exemple si nécessaire"""
    conn = sqlite3.connect("parc_auto.db")
    cursor = conn.cursor()
    
    # Vérifier si des véhicules existent déjà
    cursor.execute("SELECT COUNT(*) FROM Vehicules")
    count = cursor.fetchone()[0]
    
    if count == 0:
        # Ajouter quelques véhicules d'exemple
        vehicules = [
            ('VF001', 'AA-123-BB', 'Renault', 'Clio', 'Essence', 'Voiture', '2023-01-15', '2023-01-10', 0, 'Service Commercial', 'Actif', 'VF1RB08C12345678', 'K7M710-12345', ''),
            ('VF002', 'CC-456-DD', 'Peugeot', '308', 'Diesel', 'Voiture', '2022-06-20', '2022-06-15', 0, 'Service Technique', 'Actif', 'VF3LCRFJW12345678', 'DV6FC-12345', ''),
            ('VF003', 'EE-789-FF', 'Yamaha', 'MT-07', 'Essence', 'Moto', '2023-03-10', '2023-03-05', 0, 'Service Livraison', 'Actif', 'JYARM351000123456', 'CP2-12345', '')
        ]
        
        cursor.executemany('''
        INSERT INTO Vehicules (ID_Vehicule, Immatriculation, Marque, Modele, Type_Moteur, Categorie, 
                              Date_Mise_Service, Date_Acquisition, Kilometrage_Initial, Affectation, 
                              Statut_Actuel, Numero_Chassis, Numero_Moteur, Observations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', vehicules)
        
        # Ajouter des documents administratifs d'exemple
        today = datetime.now().strftime('%Y-%m-%d')
        next_year = datetime.now().replace(year=datetime.now().year + 1).strftime('%Y-%m-%d')
        
        documents = [
            ('VF001', 'Carte grise', 'CG12345', today, next_year, None, 'Document original'),
            ('VF001', 'Assurance', 'AS67890', today, next_year, None, 'Assurance tous risques'),
            ('VF002', 'Carte grise', 'CG23456', today, next_year, None, 'Document original'),
            ('VF002', 'Assurance', 'AS78901', today, next_year, None, 'Assurance tous risques'),
            ('VF003', 'Carte grise', 'CG34567', today, next_year, None, 'Document original'),
            ('VF003', 'Assurance', 'AS89012', today, next_year, None, 'Assurance tous risques')
        ]
        
        cursor.executemany('''
        INSERT INTO DocumentsAdministratifs (ID_Vehicule, Type_Document, Numero, Date_Emission, Date_Expiration, Fichier, Commentaires)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', documents)
        
        conn.commit()
    
    conn.close()
