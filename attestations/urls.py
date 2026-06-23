from django.urls import path
from . import views

urlpatterns = [
    path('demandeur/deposer-demande/', views.deposer_demande, name='deposer_demande'),
    path('demandeur/mes-demandes/', views.mes_demandes, name='mes_demandes'),

    path('agent/demandes-en-attente/', views.demandes_en_attente, name='demandes_en_attente'),
    path('agent/demande/<int:demande_id>/', views.detail_demande, name='detail_demande'),
    path('agent/demande/<int:demande_id>/valider/', views.valider_demande, name='valider_demande'),
    
    path('agent/demande/<int:demande_id>/rejeter/', views.rejeter_demande, name='rejeter_demande'),
    path('verification/<uuid:identifiant>/', views.verifier_attestation, name='verifier_attestation'),
    path('demandeur/attestation/<int:demande_id>/telecharger/', views.telecharger_attestation, name='telecharger_attestation'),
    path('admin/types/', views.liste_types_attestation, name='liste_types_attestation'),
    path('espace-admin/types/', views.liste_types_attestation, name='liste_types_attestation'),
    path('espace-admin/types/ajouter/', views.ajouter_type_attestation, name='ajouter_type_attestation'),
    path('espace-admin/types/<int:type_id>/modifier/', views.modifier_type_attestation, name='modifier_type_attestation'),
    path('espace-admin/types/<int:type_id>/changer-statut/', views.changer_statut_type_attestation, name='changer_statut_type_attestation'),

    path('espace-admin/tableau-bord/', views.tableau_bord_admin, name='tableau_bord_admin'),
    path('espace-admin/historique/', views.historique_actions, name='historique_actions'),
]