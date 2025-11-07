from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserUpdateForm, CustomAuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registre completat amb èxit!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Hi ha hagut un error en el registre.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Has iniciat sessió correctament!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Credencials incorrectes.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Has tancat sessió.')
    return redirect('home')

@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'user': request.user})

@login_required
def edit_profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualitzat amb èxit!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Error en actualitzar el perfil.')
    else:
        form = CustomUserUpdateForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})

def public_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    return render(request, 'users/public_profile.html', {'profile_user': user})