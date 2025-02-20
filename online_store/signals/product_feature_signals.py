from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from shop.models.product import ProductFeature


@receiver(post_save, sender=ProductFeature)
@receiver(post_delete, sender=ProductFeature)
def delete_images_cache(sender, instance, **kwargs):
    """Удаляет кеш при изменении особенностей продукта"""
    product_pk = instance.product_id

    cache_keys = [
        f"fatures_to_product_detail_{product_pk}",
    ]

    cache.delete_many(cache_keys)
