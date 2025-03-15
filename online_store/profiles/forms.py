import re

from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.utils.text import phone2numeric

from .models import User, Account

class RegisterForm(forms.ModelForm):
    """
    форма для кастомизации регистрации пользователя
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'user-input',
            'placeholder': 'Имя',
        }),
        label='',
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'user-input',
            'placeholder': 'E-mail',
        }),
        label='',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'user-input',
            'placeholder': '*********',
        }),
        label='',
    )
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class LoginForm(forms.Form):
    """
    форма для кастомизации логирования
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'user-input',
            'placeholder': 'E-mail',
        }),
        label='',
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'user-input',
            'placeholder': '*********',
        }),
        label='',
    )

    def clean(self):
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                return self.cleaned_data
            else:
                self.add_error("password", forms.ValidationError("Не верный пароль"))
        except User.DoesNotExist:
            self.add_error("email", forms.ValidationError("Пользователя не существует"))


class UserEmailRecoveryPasswordForm(PasswordResetForm):
    """
    форма запроса на восстановление пароля
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'user-input',
            'placeholder': 'E-mail',
            'autocomplete': 'off',
        }),
        label='',
    )

    def clean(self):
        email = self.cleaned_data.get('email')
        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                self.add_error("email", forms.ValidationError("Пользователь не активирован"))
        except User.DoesNotExist:
            self.add_error("email", forms.ValidationError("Нет такого пользователя"))


class UserSetNewPasswordForm(SetPasswordForm):
    """
    кастомизированная форма для ввода пароля
    """
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'user-input',
            'placeholder': 'Пароль',
            'autocomplete': 'off',
        }),
        label='',
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'user-input',
            'placeholder': 'Повторите пароль',
        }),
        label='',
    )


class ProfileUserUpdateForm(forms.ModelForm):
    avatar = forms.ImageField(required=False)
    phone = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    new_password = forms.CharField(widget=forms.PasswordInput(), required=False)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput(), required=False)


    class Meta:
        model = User
        fields = ['avatar',
                  'phone',
                  'email']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')

        # Убираем все нецифровые символы
        digits_only = re.sub(r'\D', '', phone)

        # Проверяем, что длина номера ровно 11 символов (с кодом страны)
        if len(digits_only) != 11 or not digits_only.startswith("7"):
            raise forms.ValidationError("Введите корректный номер телефона.")

        # Возвращаем только 10 цифр без 7-ки (для базы данных)
        return digits_only[1:]

class ProfileAccountUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length= 50)
    last_name = forms.CharField(max_length=50)
    patronymic = forms.CharField(max_length=50)

    class Meta:
        model = Account
        fields = ['first_name',
                  'last_name',
                  'patronymic',
                  ]
