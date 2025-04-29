from decimal import Decimal
from typing import Sequence

from django.db.models.aggregates import Max

from shop.models import Category
from shop.models.discount import Discount
from shop.models.product import Product, ProductSeller
from services.cart_service import CartService


def get_final_price_for_cart_product(product: Product):
    """
    получение максимальной цены продукта у продавца, если цена не указана изначально в модели
    """
    if product.price > 0:
        return product.price
    else:
        price_max = (ProductSeller.objects.
        filter(product_id=product.id).
        aggregate(Max('price'))['price__max']
        )
        return price_max

def check_type(discount: Discount, max_price: Decimal):
    if discount:
        if discount.discount_type == 'percentage':
            price = max_price * (100 - discount.value) / 100
            return price
        else:
            price = max_price - discount.value
            if price <= 0:
                return 1
            return price
    return max_price


class DiscountService:
    def __init__(self, request):
        self.request = request
        self.cart_service = CartService(self.request)


    def get_max_price(self, product: Product):
        """
        получение максимальной цены продукта у продавца, если цена не указана изначально в модели
        """
        return get_final_price_for_cart_product(product)


    def get_max_priority_discount(self):
        """
        получение объекта скидки с максимальным приоритетом
        """
        priority_max_obj = (
            Discount.objects.all().
            order_by('-priority').first()
        )
        return priority_max_obj


    def one_product_discount_price(self, product: Product):
        """
        получение окончательной цены для каждого товара при наличии скидки
        """
        max_price = self.get_max_price(product=product)
        discount = (Discount.objects.
        prefetch_related('products').
        filter(products__id=product.id).
        order_by('-priority').first()
        )
        price = check_type(discount=discount, max_price=max_price)
        return price


    def discount_on_each_product_in_cart(self):
        """суммарная цена товара в корзине с учетом скидки на каждый товар"""
        cart_items = self.cart_service.get_cart_items()
        price = 0
        for item in cart_items:
            price += item.quantity * self.one_product_discount_price(product=item.product)
        return price


    def discount_by_category(self, category: Sequence[Category]):
        """расчет цены товара при скидке на категорию"""
        cart_items = self.cart_service.get_cart_items()
        total_price = 0
        category_list = [item.id for item in category]
        for item in cart_items:
            max_price = self.get_max_price(product=item.product)
            if item.product.category_id in category_list:
                discount = (Discount.objects.
                            prefetch_related('categories').
                            filter(categories__id=item.product.category_id).
                            first())
                price = check_type(discount=discount, max_price=max_price)
                total_price += item.quantity * price
            else:
                total_price += item.quantity * max_price
        return total_price


    def discount_price_on_cart(self):
        """
        получение окончательной цены корзины, если скидка на всю корзину
        """
        discount = Discount.objects.filter(cart_quantity__gt=0, cart_price__gt=0).first()
        total_price = self.cart_service.get_cart_total_price()
        total_quantity = self.cart_service.get_cart_count()
        if total_price >= discount.cart_price and total_quantity >= discount.cart_quantity:
            if discount.discount_type == 'percentage':
                price = total_price * (100 - discount.value) / 100
            else:
                price = total_price - discount.value
                if price <= 0:
                    return 1
            return price
        return total_price
