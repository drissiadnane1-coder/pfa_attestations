from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import CustomUser, ProfilDemandeur
import uuid
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

        username = f"user_{uuid.uuid4().hex[:8]}"
        code_interne = f"DEM-{uuid.uuid4().hex[:8].upper()}"

        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=CustomUser.RoleUtilisateur.DEMANDEUR,
            statut=CustomUser.StatutUtilisateur.ACTIF
        )

        ProfilDemandeur.objects.create(
            utilisateur=user,
            code_interne=code_interne,
            date_naissance=date_naissance or None,
            telephone=telephone,
            structure=structure
        )

        return redirect('login')

    return render(request, 'accounts/register.html')