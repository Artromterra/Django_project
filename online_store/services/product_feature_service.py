from django.contrib.auth.models import User
from django.core.cache import cache

from typing import Optional

from shop.models.product import ProductFeature
from dto.product_features_dto import ProductFeatureDTO


class ProductFeatureService:
    def __init__(self, user: User):
        self.user = user

    def get_features_to_product_detail(
        self, product_pk: int
    ) -> Optional[ProductFeatureDTO]:
        """Выдает особенности продукта для детальной страницы продукта"""
        try:
            cache_key = f"fatures_to_product_detail_{product_pk}"
            cache_data = cache.get(cache_key)
            if cache_data:
                return cache_data

            features = ProductFeatureDTO.from_objects(
                ProductFeature.objects.filter(product__pk=product_pk).all()
            )
            if not features:
                ProductFeature.DoesNotExist(
                    f"Особенности для продукта {product_pk} не найдены."
                )

            cache.set(cache_key, features, 3600 * 24)
            return features

        except Exception as ex:
            error_type = type(ex).__name__
            message = (
                "Ошибка при получении особенностей "
                f"продукта: {error_type} - {ex}"
            )
            raise Exception(message)
