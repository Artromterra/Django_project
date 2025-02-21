from django.db import models
from .product import Product
from .seller import Seller



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