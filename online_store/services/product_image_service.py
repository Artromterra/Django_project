from django.contrib.auth.models import User
from django.core.cache import cache

from typing import Optional

from shop.models.product import ProductImage
from dto.product_image_dto import ProductImageDTO


class ProductImageService:
    def __init__(self, user: User):
        self.user = user

    def get_images_to_product_detail(
        self, product_pk: int
    ) -> Optional[ProductImageDTO]:
        """Выдает изображения продукта для детальной страницы продукта"""
        try:
            cache_key = f"images_to_product_detail_{product_pk}"
            cache_data = cache.get(cache_key)
            if cache_data:
                return cache_data

            images = ProductImageDTO.from_objects(
                ProductImage.objects.filter(product__pk=product_pk).all()
            )
            if not images:
                ProductImage.DoesNotExist(
                    f"Изображения для продукта {product_pk} не найдены."
                )

            cache.set(cache_key, images, 3600 * 24)
            return images

        except Exception as ex:
            error_type = type(ex).__name__
            message = (
                "Ошибка при получении изображений "
                f"продукта: {error_type} - {ex}"
            )
            raise Exception(message)
