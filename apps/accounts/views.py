"""
TrendPulse AI - Authentication Views
"""
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.http import require_http_methods


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
        else:
            messages.error(request, 'Username atau password salah.')
    
    return render(request, 'accounts/login.html')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        full_name = request.POST.get('full_name', '').strip()
        
        # Validation
        if not username or not password1:
            messages.error(request, 'Username dan password wajib diisi.')
        elif password1 != password2:
            messages.error(request, 'Password tidak cocok.')
        elif len(password1) < 8:
            messages.error(request, 'Password minimal 8 karakter.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah dipakai.')
        elif email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar.')
        else:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
            )
            if full_name:
                parts = full_name.split(' ', 1)
                user.first_name = parts[0]
                user.last_name = parts[1] if len(parts) > 1 else ''
                user.save()
            
            login(request, user)
            messages.success(request, f'Selamat datang di TrendPulse, {user.first_name or username}!')
            return redirect('dashboard:index')
    
    return render(request, 'accounts/register.html')


def logout_view(request):
    logout(request)
    return redirect('accounts:login')
