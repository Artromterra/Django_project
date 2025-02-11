from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User

class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        widgets = {
            'username': forms.TextInput(attrs={
                'id': 'name',
                'name': 'name',
                'class': 'user-input',
                'placeholder': 'Имя',
            }),
            'email': forms.TextInput(attrs={
                'name': 'login',
                'id': 'name',
                'class': 'user-input',
                'placeholder': 'E-mail',
            }),
            'password': forms.TextInput(attrs={
                'id': 'name',
                'name': 'pass',
                'placeholder': 'Пароль',
            })
        }