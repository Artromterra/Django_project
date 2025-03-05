from django.db import models
from profiles.models import User
from shop.models import Product


class ComparisonItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    session_key = models.CharField(max_length=255, null=True, blank=True)
    product_id = models.PositiveIntegerField()
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product_comparison'
        verbose_name = 'product comparison'