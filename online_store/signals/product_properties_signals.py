from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from shop.models.product_properties import ProductProperties


@receiver(post_save, sender=ProductProperties)
@receiver(post_delete, sender=ProductProperties)
def delete_images_cache(sender, instance, **kwargs):
    """Удаляет кеш при изменении особенностей продукта"""
    product_pk = instance.product

    cache_keys = [
        f"product_detail_{product_pk}",
    ]

    cache.delete_many(cache_keys)
