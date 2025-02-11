from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    """
    менеджер для создания профилей пользователей
    """
    def create_user(
            self,
            email,
            username,
            password,
            **extra_fields,
    ):
        """
        создаем новый профиль пользователя
        """
        if not email:
            raise ValueError('У пользователя должен быть почтовый адрес')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)

        return user


    def create_superuser(
            self,
            email,
            username,
            password,
            **extra_fields,
    ):
        """
          создаем новый профиль суперпользователя
        """
        user = self.create_user(
            email,
            username,
            password,
            **extra_fields,
        )
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)

        return user
