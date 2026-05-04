from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('redirect_by_role')

        return render(request, 'accounts/login.html', {
            'error': 'Nom d’utilisateur ou mot de passe incorrect.'
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
