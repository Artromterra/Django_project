from django.contrib.auth.models import User
from django.core.cache import cache

from typing import Optional

from shop.models.properties import ProductProperties
from dto.product_properties_dto import ProductPropertiesDTO


class ProductPropertiesService:
    def __init__(self, user: User):
        self.user = user

    def get_properties_to_product_detail(
        self, product_pk: int
    ) -> Optional[ProductPropertiesDTO]:
        """Выдает характеристики продукта для детальной страницы продукта"""
        try:
            cache_key = f"properties_to_product_detail_{product_pk}"
            cache_data = cache.get(cache_key)
            if cache_data:
                return cache_data

            properties = ProductPropertiesDTO.from_objects(
                ProductProperties.objects.filter(product__pk=product_pk).all()
            )
            if not properties:
                ProductProperties.DoesNotExist(
                    f"Характеристики для продукта {product_pk} не найдены."
                )

            cache.set(cache_key, properties, 3600 * 24)
            return properties

        except Exception as ex:
            error_type = type(ex).__name__
            message = (
                "Ошибка при получении характеристик "
                f"продукта: {error_type} - {ex}"
            )
            raise Exception(message)
