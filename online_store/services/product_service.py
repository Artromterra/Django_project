from django.contrib.auth.models import User
from django.db.models.query import QuerySet
from django.db.models import Count
from django.core.cache import cache

from typing import Optional, Dict

from shop.models.product import Product
from dto.product_dto import ProductDTO


class ProductService:
    def __init__(self, user: User):
        self.user = user

    def get_product_detail(self, product_pk: int) -> Optional[ProductDTO]:
        try:
            cache_key = f"product_detail_{product_pk}"
            cache_data = cache.get(cache_key)
            if cache_data:
                return cache_data

            product = ProductDTO.from_object(
                Product.objects.filter(pk=product_pk).first()
            )
            if not product:
                Product.DoesNotExist(f"Продукт {product_pk} не найден.")

            cache.set(cache_key, product, 3600 * 24)
            return product

        except Exception as ex:
            error_type = type(ex).__name__
            message = f"Ошибка при получении продукта: {error_type} - {ex}"
            raise Exception(message)
