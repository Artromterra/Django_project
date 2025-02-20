from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from shop.models.product import Product


@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def delete_images_cache(sender, instance, **kwargs):
    """Удаляет кеш при изменении продукта"""
    product_pk = instance.pk

    cache_keys = [
        f"product_detail_{product_pk}",
    ]

    cache.delete_many(cache_keys)
