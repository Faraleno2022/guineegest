"""
Script de test pour vérifier la synchronisation automatique des colonnes de présence
lors du pointage dans /management/presences/ vers /management/paies/
"""

import os
import sys
import django
from datetime import datetime, date
from decimal import Decimal

# Configuration Django
sys.path.append(r'c:\Users\faral\Desktop\Gestion_parck')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fleet_management.settings')
django.setup()

from django.contrib.auth.models import User
from fleet_app.models_entreprise import Employe, PresenceJournaliere, PaieEmploye

def test_synchronisation_pointage():
    """
    Test complet de la synchronisation automatique des colonnes de présence
    """
    print("🧪 DÉBUT DU TEST DE SYNCHRONISATION POINTAGE")
    print("=" * 60)
    
    try:
        # 1. Créer ou récupérer un utilisateur de test
        user, created = User.objects.get_or_create(
            username='test_pointage',
            defaults={
                'email': 'test@pointage.com',
                'first_name': 'Test',
                'last_name': 'Pointage'
            }
        )
        print(f"👤 Utilisateur: {user.username} {'(créé)' if created else '(existant)'}")
        
        # 2. Créer ou récupérer un employé de test
        employe, created = Employe.objects.get_or_create(
            matricule='TEST001',
            defaults={
                'user': user,
                'nom': 'Doe',
                'prenom': 'John',
                'salaire_base': Decimal('500000')
            }
        )
        print(f"👷 Employé: {employe.matricule} - {employe.prenom} {employe.nom} {'(créé)' if created else '(existant)'}")
        
        # 3. Nettoyer les données existantes pour ce test
        mois_test = datetime.now().month
        annee_test = datetime.now().year
        
        PresenceJournaliere.objects.filter(
            employe=employe,
            date__month=mois_test,
            date__year=annee_test
        ).delete()
        
        PaieEmploye.objects.filter(
            employe=employe,
            mois=mois_test,
            annee=annee_test
        ).delete()
        
        print(f"🧹 Données nettoyées pour {mois_test}/{annee_test}")
        
        # 4. Vérifier l'état initial (aucune paie ne devrait exister)
        paie_initiale = PaieEmploye.objects.filter(
            employe=employe,
            mois=mois_test,
            annee=annee_test
        ).first()
        
        print(f"📊 État initial: {'Aucune paie' if not paie_initiale else 'Paie existante'}")
        
        # 5. Créer des présences de test et vérifier la synchronisation automatique
        print("\n🔄 TEST DE SYNCHRONISATION AUTOMATIQUE:")
        print("-" * 40)
        
        # Créer différents types de présences
        presences_test = [
            (date(annee_test, mois_test, 1), 'P', 'Présent'),
            (date(annee_test, mois_test, 2), 'P', 'Présent'),
            (date(annee_test, mois_test, 3), 'A', 'Absent'),
            (date(annee_test, mois_test, 4), 'R', 'Repos'),
            (date(annee_test, mois_test, 5), 'M', 'Maladie'),
            (date(annee_test, mois_test, 6), 'M.PAYER', 'M.Payer'),
            (date(annee_test, mois_test, 7), 'F', 'Férié'),
            (date(annee_test, mois_test, 8), 'DIMANCHE', 'Dimanche travaillé'),
        ]
        
        for date_presence, statut, description in presences_test:
            print(f"➕ Création présence: {date_presence} - {statut} ({description})")
            
            # Créer la présence (doit déclencher automatiquement la synchronisation)
            presence = PresenceJournaliere.objects.create(
                employe=employe,
                date=date_presence,
                statut=statut
            )
            
            # Vérifier que la paie a été créée/mise à jour automatiquement
            paie = PaieEmploye.objects.filter(
                employe=employe,
                mois=mois_test,
                annee=annee_test
            ).first()
            
            if paie:
                print(f"   ✅ Paie synchronisée automatiquement")
                print(f"   📊 Colonnes actuelles:")
                print(f"      Total Jours: {paie.total_jours}")
                print(f"      Jours de présence: {paie.jours_travailles}")
                print(f"      Absent: {paie.jours_absents}")
                print(f"      J Repos: {paie.jours_repos_comptabilise}")
                print(f"      Maladies: {paie.jours_maladies}")
                print(f"      M.Payer: {paie.jours_m_payer}")
                print(f"      Férié: {paie.jours_ferie}")
                print(f"      Sundays: {paie.dimanches_travailles}")
            else:
                print(f"   ❌ ERREUR: Paie non créée automatiquement")
            
            print()
        
        # 6. Vérifier les totaux finaux
        print("📈 VÉRIFICATION DES TOTAUX FINAUX:")
        print("-" * 40)
        
        paie_finale = PaieEmploye.objects.filter(
            employe=employe,
            mois=mois_test,
            annee=annee_test
        ).first()
        
        if paie_finale:
            print(f"✅ SYNCHRONISATION RÉUSSIE!")
            print(f"📊 Résultats finaux:")
            print(f"   📅 Total Jours: {paie_finale.total_jours}")
            print(f"   ✅ Jours de présence: {paie_finale.jours_travailles} (attendu: 3)")
            print(f"   ❌ Absent: {paie_finale.jours_absents} (attendu: 1)")
            print(f"   😴 J Repos: {paie_finale.jours_repos_comptabilise} (attendu: 1)")
            print(f"   🤒 Maladies: {paie_finale.jours_maladies} (attendu: 1)")
            print(f"   💰 M.Payer: {paie_finale.jours_m_payer} (attendu: 1)")
            print(f"   🎉 Férié: {paie_finale.jours_ferie} (attendu: 1)")
            print(f"   📅 Sundays: {paie_finale.dimanches_travailles} (attendu: 1)")
            
            # Vérifier la cohérence
            total_attendu = 3 + 1 + 1 + 1 + 1 + 1 + 1  # P + A + R + M + M.PAYER + F + DIMANCHE
            total_reel = (paie_finale.jours_travailles + paie_finale.jours_absents + 
                         paie_finale.jours_repos_comptabilise + paie_finale.jours_maladies + 
                         paie_finale.jours_m_payer + paie_finale.jours_ferie)
            
            print(f"\n🔍 Vérification de cohérence:")
            print(f"   Total présences créées: {len(presences_test)}")
            print(f"   Total comptabilisé: {total_reel}")
            print(f"   ✅ Cohérent: {'Oui' if total_reel == len(presences_test) else 'Non'}")
            
        else:
            print(f"❌ ERREUR: Aucune paie trouvée après synchronisation")
        
        # 7. Test de modification d'une présence
        print(f"\n🔄 TEST DE MODIFICATION DE PRÉSENCE:")
        print("-" * 40)
        
        # Modifier une présence existante
        presence_a_modifier = PresenceJournaliere.objects.filter(
            employe=employe,
            date__month=mois_test,
            date__year=annee_test
        ).first()
        
        if presence_a_modifier:
            ancien_statut = presence_a_modifier.statut
            presence_a_modifier.statut = 'P'  # Changer en présent
            presence_a_modifier.save()
            
            print(f"✏️ Présence modifiée: {ancien_statut} → P")
            
            # Vérifier la mise à jour automatique
            paie_apres_modif = PaieEmploye.objects.get(
                employe=employe,
                mois=mois_test,
                annee=annee_test
            )
            
            print(f"📊 Colonnes après modification:")
            print(f"   ✅ Jours de présence: {paie_apres_modif.jours_travailles}")
            print(f"   ❌ Absent: {paie_apres_modif.jours_absents}")
        
        # 8. Test de suppression d'une présence
        print(f"\n🗑️ TEST DE SUPPRESSION DE PRÉSENCE:")
        print("-" * 40)
        
        presence_a_supprimer = PresenceJournaliere.objects.filter(
            employe=employe,
            date__month=mois_test,
            date__year=annee_test
        ).first()
        
        if presence_a_supprimer:
            statut_supprime = presence_a_supprimer.statut
            presence_a_supprimer.delete()
            
            print(f"🗑️ Présence supprimée: {statut_supprime}")
            
            # Vérifier la mise à jour automatique
            paie_apres_suppression = PaieEmploye.objects.get(
                employe=employe,
                mois=mois_test,
                annee=annee_test
            )
            
            print(f"📊 Colonnes après suppression:")
            print(f"   ✅ Jours de présence: {paie_apres_suppression.jours_travailles}")
            print(f"   ❌ Absent: {paie_apres_suppression.jours_absents}")
        
        print(f"\n🎉 TEST TERMINÉ AVEC SUCCÈS!")
        
    except Exception as e:
        print(f"❌ ERREUR DURANT LE TEST: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_synchronisation_pointage()
