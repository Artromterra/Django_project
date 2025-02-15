from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from banners.models.banner_product import BannerProduct
from banners.models.banner_category import BannerCategory


# сброс кеша для баннеров продукта
@receiver(post_save, sender=BannerProduct)
def clear_banner_product_cache_on_save(sender, instance, **kwargs):
    """Сброс кеша при сохранении баннера"""
    cache.delete("banners_product_homepage")


@receiver(post_delete, sender=BannerProduct)
def clear_banner_product_cache_on_delete(sender, instance, **kwargs):
    """Сброс кеша при удалении баннера"""
    cache.delete("banners_product_homepage")


# сброс кеша для баннеров категорий
@receiver(post_save, sender=BannerCategory)
def clear_banner_category_cache_on_save(sender, instance, **kwargs):
    """Сброс кеша при сохранении баннера"""
    cache.delete("banners_category_homepage")


@receiver(post_delete, sender=BannerCategory)
def clear_banner_category_cache_on_delete(sender, instance, **kwargs):
    """Сброс кеша при удалении баннера"""
    cache.delete("banners_category_homepage")
