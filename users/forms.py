from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
import re

User = get_user_model()

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Aquest correu electrònic ja està registrat.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("El nom d'usuari només pot contenir lletres, números i @/./+/-/_")
        return username

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Les contrasenyes no coincideixen.")
        if len(password1) < 8:
            raise ValidationError("La contrasenya ha de tenir almenys 8 caràcters.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'display_name', 'bio', 'avatar']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'avatar': forms.FileInput(),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label='Username or Email', max_length=254)

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Intenta trobar l'usuari per username o email
            try:
                user = User.objects.get(email=username)
                username = user.username
            except User.DoesNotExist:
                pass  # Si no és un email, assumim que és un username

            self.user_cache = self.authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise ValidationError("Credencials incorrectes.")
        return self.cleaned_data

    def authenticate(self, request, username=None, password=None):
        from django.contrib.auth import authenticate
        return authenticate(request, username=username, password=password)