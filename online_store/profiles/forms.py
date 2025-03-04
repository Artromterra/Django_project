from django import forms
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm

from .models import User

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


class ProfileForm(forms.ModelForm):
    phone = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '+7 (___) ___-__-__',
        }),
        label='Телефон'
    )

    class Meta:
        model = User
        fields = ['avatar', 'email', 'phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        clean_phone = ''.join(filter(str.isdigit, phone))[-10:]  # Убираем всё, кроме цифр, берём последние 10
        if len(clean_phone) != 10:
            raise forms.ValidationError('Введите корректный номер (10 цифр)')
        return clean_phone
