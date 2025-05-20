from django.db import models
from profiles.models import User
from shop.models import Product


class ComparisonItem(models.Model):
    objects = models.Manager()

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_comparison'
        verbose_name = 'product comparison'

    def __str__(self):
        return f'Product: {self.product.title},  User: {self.user.username}'