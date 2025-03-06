"""The module responsible for review factories"""

import datetime

import factory.fuzzy

from shop.models.reviews import Review


class ReviewFactory(factory.django.DjangoModelFactory):
    """
    Review factory class.

    To create an instance,
    you must transfer the product and author instances.
    For example
    ProductFactory.create(product=product_instance, author=user_instance)
    """

    class Meta:
        model = Review

    content = factory.faker.Faker("text")
    created_at = factory.LazyAttribute(lambda now: datetime.datetime.now())
