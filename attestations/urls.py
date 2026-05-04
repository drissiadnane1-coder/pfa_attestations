from django.urls import path
from . import views

urlpatterns = [
    path('demandeur/deposer-demande/', views.deposer_demande, name='deposer_demande'),
    path('demandeur/mes-demandes/', views.mes_demandes, name='mes_demandes'),

    path('agent/demandes-en-attente/', views.demandes_en_attente, name='demandes_en_attente'),
    path('agent/demande/<int:demande_id>/', views.detail_demande, name='detail_demande'),
    path('agent/demande/<int:demande_id>/valider/', views.valider_demande, name='valider_demande'),
    path('agent/demande/<int:demande_id>/rejeter/', views.rejeter_demande, name='rejeter_demande'),
]