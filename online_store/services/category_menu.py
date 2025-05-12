from django.core.cache import cache


from services.settings_service import SettingsService
from shop.models import Category


class CategoryMenuService:
    CACHE_KEY = 'category_menu'

    @classmethod
    def get_active_categories(cls):
        """
        Возвращает активные категории, в которых есть активные товары.
        """
        return Category.objects.filter(
            is_active=True,
            # products__is_active=True
        )

    @classmethod
    def get_sub_categories(cls):
        return Category.objects.filter(
            parent_category_id__isnull=False,
        )


    @classmethod
    def get_cache_timeout(cls):
        """
        Возвращает время жизни кеша из сервиса настроек.
        """
        return SettingsService.get_cache_timeout()

    @classmethod
    def get_cached_menu(cls):
        menu = cache.get(cls.CACHE_KEY)

        if menu is None:
            menu = cls.get_active_categories()
            cache.set(cls.CACHE_KEY, menu, timeout=cls.get_cache_timeout())

        return menu

    @classmethod
    def clear_cache(cls):
        """
        Очищает кеш меню категорий.
        """
        cache.delete(cls.CACHE_KEY)
