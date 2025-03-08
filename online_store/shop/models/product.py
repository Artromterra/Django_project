from django.db import models
from .category import Category
from .seller import Seller

# Product main model
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
    created_at = models.DateTimeField(auto_now_add=True)

    # DB relatives
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    sellers = models.ManyToManyField('Seller', through='ProductSeller', related_name="products")


class ProductSeller(models.Model):
    class Meta:
        verbose_name = "Product Seller"
        verbose_name_plural = "Product Sellers"
        unique_together = ('product', 'seller')

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_sellers')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='product_sellers')

    price = models.DecimalField(max_digits=8, decimal_places=2)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.title} - {self.seller.name}"

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


class ProductFeature(models.Model):
    # DB fields
    value = models.CharField(max_length=300, null=False, blank=True)

    # DB relatives
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="features"
    )


class ProductTag(models.Model):
    # DB fields
    name = models.CharField(max_length=50, null=False, blank=True)

    # DB relatives
    products = models.ManyToManyField(
        Product, related_name="tags"
    )
