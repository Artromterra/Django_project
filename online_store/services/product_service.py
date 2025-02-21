from typing import Optional

from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.core.cache import cache

from shop.models.product import Product
from services.settings_service import SettingsService
from dto.product_dto import ProductDetailDTO


class ProductService:
    def __init__(self, user: User):
        self.user = user

    def get_product_detail(
        self, product_pk: int, queryset: QuerySet[Optional[Product]]
    ) -> Optional[ProductDetailDTO]:
        """
        ### Данные для детальной страницы продукта
        Выдает продукт в виде ProductDetailDTO и все связанные с ним объекты:
        - features
        - images
        - properties
        - tags
        """
        try:

            cache_key = f"product_detail_{product_pk}"
            cache_data = cache.get(cache_key)
            if cache_data:
                return cache_data

            product_model = queryset.prefetch_related(
                "images", "features", "tags", "properties"
            ).get(pk=product_pk)

            product_dto = ProductDetailDTO.from_object(product_model)

            settings_service = SettingsService()
            cache.set(
                cache_key, product_dto, settings_service.get_cache_timeout()
            )
            return product_dto

        except Exception as ex:
            error_type = type(ex).__name__
            message = (
                f"Ошибка при получении данных продукта: {error_type} - {ex}"
            )
            raise Exception(message)
