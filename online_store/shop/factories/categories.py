"""The module responsible for category factories."""

import random

import factory.fuzzy

from shop.models.category import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    """Category factory class."""

    class Meta:
        model = Category

    name = factory.faker.Faker("word")
    description = factory.faker.Faker("text")
    is_active = factory.LazyAttribute(lambda x: random.choice((True, False)))
