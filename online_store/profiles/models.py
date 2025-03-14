from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.safestring import mark_safe

from .managers import UserManager


# Create your models here.
def user_avatar_directory_path(instance: 'User', filename: str) -> str:
    return 'profile/user_{pk}/avatar/{filename}'.format(
        pk=instance.pk,
        filename=filename,
    )


def image_file_validate_size(fieldfile):
    filesize = fieldfile.file.size
    if filesize > (2 * 1024 * 1024):
        raise ValidationError('Максимальный размер файла не может быть более 2Mb')


class User(AbstractBaseUser, PermissionsMixin):
    """
    Переопределенная модель пользователя
    """
    username = models.CharField(
        'user name',
        max_length=150,
        null=False,
        blank=False,
    )
    email = models.EmailField(
        'email',
        max_length=255,
        unique=True,
        null=False,
        blank=False,
    )
    phone = models.CharField(
        'phone number',
        max_length=15,
        unique=True,
        null=True,
        blank=True,
        validators=[
            RegexValidator(regex=r'^\d{10}$', message='Введите 10 цифр без кода страны')
        ]
    )
    is_active = models.BooleanField('is active', default=False)
    is_staff = models.BooleanField('is staff', default=False)
    is_superuser = models.BooleanField('is superuser', default=False)
    avatar = models.ImageField(
        'avatar',
        upload_to=user_avatar_directory_path,
        null=True,
        blank=True,
        validators=[image_file_validate_size],
    )

    objects = UserManager()

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    def __str__(self):
        return 'Пользователь: {}'.format(self.username)

    def image_preview(self):
        if self.avatar:
            return mark_safe(f'<img src="{self.avatar.url}" width="50" height="50" />')
        return 'No avatar'


from shop.models.order import Order
class Account(models.Model):

    # DB Fields
    # ФИО
    first_name = models.CharField(max_length= 50, null=True, blank=True)
    last_name = models.CharField(max_length=50, null=True, blank=True)
    patronymic = models.CharField(max_length=50, null=True, blank=True)

    # DB Relations
    # Связь аккаунта с пользовалелем
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # последний заказ из истории заказов
    last_order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="account_last_order", null=True, blank=True)
