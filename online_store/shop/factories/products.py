"""The module responsible for product factories"""

import random

import factory.fuzzy

from shop.models.product import Product


class ProductFactory(factory.django.DjangoModelFactory):
    """
    Product factory class.

    To create an instance,
    you must transfer the category instance.
    For example
    ProductFactory.create(category=category_instance)
    """

    class Meta:
        model = Product

    title = factory.faker.Faker("word")
    description = factory.faker.Faker("text")
    short_description = factory.faker.Faker("word")
    price = factory.LazyAttribute(lambda x: round(random.uniform(0, 100), 2))
    is_active = factory.LazyAttribute(lambda x: random.choice((True, False)))
