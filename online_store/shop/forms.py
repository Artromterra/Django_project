from django import forms
from django.core.exceptions import ValidationError

from profiles.models import User


class OrderUserForm(forms.ModelForm):
    """
    форма данных пользователя при заказе
    """
    my_default_errors = {
        'required': 'Это поле необходимо заполнить',
        'invalid': 'Введите верное значение',
    }

    username = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
        }),
        error_messages=my_default_errors,
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
            'class': 'form-input',
        }),
        error_messages=my_default_errors,
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Тут можно изменить пароль'
        }),
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Введите пароль повторно',
            'onchange': 'submit();'
        }),
    )

    class Meta:
        model = User
        fields = ('username', 'phone', 'email', 'password', 'password_confirm')

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password1 = cleaned_data.get('password')
        password2 = cleaned_data.get('password_confirm')
        if password1 != password2:
            raise ValidationError('Пароли должны совпадать!')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                'Пользователь с указанным email существует, вы можете авторизоваться',
            )
