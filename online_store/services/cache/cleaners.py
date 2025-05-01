"""The module responsible for clearing the cache."""
from typing import List
from abc import ABC, abstractmethod
from logging import getLogger

from django.core.cache import cache

logger = getLogger("main.services.cache")


class BaseCleaner(ABC):
    """
    Base cleaner of the cache.

    Args:
        name (str) - app name.
    """

    name: str = "all"

    @classmethod
    @abstractmethod
    def clean(cls):
        """Clean cache."""
        pass


class AllCleaner(BaseCleaner):
    """Cleaner of the cache for all apps."""

    name = "shop"

    @classmethod
    def clean(cls):
        """Clean cache."""
        logger.debug("Clear cache for all apps.")
        cache.clear()


class AppCleaner(BaseCleaner):
    """
    Base cleaner of the cache for app.

    Args:
        name (str) - app name.
        keys (List[str]) - list of prefix for removing from cache.
    """

    name = ""
    keys: List[str] = list()

    def clean(self):
        """Clean cache."""
        logger.debug("Clean cache for app %s", self.name)
        if hasattr(cache, "_cache"):
            for key in cache._cache:
                for prefix in self.keys:
                    if key.startswith(prefix):
                        cache._cache.pop(key)
                        break


class ShopCleaner(AppCleaner):
    """Shop app cleaner."""

    name = "shop"
    keys: List[str] = [
        "product_detail",
        "products_list",
        "category_menu",
    ]


class BannerCleaner(AppCleaner):
    """Banners app cleaner."""

    name = "banners"
    keys: List[str] = ["banners_",]
