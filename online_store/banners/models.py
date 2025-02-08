from django.db import models

from products.models import Product
from categories.models import Category


def banner_category_directory_path(
    instance: "BannerCategory", filename: str
) -> str:
    category_name = (instance.category.name).replace(" ", "_").lower()
    return f"banners/categories/banner_{category_name}_{filename}"


def banner_product_directory_path(
    instance: "BannerProduct", filename: str
) -> str:
    product_title = (instance.product.title).replace(" ", "_").lower()
    return f"banners/products/banner_{product_title}_{filename}"


class BannerProduct(models.Model):
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        related_name="banner",
        verbose_name="Товар",
        null=False,
        blank=False,
    )
    image = models.ImageField(
        upload_to=banner_product_directory_path,
        verbose_name="Изображение баннера",
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(
        verbose_name="Активен",
        null=False,
        default=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Баннер продукта - {self.product.title}"


class BannerCategory(models.Model):
    category = models.OneToOneField(
        Category,
        on_delete=models.CASCADE,
        related_name="banner",
        verbose_name="Категория",
        null=False,
        blank=False,
    )
    image = models.ImageField(
        upload_to=banner_category_directory_path,
        verbose_name="Изображение баннера",
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(
        verbose_name="Активен",
        null=False,
        default=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Баннер категории - {self.category.title}"
