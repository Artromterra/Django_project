"""The module responsible for user factories"""

import random

import factory.fuzzy

from .models import User


class UserFactory(factory.django.DjangoModelFactory):
    """User factory class."""

    class Meta:
        model = User
        django_get_or_create = (
            "email",
            "password",
        )

    username = factory.faker.Faker("name")
    phone = factory.LazyAttribute(
        lambda _: f"+7 ({random.randint(0, 999):03d}) "
                f"{random.randint(0, 999):03d} "
                f"{random.randint(0, 9999):04d}")
    email = factory.faker.Faker("email")
    password = factory.faker.Faker("word")
