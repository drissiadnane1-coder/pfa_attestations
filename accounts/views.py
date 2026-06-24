import uuid
import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, ProfilDemandeur


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user_obj = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return render(request, 'accounts/login.html', {
                'error': 'Email ou mot de passe incorrect.'
            })

        user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            return redirect('redirect_by_role')

        return render(request, 'accounts/login.html', {
            'error': 'Email ou mot de passe incorrect.'
        })

    return render(request, 'accounts/login.html')


@login_required
def redirect_by_role(request):
    user = request.user

    if user.role == 'ADMIN':
        return redirect('admin_dashboard')

    if user.role == 'AGENT_ADMINISTRATIF':
        return redirect('agent_dashboard')

    if user.role == 'DEMANDEUR':
        return redirect('demandeur_dashboard')

    return redirect('login')


@login_required
def admin_dashboard(request):
    return render(request, 'dashboards/admin_dashboard.html')


@login_required
def agent_dashboard(request):
    return render(request, 'dashboards/agent_dashboard.html')


@login_required
def demandeur_dashboard(request):
    return render(request, 'dashboards/demandeur_dashboard.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register_view(request):
    """Étape 1 : Vérification des erreurs, sauvegarde en session et envoi de l'email"""
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        date_naissance = request.POST.get('date_naissance')
        telephone = request.POST.get('telephone')
        structure = request.POST.get('structure')

        if password != password_confirm:
            return render(request, 'accounts/register.html', {
                'error': 'Les mots de passe ne correspondent pas.'
            })

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'accounts/register.html', {
                'error': 'Cet email existe déjà.'
            })

        # Générer un code à 6 chiffres
        code_verification = str(random.randint(100000, 999999))

        # Sauvegarder TOUTES les données en session
        request.session['pending_user_data'] = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': password,
            'date_naissance': date_naissance,
            'telephone': telephone,
            'structure': structure,
        }
        request.session['verification_code'] = code_verification

        # Envoyer l'email
        send_mail(
            subject='Code de vérification - Plateforme Attestations',
            message=f'Bonjour {first_name},\n\nVotre code de vérification est : {code_verification}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )

        return redirect('verify_code')

    return render(request, 'accounts/register.html')


def verify_code_view(request):
    """Étape 2 : Vérification du code et création officielle du compte"""
    if 'verification_code' not in request.session:
        messages.error(request, "Votre session a expiré. Veuillez vous réinscrire.")
        return redirect('register')

    if request.method == 'POST':
        user_code = request.POST.get('code')
        actual_code = request.session.get('verification_code')

        if user_code == actual_code:
            # Récupérer les données de la session
            data = request.session.get('pending_user_data')

            # Reprise de TA logique exacte de création d'utilisateur
            username = f"user_{uuid.uuid4().hex[:8]}"
            code_interne = f"DEM-{uuid.uuid4().hex[:8].upper()}"

            user = CustomUser.objects.create_user(
                username=username,
                email=data['email'],
                password=data['password'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                role=CustomUser.RoleUtilisateur.DEMANDEUR,
                statut=CustomUser.StatutUtilisateur.ACTIF
            )

            ProfilDemandeur.objects.create(
                utilisateur=user,
                code_interne=code_interne,
                date_naissance=data.get('date_naissance') or None,
                telephone=data.get('telephone'),
                structure=data.get('structure')
            )

            # Nettoyer la session
            del request.session['verification_code']
            del request.session['pending_user_data']

            messages.success(request, "Votre compte a été activé avec succès ! Vous pouvez vous connecter.")
            return redirect('login')
        else:
            # ICI : On utilise le système de messages global de Django
            messages.error(request, "Code invalide. Veuillez vérifier vos emails.")
            return render(request, 'Email_verification/verify.html')

    return render(request, 'Email_verification/verify.html')