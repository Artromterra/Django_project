from django.db import models
from profiles.models import User
from shop.models import Product


class Comparison(models.Model):
    user_comparison = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_comparison')
    product_comparison = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_for_comparison')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_comparison'
        verbose_name = 'product comparison'