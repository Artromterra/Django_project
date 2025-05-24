from django.db import models

from profiles.models import User
from . import Product
from .cart import Cart, CartItem
from .seller import Seller


class Order(models.Model):
    """
    Заказ пользователя
    """
    objects = models.Manager()

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    REGULAR_DELIVERY = 'RD'
    EXPRESS_DELIVERY = 'ED'
    DELIVERY_CHOICES = {
        REGULAR_DELIVERY: 'Обычная доставка',
        EXPRESS_DELIVERY: 'Экспресс доставка',
    }

    SELF_CARD = 'SC'
    RANDOM_CARD = 'RC'
    CARD_CHOICES = {
        SELF_CARD: 'Онлайн картой',
        RANDOM_CARD: 'Онлайн со случайного чужого счёта'
    }

    city = models.CharField('City', max_length=100)
    address = models.CharField('Address', max_length=500)
    paid = models.BooleanField('Paid', default=False)
    delivery = models.CharField(
        'Delivery',
        max_length=2,
        choices=DELIVERY_CHOICES,
        default=REGULAR_DELIVERY,
    )
    payment_method = models.CharField(
        'Payment Method',
        max_length=2,
        choices=CARD_CHOICES,
        default=SELF_CARD,
    )
    total_price = models.DecimalField(
        'Total Price',
        decimal_places=0,
        max_digits=10,
        default=0,
    )
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_order', null=True)
    cart = models.OneToOneField(Cart, on_delete=models.SET_NULL, null=True, related_name='order')

    def __str__(self):
        if self.user:
            return f'Заказ № {self.pk}, пользователь {self.user.username}'
        return f'Заказ № {self.pk}, пользователь Anonymous'

    yookassa_payment_id = models.CharField(max_length=100, null=True, blank=True)


class OrderItem(models.Model):
    objects = models.Manager()

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_product_items',
    )
    selected_seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE,
        related_name='order_selected_seller',
    )
    quantity = models.PositiveIntegerField(default=1)

    def get_final_price(self):
        from services.discount_service import get_final_price_for_cart_product
        price = get_final_price_for_cart_product(product=self.product)
        return price

    def __str__(self):
        return f'{self.order.pk} {self.product.title} {self.quantity} {self.selected_seller.name}'



class OrderDeliveryPrice(models.Model):
    objects = models.Manager()
    class Meta:
        verbose_name = 'Order Delivery Price'
        verbose_name_plural = 'Order Delivery Prices'

    express_price = models.DecimalField(
        'Express Delivery Price',
        decimal_places=1,
        max_digits=7,
        default=0,
    )
    regular_price = models.DecimalField(
        'Regular Delivery Price',
        decimal_places=1,
        max_digits=7,
        default=0,
    )
    order_price_for_delivery = models.DecimalField(
        'Order Price For Delivery',
        decimal_places=1,
        max_digits=10,
        default=0,
    )

    def __str__(self):
        return 'Prices for order delivery'
