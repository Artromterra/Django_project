"""The module responsible for seller factories"""

import random

import factory.fuzzy
from faker import Faker

from shop.models.seller import Seller


class SellerFactory(factory.django.DjangoModelFactory):
    """
    Seller factory class.

    To create an instance,
    you must transfer the user's instance.
    For example SellerFactory.create(user=user_instance)
    """

    class Meta:
        model = Seller
        django_get_or_create = (
            "email",
        )

    name = factory.faker.Faker("name")
    phone = factory.LazyAttribute(
        lambda _: f"+7 ({random.randint(0, 999):03d}) "
                f"{random.randint(0, 999):03d} "
                f"{random.randint(0, 9999):04d}")
    address = factory.LazyAttribute(lambda _: Faker().address())
    email = factory.faker.Faker("email")
