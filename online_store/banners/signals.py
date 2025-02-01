from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Banner


@receiver(post_save, sender=Banner)
def clear_banner_cache_on_save(sender, instance, **kwargs):
    """Сброс кеша при сохранении баннера"""
    cache.delete("banners_homepage")


@receiver(post_delete, sender=Banner)
def clear_banner_cache_on_delete(sender, instance, **kwargs):
    """Сброс кеша при удалении баннера"""
    cache.delete("banners_homepage")
