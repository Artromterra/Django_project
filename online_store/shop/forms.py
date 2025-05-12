import re
from typing import List, Callable, Any

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from profiles.models import User
from shop.models.order import Order
from django import forms

from django.utils.translation import gettext_lazy as _


class NewImportFileForm(forms.Form):
    """Form for uploading a new import file."""

    new_import_file = forms.FileField(
        required=False,
        help_text=_("Загрузить новый файл импорта"),
        label=_("Новый файл импорта"),
    )


class ImportFilesForm(forms.Form):
    """Form for selecting files to import."""

    email = forms.EmailField(
        required=False,
        label="Email админа",
        help_text=_("Email, куда будет отправлен отчет об импорте. "
                  "Если не указать, будут использоваться email-ы админов, "
                  "установленных по умолчанию.")
    )
    files = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        choices=[],
        label=_("Выберете файлы импорта"),
        required=True,
    )

class OrderUserForm(forms.ModelForm):
    """
    форма данных пользователя при заказе
    """
    my_default_errors = {
        'required': _('Это поле необходимо заполнить'),
        'invalid': _('Введите верное значение'),
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
            'placeholder': _('Тут можно изменить пароль')
        }),
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': _('Введите пароль повторно'),
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
                raise ValidationError(_('Введите корректный номер телефона'))
        else:
            raise ValidationError(_('Поле с номером телефона не должно быть пустым'))

        if password1 != password2:
            raise ValidationError(_('Пароли должны совпадать!'))
        if User.objects.filter(email=email).exists():
            raise ValidationError(
                _('Пользователь с указанным email существует, вы можете авторизоваться'),
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
        'RD': _('Обычная доставка'),
        'ED': _('Экспресс доставка'),
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
        'SC': _('Онлайн картой'),
        'RC': _('Онлайн со случайного чужого счета')
    }
    payment_method = forms.ChoiceField(
        widget=forms.RadioSelect(attrs={
                'onchange': 'submit();',
            }),
        choices=CHOICES,
    )

class OrderYookassaPayForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('cart_number', 'expiry_month', 'expiry_year', 'cvc', 'total_price')

    cart_number = forms.CharField(max_length=16, label=_('Номер карты'))
    expiry_month = forms.CharField(max_length=2, label=_('Месяц окончания (MM)'))
    expiry_year = forms.CharField(max_length=4, label=_('Год окончания (YYYY)'))
    cvc = forms.CharField(max_length=4, label='CVC', widget=forms.PasswordInput())
    total_price = forms.DecimalField(disabled=True, label=_('Сумма'))



class ListEmailsField(forms.CharField):
    """A field for entering a list of emails."""

    def __init__(self, *args, separator: str = "\n", **kwargs):
        """
        :param separator: The separator used to separate the emails in the string.
        """
        super().__init__(*args, **kwargs)
        self.__separator = separator

    def clean(self, value) -> List[str]:
        value = super().clean(value)
        if not value:
            return []

        emails: List[str] = list()
        for part in re.split(r'[ ,;\n\r\t]+', value):
            cleaned_part = (part.replace("[", "")
                            .replace("]", "")
                            .replace("'", ""))
            email = cleaned_part.strip()
            if email:
                validate_email(email)
                emails.append(email)

        return emails
