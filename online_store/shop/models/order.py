from django.db import models

from .cart import Cart, CartItem


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

    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='order')
    # cart = models.ForeignKey(Cart, on_delete=models.CASCADE)

    def __str__(self):
        if self.cart.user is not None:
            return f'Заказ № {self.pk}, пользователь {self.cart.user.username}'
        return f'Заказ № {self.pk}, пользователь Anonymous'

    yookassa_payment_id = models.CharField(max_length=100, null=True, blank=True)


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
