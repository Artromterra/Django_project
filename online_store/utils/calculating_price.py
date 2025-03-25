from django.db.models import QuerySet

from shop.models.cart import CartItem
from shop.models.order import OrderDeliveryPrice, Order

"""
Подсчет общей цены заказа с учетом условий доставки и общей цены
корзины
"""

def calculate_price(
        cart_queryset: QuerySet[CartItem],
        order: Order,
        delivery_price: OrderDeliveryPrice,
) -> float:
    one_seller = False
    ids = [cart_item.selected_seller_id for cart_item in cart_queryset]
    if len(set(ids)) == 1:
        one_seller = True
    total_prod_price = sum(item.get_final_price() * item.quantity for item in cart_queryset)
    if order.delivery == 'RD':
        if total_prod_price < delivery_price.order_price_for_delivery or not one_seller:
            result_price = total_prod_price + delivery_price.regular_price
        else:
            result_price = total_prod_price
    else:
        result_price = total_prod_price + delivery_price.express_price
    return result_price