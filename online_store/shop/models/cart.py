from django.db import models
from profiles.models import User
from .product import Product, ProductSeller
from .seller import Seller

class Cart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='cart',
    )
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f'Корзина № {self.pk} Пользователь {self.user.username}'
        return f'Anonymous {self.session_key}'


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='cart_items',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='cart_product_items',
    )
    selected_seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='cart_selected_seller',
    )
    quantity = models.PositiveIntegerField(default=1)

    def get_final_price(self):
        seller_product = ProductSeller.objects.get(
            product=self.product,
            seller=self.selected_seller
        )
        price = seller_product.price
        if self.product.discount > 0:
            price = price * (1 - self.product.discount / 100)
        return price

    def get_available_sellers(self):
        return Seller.objects.filter(product_sellers__product=self.product)