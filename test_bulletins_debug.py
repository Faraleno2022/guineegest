#!/usr/bin/env python
"""
Script de test pour identifier l'erreur 500 sur /bulletins-paie/
"""
import os
import sys
import django
from datetime import datetime

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

def test_bulletin_paie_list():
    """Test de la vue bulletin_paie_list pour identifier l'erreur"""
    from django.contrib.auth.models import User
    from fleet_app.models_entreprise import Employe, PresenceJournaliere, HeureSupplementaire, PaieEmploye, ParametrePaie
    from fleet_app.models_accounts import Entreprise, Profil
    from decimal import Decimal
    import calendar
    
    print("🔍 TEST BULLETINS - Démarrage du diagnostic")
    
    try:
        # 1. Vérifier l'utilisateur
        users = User.objects.all()
        if not users.exists():
            print("❌ Aucun utilisateur trouvé")
            return False
        
        user = users.first()
        print(f"✅ Utilisateur trouvé: {user.username}")
        
        # 2. Vérifier les employés
        employes = Employe.objects.filter(user=user)
        print(f"📊 Employés trouvés: {employes.count()}")
        
        if not employes.exists():
            print("⚠️ Aucun employé trouvé - création d'un employé test")
            employe_test = Employe.objects.create(
                user=user,
                matricule="TEST001",
                nom="Test",
                prenom="Employé",
                salaire_journalier=50000,
                statut="Actif"
            )
            print(f"✅ Employé test créé: {employe_test.matricule}")
        
        # 3. Test des paramètres de mois/année
        mois_actuel = datetime.now().month
        annee_actuelle = datetime.now().year
        print(f"📅 Période test: {mois_actuel}/{annee_actuelle}")
        
        # 4. Test de récupération entreprise
        try:
            profil = Profil.objects.get(user=user)
            if hasattr(profil, 'entreprise'):
                entreprise = profil.entreprise
                print(f"🏢 Entreprise trouvée: {entreprise.nom_entreprise if entreprise else 'None'}")
            else:
                print("⚠️ Profil sans entreprise")
                entreprise = None
        except Profil.DoesNotExist:
            print("⚠️ Profil utilisateur non trouvé")
            entreprise = None
        
        # 5. Test des calculs pour chaque employé
        employes = Employe.objects.filter(user=user).order_by('matricule')
        bulletins_data = []
        
        for employe in employes:
            print(f"\n🔄 Test employé: {employe.matricule}")
            
            # Test présences
            presences_mois = PresenceJournaliere.objects.filter(
                employe=employe,
                date__month=mois_actuel,
                date__year=annee_actuelle
            )
            print(f"   📊 Présences: {presences_mois.count()}")
            
            # Test heures supplémentaires
            heures_supp = HeureSupplementaire.objects.filter(
                employe=employe,
                date__month=mois_actuel,
                date__year=annee_actuelle
            )
            print(f"   ⏰ Heures supp: {heures_supp.count()}")
            
            # Test récupération/création paie
            try:
                paie, created = PaieEmploye.objects.get_or_create(
                    employe=employe,
                    mois=mois_actuel,
                    annee=annee_actuelle,
                    defaults={
                        'salaire_base': employe.salaire_journalier or 0,
                        'prime_discipline': 0,
                        'cherete_vie': 0,
                        'indemnite_transport': 0,
                    }
                )
                print(f"   💰 Paie {'créée' if created else 'trouvée'}: {paie.id}")
            except Exception as e:
                print(f"   ❌ Erreur paie: {e}")
                return False
            
            # Test paramètres CNSS
            try:
                param_cnss = ParametrePaie.objects.get(cle='CNSS_ACTIVER', user=user)
                print(f"   ⚙️ CNSS_ACTIVER: {param_cnss.valeur}")
            except ParametrePaie.DoesNotExist:
                print(f"   ⚠️ CNSS_ACTIVER non trouvé")
            
            # Test calculs basiques
            try:
                salaire_brut = Decimal(str(paie.salaire_base or 0))
                cnss_employe = salaire_brut * Decimal('0.05')
                avances = Decimal(str(employe.avances or 0))
                sanctions = Decimal('0')  # Champ supprimé
                net_a_payer = salaire_brut - cnss_employe - avances - sanctions
                
                print(f"   💵 Calculs: Brut={salaire_brut}, CNSS={cnss_employe}, Net={net_a_payer}")
                
                bulletins_data.append({
                    'employe': employe,
                    'paie': paie,
                    'salaire_brut': salaire_brut,
                    'net_a_payer': net_a_payer,
                })
                
            except Exception as e:
                print(f"   ❌ Erreur calculs: {e}")
                return False
        
        # 6. Test pagination
        try:
            from django.core.paginator import Paginator
            paginator = Paginator(bulletins_data, 12)
            page = paginator.get_page(1)
            print(f"📄 Pagination: {page.number}/{paginator.num_pages} pages")
        except Exception as e:
            print(f"❌ Erreur pagination: {e}")
            return False
        
        # 7. Test context
        try:
            context = {
                'bulletins_data': page,
                'employes_page': page,
                'paginator': paginator,
                'mois_actuel': mois_actuel,
                'annee_actuelle': annee_actuelle,
                'mois_nom': calendar.month_name[mois_actuel],
                'entreprise': entreprise,
            }
            print(f"📋 Context créé avec {len(context)} éléments")
        except Exception as e:
            print(f"❌ Erreur context: {e}")
            return False
        
        print("✅ TEST BULLETINS - Tous les tests passés")
        return True
        
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_bulletin_paie_list()
    if success:
        print("\n🎉 Diagnostic terminé - Aucune erreur détectée dans la logique")
    else:
        print("\n💥 Diagnostic terminé - Erreurs détectées")
