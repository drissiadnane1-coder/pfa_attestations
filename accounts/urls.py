from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('redirect/', views.redirect_by_role, name='redirect_by_role'),

    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/agent/', views.agent_dashboard, name='agent_dashboard'),
    path('dashboard/demandeur/', views.demandeur_dashboard, name='demandeur_dashboard'),

    path('register/', views.register_view, name='register'),
    path('verify/', views.verify_code_view, name='verify_code'),


# 1. Page pour taper son email
    path('mot-de-passe-oublie/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),

    # 2. Page de confirmation d'envoi de l'email
    path('mot-de-passe-oublie/envoye/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_sent.html'
    ), name='password_reset_done'),

    # 3. Le lien unique envoyé par email (Django génère le uidb64 et le token)
    path('reinitialisation/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_form.html'
    ), name='password_reset_confirm'),

    # 4. Page de succès
    path('reinitialisation/succes/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_done_final.html'
    ), name='password_reset_complete'),
]