from urllib import request

from django.utils.crypto import get_random_string
from django.shortcuts import get_object_or_404
from shop.models.cart import Cart, CartItem
from shop.models.product import Product
from shop.models.seller import Seller

class CartService:
    def __init__(self, request):
        self.request = request
        self.cart = self.get_or_create_cart()


    def get_or_create_cart(self):
        """ Получает или создаёт корзину для пользователя или сессии """
        if self.request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user_id=self.request.user.id)
        else:
            session_key = self.request.session.get("cart_key")
            if not session_key:
                session_key = get_random_string(40)
                self.request.session["cart_key"] = session_key
            cart, _ = Cart.objects.get_or_create(session_key=session_key)
        return cart


    def add_product(self, product_id, seller_id, quantity=1):
        """ Добавляет товар в корзину или обновляет количество """
        product = get_object_or_404(Product, id=product_id)
        seller = get_object_or_404(Seller, id=seller_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=self.cart,
            product=product,
            selected_seller=seller
        )
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()


    def remove_product(self, product_id, seller_id):
        """ Удаляет товар из корзины """
        CartItem.objects.filter(
            cart=self.cart,
            product_id=product_id,
            selected_seller_id=seller_id
        ).delete()


    def update_product_quantity(self, product_id, seller_id, delta):
        """ Изменяет количество товара """
        cart_item = CartItem.objects.filter(
            cart=self.cart,
            product_id=product_id,
            selected_seller_id=seller_id
        ).first()
        if cart_item:
            cart_item.quantity += delta
            if cart_item.quantity <= 0:
                cart_item.delete()
            else:
                cart_item.save()


    def get_cart_items(self):
        """ Возвращает список товаров в корзине """
        return self.cart.cart_items.all()


    def get_cart_total_price(self):
        """получение итоговой цены корзины без скидок"""
        from services.discount_service import DiscountService

        cart_items = self.get_cart_items()
        total_price = 0
        for item in cart_items:
            discount = DiscountService(self.request)
            total_price += item.quantity * discount.get_max_price(product=item.product)
        return total_price


    def get_cart_count(self):
        """ Возвращает количество товаров в корзине """
        return sum(item.quantity for item in self.cart.cart_items.all())


    def merge_carts(self):
        """ Объединяет корзины после авторизации """
        if self.request.user.is_authenticated:
            guest_cart = Cart.objects.filter(session_key=self.request.session.get("cart_key")).first()
            user_cart, _ = Cart.objects.get_or_create(user=self.request.user)

            if guest_cart and guest_cart != user_cart:
                for item in guest_cart.cart_items.all():
                    user_cart_service = CartService(self.request)
                    user_cart_service.add_product(item.product.id, item.selected_seller.id, item.quantity)
                guest_cart.delete()