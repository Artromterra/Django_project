from django.contrib import admin
from django.urls import path

from .views import (
    ProductDetailView,
    ProductListView,
    OrderUserView,
    OrderDeliveryView,
    OrderPayView,
    OrderConfirmView,
    OrderHistoryView,
    OrderDetailView,
    CartAddView,
    CartRemoveView,
    CartUpdateView,
    CartView,
    TestDiscountView, # убрать после теста
)


app_name = "shop"


urlpatterns = [
    path("products/", ProductListView.as_view(), name="products_list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="products_detail"),
    path("order/<int:pk>", OrderUserView.as_view(), name="order_user"),
    path("order-delivery/", OrderDeliveryView.as_view(), name="order_delivery"),
    path("order-pay/", OrderPayView.as_view(), name="order_pay"),
    path("order-confirm/", OrderConfirmView.as_view(), name="order_confirm"),
    path("order-history/", OrderHistoryView.as_view(), name="order_history"),
    path("order-detail/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("cart/add/", CartAddView.as_view(), name="cart_add"),
    path("cart/remove/", CartRemoveView.as_view(), name="cart_remove"),
    path("cart/update/", CartUpdateView.as_view(), name="cart_update"),
    path("cart/", CartView.as_view(), name="cart"),
    path("test/", TestDiscountView.as_view(), name="test_discount"), # убрать после теста
]
