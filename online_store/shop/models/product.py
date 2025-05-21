from django.db import models
from django.urls import reverse

from decimal import Decimal

from .category import Category
from .seller import Seller


# Product main model
class Product(models.Model):
    objects = models.Manager()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.title

    # DB fields
    title = models.CharField(blank=False, max_length=100, db_index=True)
    description = models.TextField(blank=False, max_length=5000, db_index=True)
    short_description = models.CharField(blank=False, max_length=100)
    price = models.DecimalField(default=0, max_digits=8, decimal_places=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.00"))
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # DB relatives
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    sellers = models.ManyToManyField('Seller', through='ProductSeller', related_name="products")
    images: models.Manager["ProductImage"]
    product_sellers: models.Manager["ProductSeller"]

    def get_absolute_url(self):
        return reverse('shop:products_detail', kwargs={'pk': self.pk})

    def get_price(self):
        if self.price == 0:
            seller_obj = ProductSeller.objects.filter(
                product=self.pk
            ).first()
            return seller_obj.price
        return self.price


class ProductSeller(models.Model):
    objects = models.Manager()

    class Meta:
        verbose_name = "Product Seller"
        verbose_name_plural = "Product Sellers"
        unique_together = ('product', 'seller')

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_sellers')
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='product_sellers')
    free_shipping = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=0)
    amount = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.title} - {self.seller.name}"


# Product image
def product_images_directory_path(instance, filename: str) -> str:
    return "products/product_{pk}/images/{filename}".format(
        pk=instance.product.pk,
        filename=filename,
    )


class ProductImage(models.Model):
    # DB fields
    image = models.ImageField(upload_to=product_images_directory_path, null=False)
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
