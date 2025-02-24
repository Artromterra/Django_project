from django.db import models

from profiles.models import User
from shop.models import Product


class ViewedProducts(models.Model):

    viewed_at = models.DateTimeField('viewing time', auto_now_add=True)
    viewed_by_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewed_products')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='viewed_products')

    class Meta:
        db_table = 'viewed_products'
        verbose_name = 'viewed product'
        verbose_name_plural = 'viewed products'

    def __str__(self):
        return 'Просмотрен продукт {}, пользователем {}'.format(
            self.product.title,
            self.viewed_by_user.username,
        )
