from django.contrib import admin
from django.urls import path

from .views import (
    ProductDetailView,
    ProductListView,
    OrderUserView,
    OrderDeliveryView,
    OrderPayView,
    OrderConfirmView,
    CartView,
    OrderHistoryView,
    OrderDetailView,
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
    path('cart/', CartView.as_view(), name='cart'),
]
