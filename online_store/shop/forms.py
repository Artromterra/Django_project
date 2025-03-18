import re

from django import forms
from django.core.exceptions import ValidationError

from profiles.models import User
from shop.models.order import Order


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

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            digits = re.sub(r'\D', '', phone)
            return digits[1:]

    def clean(self):
        cleaned_data = super().clean()
        email = self.cleaned_data.get('email')
        password1 = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password_confirm')
        phone = self.cleaned_data.get('phone')

        if phone:
            if len(phone) != 10:
                raise ValidationError('Введите корректный номер телефона')
        else:
            raise ValidationError('Поле с номером телефона не должно быть пустым')

        if password1 != password2:
            raise ValidationError('Пароли должны совпадать!')
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                'Пользователь с указанным email существует, вы можете авторизоваться',
            )
        return cleaned_data

class OrderDeliveryForm(forms.ModelForm):
    """
    форма для страницы способ доставки
    """
    class Meta:
        model = Order
        fields = ('delivery', 'city', 'address')

    CHOICES = {
        'RD': 'Обычная доставка',
        'ED': 'Экспресс доставка',
    }
    delivery = forms.ChoiceField(
        widget=forms.RadioSelect(),
        choices=CHOICES,
    )
    city = forms.CharField(max_length=100)
    address = forms.CharField(
        widget=forms.TextInput(attrs={
            'onchange': 'submit();',
        }),
    )

class OrderPayForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('payment_method',)

    CHOICES = {
        'SC': 'Онлайн картой',
        'RD': 'Онлайн со случайного чужого счета'
    }
    payment_method = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={
            'onchange': 'submit();',
        }),
        choices=CHOICES,
    )