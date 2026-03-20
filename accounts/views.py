import random
import string

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django_ratelimit.decorators import ratelimit

from .forms import (
    RegisterForm, LoginForm, PasswordResetRequestForm,
    PasswordResetConfirmForm, ProfileForm, ChangePasswordForm
)
from .models import PasswordResetToken, AuditLog

User = get_user_model()


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0]
    return request.META.get('REMOTE_ADDR')


def log_action(user, action, details='', request=None):
    AuditLog.objects.create(
        user=user,
        action=action,
        details=details,
        ip_address=get_client_ip(request) if request else None
    )


@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def register_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:settings')

    ref_code = request.GET.get('ref', '')
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if ref_code:
                referrer = User.objects.filter(referral_code=ref_code).first()
                if referrer:
                    user.referred_by = referrer
            user.save()
            log_action(user, 'register', request=request)
            login(request, user)
            return redirect('accounts:settings')

    return render(request, 'accounts/register.html', {'form': form, 'ref_code': ref_code})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:settings')

    next_url = request.GET.get('next', request.POST.get('next', ''))
    form = LoginForm()

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                log_action(user, 'login', request=request)
                if next_url and next_url.startswith('/'):
                    return redirect(next_url)
                return redirect('accounts:settings')
            else:
                messages.error(request, 'Неверный email или пароль')

    return render(request, 'accounts/login.html', {'form': form, 'next': next_url})


def logout_view(request):
    if request.user.is_authenticated:
        log_action(request.user, 'logout', request=request)
    logout(request)
    return redirect('accounts:login')


@ratelimit(key='ip', rate='3/m', method='POST', block=True)
def password_reset_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:settings')

    step = request.POST.get('step', 'request')

    if request.method == 'POST' and step == 'request':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.filter(email=email).first()
            if user:
                code = ''.join(random.choices(string.digits, k=6))
                PasswordResetToken.objects.create(user=user, code=code)
                send_mail(
                    'Восстановление пароля — Quantera',
                    f'Ваш код: {code}',
                    settings.EMAIL_HOST_USER or 'noreply@quantera.ru',
                    [email],
                    fail_silently=True,
                )
                log_action(user, 'password_reset_request', request=request)
            messages.info(request, 'Если аккаунт существует, код отправлен на email')
            return render(request, 'accounts/reset_password.html', {
                'step': 'confirm',
                'email': email,
            })

    if request.method == 'POST' and step == 'confirm':
        form = PasswordResetConfirmForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            code = form.cleaned_data['code'].replace(' ', '').replace('-', '')
            new_password = form.cleaned_data['new_password']
            user = User.objects.filter(email=email).first()
            if user:
                token = PasswordResetToken.objects.filter(
                    user=user, code=code, is_used=False
                ).order_by('-created_at').first()
                if token and token.is_valid():
                    user.set_password(new_password)
                    user.save()
                    token.is_used = True
                    token.save()
                    log_action(user, 'password_reset_complete', request=request)
                    messages.success(request, 'Пароль успешно изменён')
                    return redirect('accounts:login')
            messages.error(request, 'Неверный код или код истёк')
            return render(request, 'accounts/reset_password.html', {
                'step': 'confirm',
                'email': email,
            })

    return render(request, 'accounts/reset_password.html', {'step': 'request'})


@login_required
def settings_view(request):
    user = request.user
    profile_form = ProfileForm(instance=user)
    password_form = ChangePasswordForm()
    active_tab = 'profile'

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'profile':
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                log_action(user, 'profile_update', request=request)
                messages.success(request, 'Профиль обновлён')
                return redirect('accounts:settings')

        elif action == 'password':
            active_tab = 'security'
            password_form = ChangePasswordForm(request.POST)
            if password_form.is_valid():
                if user.check_password(password_form.cleaned_data['old_password']):
                    user.set_password(password_form.cleaned_data['new_password'])
                    user.save()
                    login(request, user)
                    log_action(user, 'password_change', request=request)
                    messages.success(request, 'Пароль изменён')
                    return redirect('accounts:settings')
                else:
                    messages.error(request, 'Неверный текущий пароль')

    return render(request, 'accounts/settings.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'active_tab': active_tab,
    })
