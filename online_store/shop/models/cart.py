from django.db import models
from django.contrib.auth.models import User
from .product import Product, ProductSeller
from .seller import Seller

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    selected_seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
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