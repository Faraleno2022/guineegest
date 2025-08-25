#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour créer un template propre et fonctionnel avec les colonnes de montants
"""

import os

def create_clean_template_with_montants():
    """
    Créer un template propre avec les colonnes de montants intégrées
    """
    template_path = r"c:\Users\faral\Desktop\Gestion_parck\fleet_app\templates\fleet_app\entreprise\presence_journaliere_list.html"
    
    # Créer une sauvegarde du template actuel
    backup_path = template_path + '.backup_corrupted'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Sauvegarde du template corrompu créée : {backup_path}")
    except Exception as e:
        print(f"⚠️  Erreur lors de la sauvegarde : {e}")
    
    # Template propre avec colonnes de montants
    clean_template = '''{% extends 'fleet_app/base.html' %}
{% load static %}
{% load fleet_filters %}

{% block title %}Présences Journalières{% endblock %}

{% block extra_css %}
<style>
    /* Styles généraux du tableau */
    .table {
        border-collapse: separate;
        border-spacing: 0;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        margin-bottom: 2rem;
        font-family: Arial, Helvetica, sans-serif;
        font-size: 14px;
    }
    
    /* Style pour élargir la colonne Employé */
    .table th.employe-col, .table td.employe-col {
        min-width: 180px;
        white-space: nowrap;
        font-weight: 700;
        font-size: 1.1rem;
        color: #0056b3;
    }
    
    /* Style pour la colonne Matricule */
    .table th.matricule-col, .table td.matricule-col {
        min-width: 100px;
        font-family: Consolas, monospace;
        font-size: 1.1rem;
        color: #0056b3;
        font-weight: 700;
        letter-spacing: 0.5px;
    }
    
    /* Style pour la colonne Poste */
    .table th.poste-col, .table td.poste-col {
        min-width: 150px;
        white-space: nowrap;
        font-weight: 600;
        font-size: 1.1rem;
        color: #0056b3;
    }
    
    /* Style pour les colonnes de statistiques */
    .table td.stat-col {
        font-weight: bold;
        text-align: center;
        background-color: #f0f7ff;
        border-left: 1px solid #c9d8e8;
        border-right: 1px solid #c9d8e8;
        font-size: 0.9rem;
        padding: 10px 8px;
    }
    
    /* Style pour les colonnes de montants */
    .table td.montant-col {
        font-weight: bold;
        text-align: center;
        font-size: 0.85rem;
        padding: 8px 6px;
        min-width: 80px;
    }
    
    .table-responsive {
        overflow-x: auto;
    }
</style>
{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="d-flex justify-content-between align-items-center mb-4">
        <h1 class="h3 mb-0 text-gray-800">
            <i class="fas fa-calendar-check me-2"></i>Présences Journalières
        </h1>
        <div class="d-flex gap-2">
            <a href="{% url 'presence_create' %}" class="btn btn-primary">
                <i class="fas fa-plus me-1"></i>Nouvelle Présence
            </a>
        </div>
    </div>

    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        {% endfor %}
    {% endif %}

    <div class="card shadow">
        <div class="card-header py-3">
            <h6 class="m-0 font-weight-bold text-primary">
                <i class="fas fa-table me-1"></i>Liste des Présences - {{ selected_month|date:"F Y" }}
            </h6>
        </div>
        <div class="card-body">
            <div class="table-responsive">
                <table class="table table-hover table-bordered" id="presenceTable">
                    <thead class="table-light">
                        <tr>
                            <!-- Colonnes principales -->
                            <th class="align-middle matricule-col text-center" rowspan="2">
                                <i class="fas fa-id-card me-1" style="color: #0056b3;"></i>
                                <span style="font-size: 0.9rem; color: #0056b3;">Matricule</span>
                            </th>
                            <th class="align-middle employe-col" rowspan="2">
                                <i class="fas fa-user me-1" style="color: #0056b3;"></i>
                                <span style="font-size: 0.9rem; color: #0056b3;">Employé</span>
                            </th>
                            <th class="align-middle poste-col" rowspan="2">
                                <i class="fas fa-briefcase me-1" style="color: #0056b3;"></i>
                                <span style="font-size: 0.9rem; color: #0056b3;">Fonction</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-info-circle me-1"></i>
                                <span style="font-size: 0.9rem;">Statut</span>
                            </th>
                            
                            <!-- Jours du mois -->
                            {% for header in days_headers %}
                            <th class="text-center">
                                <span class="d-block fw-bold" style="font-size: 0.85rem; color: #0056b3;">{{ header.day }}</span>
                                <span style="font-size: 0.75rem; color: #0056b3;">{{ header.date_str }}</span>
                            </th>
                            {% endfor %}
                            
                            <!-- Colonnes de statistiques -->
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-calendar me-1"></i>
                                <span style="font-size: 0.75rem;">Total Jours</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-check-circle me-1"></i>
                                <span style="font-size: 0.75rem;">Jours de présence</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-times-circle me-1"></i>
                                <span style="font-size: 0.75rem;">Absent</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-bed me-1"></i>
                                <span style="font-size: 0.75rem;">J Repos</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-thermometer-half me-1"></i>
                                <span style="font-size: 0.75rem;">Maladies</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-money-bill me-1"></i>
                                <span style="font-size: 0.75rem;">M.Payer</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-star me-1"></i>
                                <span style="font-size: 0.75rem;">Férié</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-graduation-cap me-1"></i>
                                <span style="font-size: 0.75rem;">Formation</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-umbrella-beach me-1"></i>
                                <span style="font-size: 0.75rem;">Congé</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-sun me-1"></i>
                                <span style="font-size: 0.75rem;">Sundays</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-clock me-1"></i>
                                <span style="font-size: 0.75rem;">H Supp</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-coins me-1"></i>
                                <span style="font-size: 0.75rem;">Mt Supp</span>
                            </th>
                            
                            <!-- Colonnes des montants par statut -->
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-euro-sign me-1" style="color: #28a745;"></i>
                                <span style="font-size: 0.75rem; color: #28a745;">Mt Présences</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-euro-sign me-1" style="color: #dc3545;"></i>
                                <span style="font-size: 0.75rem; color: #dc3545;">Mt Absent</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-euro-sign me-1" style="color: #6c757d;"></i>
                                <span style="font-size: 0.75rem; color: #6c757d;">Mt J Repos</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-euro-sign me-1" style="color: #ffc107;"></i>
                                <span style="font-size: 0.75rem; color: #ffc107;">Mt Maladies</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-euro-sign me-1" style="color: #fd7e14;"></i>
                                <span style="font-size: 0.75rem; color: #fd7e14;">Mt M.Payer</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-euro-sign me-1" style="color: #0d6efd;"></i>
                                <span style="font-size: 0.75rem; color: #0d6efd;">Mt Férié</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-euro-sign me-1" style="color: #17a2b8;"></i>
                                <span style="font-size: 0.75rem; color: #17a2b8;">Mt Formation</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-euro-sign me-1" style="color: #20c997;"></i>
                                <span style="font-size: 0.75rem; color: #20c997;">Mt Congé</span>
                            </th>
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-euro-sign me-1" style="color: #28a745;"></i>
                                <span style="font-size: 0.75rem; color: #28a745;">Mt Sundays</span>
                            </th>
                            
                            <!-- Colonne Action -->
                            <th class="align-middle text-center" rowspan="2">
                                <i class="fas fa-eye me-1" style="color: #007bff;"></i>
                                <span style="font-size: 0.75rem; color: #007bff;">Action</span>
                            </th>
                        </tr>
                        <tr>
                            <!-- Jours de la semaine -->
                            {% for header in days_headers %}
                            <th class="text-center small">
                                <span class="badge bg-light text-primary rounded-pill shadow-sm" 
                                      style="font-size: 0.75rem; padding: 0.25rem 0.5rem; border: 1px solid #0056b3;">
                                    {{ header.weekday|capfirst }}
                                </span>
                            </th>
                            {% endfor %}
                            <!-- Pas de contenu pour les colonnes de statistiques et montants dans cette ligne -->
                        </tr>
                    </thead>
                    <tbody>
                        {% for data in employes_data %}
                        <tr data-employee-id="{{ data.employe.id }}">
                            <!-- Colonnes principales -->
                            <td class="matricule-col text-center">{{ data.employe.matricule }}</td>
                            <td class="employe-col">{{ data.employe.nom }} {{ data.employe.prenom }}</td>
                            <td class="poste-col">{{ data.employe.poste|default:"N/A" }}</td>
                            <td class="text-center">
                                <span class="badge bg-success">Actif</span>
                            </td>
                            
                            <!-- Jours du mois avec présences -->
                            {% for day_data in data.presences_data %}
                            <td class="text-center">
                                {% if day_data.presence %}
                                    <span class="badge bg-{{ day_data.presence.statut|get_status_color }}">
                                        {{ day_data.presence.statut|get_status_display }}
                                    </span>
                                {% else %}
                                    <span class="text-muted">-</span>
                                {% endif %}
                            </td>
                            {% endfor %}
                            
                            <!-- Colonnes de statistiques -->
                            <td class="stat-col">{{ data.stats.total_jours|default:0 }}</td>
                            <td class="stat-col text-success">{{ data.stats.nombre_presences|default:0 }}</td>
                            <td class="stat-col text-danger">{{ data.stats.nombre_absences|default:0 }}</td>
                            <td class="stat-col text-secondary">{{ data.stats.nombre_repos|default:0 }}</td>
                            <td class="stat-col text-warning">{{ data.stats.nombre_maladies|default:0 }}</td>
                            <td class="stat-col text-info">{{ data.stats.nombre_maladie_payee|default:0 }}</td>
                            <td class="stat-col text-primary">{{ data.stats.nombre_feries|default:0 }}</td>
                            <td class="stat-col text-info">{{ data.stats.nombre_formations|default:0 }}</td>
                            <td class="stat-col text-info">{{ data.stats.nombre_conges|default:0 }}</td>
                            <td class="stat-col text-success">{{ data.stats.nombre_dimanches|default:0 }}</td>
                            <td class="stat-col">{{ data.stats.heures_supplementaires|default:0 }}</td>
                            <td class="stat-col">{{ data.stats.montant_heures_supp|default:0|floatformat:0 }} GNF</td>
                            
                            <!-- Colonnes des montants -->
                            <td class="montant-col text-success">
                                {{ data.montant_presences|default:0|floatformat:0 }} GNF
                            </td>
                            <td class="montant-col text-danger">
                                {{ data.montant_absent|default:0|floatformat:0 }} GNF
                            </td>
                            <td class="montant-col text-secondary">
                                {{ data.montant_repos|default:0|floatformat:0 }} GNF
                            </td>
                            <td class="montant-col text-warning">
                                {{ data.montant_maladies|default:0|floatformat:0 }} GNF
                            </td>
                            <td class="montant-col" style="color: #fd7e14;">
                                {{ data.montant_maladie_payee|default:0|floatformat:0 }} GNF
                            </td>
                            <td class="montant-col text-primary">
                                {{ data.montant_ferie|default:0|floatformat:0 }} GNF
                            </td>
                            <td class="montant-col text-info">
                                {{ data.montant_formation|default:0|floatformat:0 }} GNF
                            </td>
                            <td class="montant-col" style="color: #20c997;">
                                {{ data.montant_conge|default:0|floatformat:0 }} GNF
                            </td>
                            <td class="montant-col text-success">
                                {{ data.montant_dimanches|default:0|floatformat:0 }} GNF
                            </td>
                            
                            <!-- Colonne Action -->
                            <td class="text-center">
                                <button class="btn btn-sm btn-outline-primary" 
                                        onclick="showEmployeeDetails({{ data.employe.id }})">
                                    <i class="fas fa-eye"></i>
                                </button>
                            </td>
                        </tr>
                        {% empty %}
                        <tr>
                            <td colspan="100%" class="text-center text-muted py-4">
                                <i class="fas fa-info-circle me-2"></i>
                                Aucune donnée de présence disponible pour ce mois.
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script>
function showEmployeeDetails(employeeId) {
    // Fonction pour afficher les détails d'un employé
    alert('Détails de l\'employé ID: ' + employeeId);
}
</script>
{% endblock %}'''
    
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(clean_template)
        print(f"✅ Template propre créé avec les colonnes de montants : {template_path}")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du template : {e}")
        return False

def main():
    """
    Fonction principale
    """
    print("🔄 CRÉATION D'UN TEMPLATE PROPRE AVEC COLONNES DE MONTANTS")
    print("=" * 60)
    
    if create_clean_template_with_montants():
        print(f"\n✅ TEMPLATE CRÉÉ AVEC SUCCÈS !")
        print(f"📋 Colonnes de montants incluses :")
        print(f"   - Mt Présences")
        print(f"   - Mt Absent") 
        print(f"   - Mt J Repos")
        print(f"   - Mt Maladies")
        print(f"   - Mt M.Payer")
        print(f"   - Mt Férié")
        print(f"   - Mt Formation")
        print(f"   - Mt Congé")
        print(f"   - Mt Sundays")
        print(f"\n🚀 Redémarrez le serveur Django pour voir les changements :")
        print(f"   python manage.py runserver")
    else:
        print(f"\n❌ ÉCHEC DE LA CRÉATION DU TEMPLATE")
    
    return True

if __name__ == "__main__":
    main()
