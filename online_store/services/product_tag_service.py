from django.contrib.auth.models import User
from django.core.cache import cache

from typing import Optional

from shop.models.product import ProductTag
from dto.product_tag_dto import ProductTagDTO


class ProductTagService:
    def __init__(self, user: User):
        self.user = user

    def get_tags_to_product_detail(
        self, product_pk: int
    ) -> Optional[ProductTagDTO]:
        """Выдает теги продукта для детальной страницы продукта"""
        try:
            cache_key = f"tags_to_product_detail_{product_pk}"
            cache_data = cache.get(cache_key)
            if cache_data:
                return cache_data

            tags = ProductTagDTO.from_objects(
                ProductTag.objects.filter(product__pk=product_pk).all()
            )
            if not tags:
                ProductTag.DoesNotExist(
                    f"Теги для продукта {product_pk} не найдены."
                )

            cache.set(cache_key, tags, 3600 * 24)
            return tags

        except Exception as ex:
            error_type = type(ex).__name__
            message = (
                "Ошибка при получении тегов "
                f"продукта: {error_type} - {ex}"
            )
            raise Exception(message)
