"""The module responsible for review factories"""

import datetime

import factory.fuzzy

from shop.models.reviews import Review


class ReviewFactory(factory.django.DjangoModelFactory):
    """Review factory class."""

    class Meta:
        model = Review
        django_get_or_create = (
            "content",
            "created_at",
        )

    content = factory.faker.Faker("text")
    created_at = factory.LazyAttribute(lambda now: datetime.datetime.now())
