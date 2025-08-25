import calendar
from datetime import date

print("=== TEST DU CALCUL DU NOMBRE DE JOURS PAR MOIS ===\n")

# Test pour l'année actuelle (2025)
current_year = 2025
print(f"Année testée: {current_year}")
print("-" * 50)

# Tester chaque mois
for month in range(1, 13):
    # Utiliser la même méthode que dans la vue Django
    nombre_jours_mois = calendar.monthrange(current_year, month)[1]
    month_name = calendar.month_name[month]
    
    print(f"{month:2d}. {month_name:12} : {nombre_jours_mois:2d} jours")

print("\n" + "=" * 50)

# Test spécial pour les années bissextiles
print("\nTEST ANNÉES BISSEXTILES (Février):")
print("-" * 35)

test_years = [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027, 2028]

for year in test_years:
    feb_days = calendar.monthrange(year, 2)[1]
    is_leap = calendar.isleap(year)
    status = "bissextile" if is_leap else "normale"
    print(f"Février {year} : {feb_days:2d} jours (année {status})")

print("\n" + "=" * 50)

# Test du mois actuel
today = date.today()
current_month_days = calendar.monthrange(today.year, today.month)[1]
current_month_name = calendar.month_name[today.month]

print(f"\nMOIS ACTUEL:")
print(f"{current_month_name} {today.year} : {current_month_days} jours")
print(f"Date d'aujourd'hui : {today.strftime('%d/%m/%Y')}")

print("\n" + "=" * 50)
print("✅ Test terminé avec succès!")
