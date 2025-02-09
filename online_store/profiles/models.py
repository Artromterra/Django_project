from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# Create your models here.
def user_avatar_directory_path(instance: 'UserProfile', filename: str) -> str:
    return 'profile/user_{pk}/avatar/{filename}'.format(
        pk=instance.pk,
        filename=filename,
    )


class UserProfile(AbstractBaseUser, PermissionsMixin):
    """
    Переопределенная модель пользователя
    """
    username = models.CharField(max_length=20, null=True, blank=True)
    first_name = models.CharField(max_length=20, verbose_name='имя пользователя')
    last_name = models.CharField(max_length=50, verbose_name='фамилия пользователя')
    email = models.EmailField(max_length=255, unique=True, verbose_name='электронная почта')
    phone_number = models.CharField(max_length=15, unique=True, verbose_name='телефонный номер')
    image = models.ImageField(
        upload_to=user_avatar_directory_path,
        null=True,
        blank=True,
        verbose_name='картинка пользователя'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number', 'first_name', 'last_name', 'password']

    def __str__(self):
        return ('Имя пользователя {}, почта {}'.
                format(self.first_name, self.email))


class UserProfileManager(BaseUserManager):
    """
    менеджер для создания профилей пользователей
    """
    def create_user(
            self,
            email,
            first_name,
            last_name,
            phone_number,
            password,
            image,
    ):
        """
        создаем новый профиль пользователя
        """
        if not email:
            raise ValueError('У пользователя должен быть почтовый адрес')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            image=image,
        )
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)

        return user

    def create_superuser(
            self,
            email,
            first_name,
            last_name,
            phone_number,
            password,
            image,
    ):
        """
          создаем новый профиль суперпользователя
        """
        user = self.create_user(
            email,
            first_name,
            last_name,
            phone_number,
            password,
            image,
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)

        return user
