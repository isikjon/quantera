from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '********'
    }))

    class Meta:
        model = User
        fields = ['full_name', 'phone', 'email', 'password']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Иванов Иван Иванович'}),
            'phone': forms.TextInput(attrs={'placeholder': '+7 (___) ___ __-__'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@yandex.ru'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'example@yandex.ru'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '********'
    }))


class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'example@yandex.ru'
    }))


class PasswordResetConfirmForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'example@yandex.ru'
    }))
    code = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder': '_ _ _ - _ _ _'
    }))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': '********'
    }))


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'phone', 'email', 'date_of_birth']
        widgets = {
            'full_name': forms.TextInput(attrs={'placeholder': 'Имя'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Номер телефона'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Электронная почта'}),
            'date_of_birth': forms.DateInput(attrs={'placeholder': 'Дата рождения', 'type': 'date'}),
        }


class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Текущий пароль'
    }))
    new_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Новый пароль'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Повторите пароль'
    }))

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password and new_password != confirm_password:
            raise forms.ValidationError('Пароли не совпадают')
        return cleaned_data
