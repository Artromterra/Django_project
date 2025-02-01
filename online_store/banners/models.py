from django.db import models

from products.models import Product


def user_avatar_directory_path(instance: "Banner", filename: str) -> str:
    product_name = (instance.product.name).replace(" ", "_").lower()
    banner_type = (instance.banner_type).replace(" ", "_").lower()
    return f"{product_name}/banners/banner_{banner_type}_{filename}"


class Banner(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="banners",
        verbose_name="Товар",
        null=False,
        blank=False,
    )
    image = models.ImageField(
        upload_to=user_avatar_directory_path,
        verbose_name="Изображение баннера",
        null=False,
        blank=False,
    )
    is_active = models.BooleanField(
        verbose_name="Активен",
        null=False,
        default=True,
    )
    banner_type = models.CharField(
        max_length=50,
        choices=[
            ("main", "Главный баннер"),
            ("sale", "Скидка"),
            ("new", "Новинка"),
        ],
        default="main",
        verbose_name="Тип баннера",
        null=False,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "banner_type"],
                name="unique_product_banner_type"
            )
        ]

    def __str__(self):
        return f"Баннер для {self.product.name} ({self.banner_type})"
