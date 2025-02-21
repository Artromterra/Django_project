"""The module responsible for product factories"""

import random

import factory.fuzzy

from shop.models.product import Product

from .categories import CategoryFactory


class ProductFactory(factory.django.DjangoModelFactory):
    """Product factory class."""

    class Meta:
        model = Product
        django_get_or_create = (
            "title",
            "description",
            "short_description",
            "price",
            "is_active",
            "category"
        )

    title = factory.faker.Faker("word")
    description = factory.faker.Faker("text")
    short_description = factory.faker.Faker("word")
    price = factory.LazyAttribute(lambda x: round(random.uniform(0, 100), 2))
    is_active = factory.LazyAttribute(lambda x: random.choice((True, False)))
    category = factory.SubFactory(CategoryFactory)
