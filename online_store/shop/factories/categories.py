"""The module responsible for category factories."""

import factory.fuzzy

from shop.models.category import Category


class CategoryFactory(factory.django.DjangoModelFactory):
    """Category factory class."""

    class Meta:
        model = Category
        django_get_or_create = ("name",)

    name = factory.faker.Faker("word")
