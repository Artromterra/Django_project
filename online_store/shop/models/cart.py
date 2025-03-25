from django.db import models
from profiles.models import User
from .product import Product, ProductSeller
from .seller import Seller


class Cart(models.Model):
    """
    Корзина продуктов пользователя

    Arguments:
        user (User): внешний ключ - пользователь, которому принадлежит корзина
        session_key (str): ключ сессии
        created_at (datetime): дата создания корзины
        cart_items (List[CartItem]): все продукты, которые находятся в карточке
    """
    objects = models.Manager()

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
    """
    Карточка товара

    Arguments:
        cart (Cart): внешний ключ - корзина, к которой принадлежит товар
        product (Product): внешний ключ - продукт
        selected_seller (Seller): внешний ключ - продавец
        quantity (int): количество товара в корзине
    """
    objects = models.Manager()

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

    def __str__(self):
        return f'{self.cart.pk} {self.product.title} {self.selected_seller.name}'
