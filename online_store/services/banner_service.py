from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.db.models import Count
from django.core.cache import cache

from typing import Optional, Dict

from banners.models import Banner


class BannerService:
    def __init__(self, user: User):
        self.user = user

    def get_banners_to_homepage(self) -> Dict[str, QuerySet[Optional[Banner]]]:
        """
        ## Получить активные баннеры для главной страницы
        Выдает баннеры по группам:
        - основные
        - популярные
        - ограниченное издание
        - ограниченное предложение

        ### Вывод
        - Словарь с кверисетами, групированный по названиям групп
        """
        try:
            cache_data = cache.get("banners_homepage")
            if cache_data:
                return cache_data

            objects = (
                Banner.objects.filter(is_active=True)
                .select_related("product")
                .all()
            )

            # 3 больших основных баннера
            main_banners = objects.filter(banner_type="main").order_by(
                "-created_at"
            )[:3]
            objects = objects.exclude(
                id__in=main_banners.values_list("id", flat=True)
            )

            # популярные продукты
            popular_banners = (
                objects.filter(
                    banner_type="main", product__category__name="popular"
                )
                .annotate(orders_count=Count("product__orders"))
                .order_by("-orders_count")
            )

            # ограниченный тираж
            limited_edition_banners = objects.filter(
                banner_type="main", product__category__name="limited"
            ).order_by("product__count")

            # ограниченные предложения
            limited_offer_banners = (
                objects.filter(
                    banner_type="main",
                ).order_by("product__discount__exp_date")
            )[:3]

            result = {
                "main_banners": main_banners,
                "popular_banners": popular_banners,
                "limited_edition_banners": limited_edition_banners,
                "limited_offer_banners": limited_offer_banners,
            }

            cache.set("banners_homepage", result, timeout=600)
            return result

        except Exception as ex:
            class_error = type(ex).__name__
            message = (
                "Ошибка при подгрузке баннеров для главной страницы: "
                f"{class_error} - {ex}"
            )
            raise Exception(message)
