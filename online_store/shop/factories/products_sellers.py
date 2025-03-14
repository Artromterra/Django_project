"""The module responsible for ProductSeller factories"""

import random

import factory.fuzzy

from shop.models.product import ProductSeller


class ProductSellerFactory(factory.django.DjangoModelFactory):
    """
    ProductSeller factory class.

    To create an instance,
    you must transfer the product and seller instances.
    For example
    ProductSellerFactory.create(product=product_instance, seller=seller_instance)
    """

    class Meta:
        model = ProductSeller
        django_get_or_create = ("product", "seller")

    price = factory.LazyAttribute(lambda _: round(random.uniform(0, 100), 2))
    amount = factory.LazyAttribute(lambda _: random.randint(0, 100))
