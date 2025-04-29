from django.db import models
from .product import Product
from .category import Category

from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxValueValidator

class Discount(models.Model):
    objects = models.Manager()

    PERCENTAGE = 'percentage'
    FIXED_AMOUNT = 'fixed'

    DISCOUNT_TYPE_CHOICES = [
        (PERCENTAGE, _('Percentage')),
        (FIXED_AMOUNT, _('Fixed amount')),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Название скидки"))
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default=PERCENTAGE,
        verbose_name=_("Тип скидки")
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Величина скидки")
    )
    start_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата начала"))
    end_date = models.DateTimeField(null=True, blank=True, verbose_name=_("Дата окончания"))
    is_active = models.BooleanField(default=True, verbose_name=_("Активна"))
    priority = models.PositiveIntegerField(
        default=1,
        verbose_name=_("Вес скидки от 1 до 5"),
        validators=[MaxValueValidator(5)],
    )
    # поля для ввода значений при скидке на всю корзину
    cart_quantity = models.PositiveIntegerField(default=0, verbose_name=_("Количество товара в корзине"))
    cart_price = models.PositiveIntegerField(default=0, verbose_name=_("Итоговая стоимость товаров в корзине"))

    products = models.ManyToManyField(Product, blank=True, related_name='discounts', verbose_name=_("Продукты"))
    categories = models.ManyToManyField(Category, blank=True, related_name='discounts', verbose_name=_("Категории"))

    def __str__(self):
        return self.name

    def is_valid(self):
        """Проверяет, действует ли скидка в текущий момент."""
        from django.utils.timezone import now
        if not self.is_active:
            return False
        if self.start_date and self.end_date:
            return self.start_date <= now() <= self.end_date
        return True