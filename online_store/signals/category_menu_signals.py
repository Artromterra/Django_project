from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from shop.models import Category, Product
from services.category_menu import CategoryMenuService

@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
@receiver(post_save, sender=Product)
@receiver(post_delete, sender=Product)
def clear_category_menu_cache(sender, **kwargs):
    """
    Сбрасывает кэш меню категорий при изменении данных.
    """
    CategoryMenuService.clear_cache()


