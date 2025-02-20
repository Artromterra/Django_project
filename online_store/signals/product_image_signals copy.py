from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from shop.models.product import ProductTag


@receiver(post_save, sender=ProductTag)
@receiver(post_delete, sender=ProductTag)
def delete_images_cache(sender, instance, **kwargs):
    """Удаляет кеш при изменении особенностей продукта"""
    product_pk = instance.product_id

    cache_keys = [
        f"tags_to_product_detail_{product_pk}",
    ]

    cache.delete_many(cache_keys)
