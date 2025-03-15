from django.db import models

from .cart import Cart


class Order(models.Model):
    """
    Заказ пользователя

    Arguments:
        city (str): город доставки
        address (str): адрес доставки
        express_delivery (bool): экспресс доставка
        payment_method (str): способ оплаты (онлайн картой или со случайного чужого счёта)
        created_at (datetime): дата создания заказа
        cart (Cart): внешний ключ - корзина, которая была использована для создания заказа
    """
    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'

    SELF_CARD = 'SC'
    RANDOM_CARD = 'RC'
    CARD_CHOICES = {
        SELF_CARD: 'Онлайн картой',
        RANDOM_CARD: 'Онлайн со случайного чужого счёта'
    }

    city = models.CharField('City', max_length=100)
    address = models.CharField('Address', max_length=500)
    express_delivery = models.BooleanField('Express Delivery', default=False)
    payment_method = models.CharField(
        'Payment Method',
        max_length=2,
        choices=CARD_CHOICES,
        default=SELF_CARD,
    )
    created_at = models.DateTimeField('Created at', auto_now_add=True)

    cart = models.OneToOneField(Cart, on_delete=models.CASCADE, related_name='order')

    def __str__(self):
        return f'Заказ № {self.pk}, пользователь {self.cart.user.username}'
