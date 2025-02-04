from django.db import models
from .category import Category


#Product main model
class Product(models.Model):
    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.title

    # DB fields
    title = models.CharField(blank=False, max_length=100, db_index=True)
    description = models.TextField(blank=False, max_length=5000, db_index=True)
    short_description = models.CharField(blank=False, max_length=100)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=False)

    # DB relatives
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")

# Product image
def product_images_directory_path(instance: "ProductImage", filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    # DB fields
    image = models.ImageField(upload_to=product_images_directory_path)
    description = models.CharField(max_length=200, null=False, blank=True)

    # DB relatives
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
