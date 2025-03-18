from django.contrib import admin
from django.urls import path

from .views import (
    ProductDetailView,
    ProductListView,
    OrderUserView,
    OrderDeliveryView,
    OrderPayView,
    OrderConfirmView,
)

app_name = "shop"

urlpatterns = [
    path("products/", ProductListView.as_view(), name="products_list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="products_detail"),
    path("order/<int:pk>", OrderUserView.as_view(), name="order_user"),
    path("order-delivery/<int:pk>", OrderDeliveryView.as_view(), name="order_delivery"),
    path("order-pay/<int:pk>", OrderPayView.as_view(), name="order_pay"),
    path("order-confirm/<int:pk>", OrderConfirmView.as_view(), name="order_confirm"),
    # path("product-properties/<int:product_id>/", product_properties, name="product-characterictic")
]
