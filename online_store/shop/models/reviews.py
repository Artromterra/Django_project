from django.db import models
from .product import Product


class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    author = models.CharField(max_length=100)
    content = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        formatted_date = self.created_at.strftime('%Y-%m-%d %H:%M')
        return f'{self.product.title} {self.author} {formatted_date}'