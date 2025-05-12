from decimal import Decimal

from django.db.models import QuerySet

from shop.models.cart import CartItem
from shop.models.order import OrderDeliveryPrice, Order

"""
Подсчет общей цены заказа с учетом условий доставки и общей цены
корзины
"""

def calculate_price(
        total_prod_price: float,
        cart_queryset: QuerySet[CartItem],
        order: Order,
) -> float:
    one_seller = False
    price_for_delivery = OrderDeliveryPrice.objects.first()
    ids = [cart_item.selected_seller_id for cart_item in cart_queryset]
    if len(set(ids)) == 1:
        one_seller = True
    if order.delivery == 'RD':
        if total_prod_price < price_for_delivery.order_price_for_delivery or not one_seller:
            result_price = total_prod_price + float(price_for_delivery.regular_price)
        else:
            result_price = total_prod_price
    else:
        result_price = total_prod_price + float(price_for_delivery.express_price)
    return result_price