from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.db.models import Count
from django.core.cache import cache

from typing import Optional, Dict

from banners.models import BannerProduct, BannerCategory
from dto.banners_dto import BannerProductDTO, BannerCategoryDTO


class BannerService:
    def __init__(self, user: User):
        self.user = user

    def get_banners_to_homepage(
        self,
    ) -> Dict[str, QuerySet[Optional[BannerProduct | BannerCategory]]]:
        """
        ## Получить активные баннеры для главной страницы
        Выдает баннеры по группам:
        - 3 баннера новинок
        - 3 баннера популярных категорий

        ### Вывод
        - Словарь с кверисетами, групированный по названиям групп
        """
        try:
            banners_product = cache.get("banners_product_homepage")
            banners_category = cache.get("banners_category_homepage")

            if not banners_product:
                # Большие баннеры для товаров новинок
                banners_product = BannerProductDTO.from_queryset(
                    BannerProduct.objects.filter(is_active=True)
                    .select_related("product")
                    .order_by("-created_at")[:3]
                )
                cache.set(
                    "banners_product_homepage", banners_product, timeout=600
                )

            if not banners_category:
                # Баннеры популярных категорий
                banners_category = BannerCategoryDTO.from_queryset(
                    BannerCategory.objects.filter(is_active=True)
                    .select_related("category")
                    .annotate(
                        orders_count=Count(
                            "category__products__oreders", distinct=True
                        )
                    )
                    .order_by("-orders_count")[:3]
                )
                cache.set(
                    "banners_category_homepage", banners_category, timeout=600
                )

            result = {
                "banners_product": banners_product,
                "banners_category": banners_category,
            }

            return result

        except Exception as ex:
            class_error = type(ex).__name__
            message = (
                "Ошибка при подгрузке баннеров для главной страницы: "
                f"{class_error} - {ex}"
            )
            raise Exception(message)
