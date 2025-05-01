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
    DiscountView,
    OrderPayment,
    OrderPaymentProgress,
)


app_name = "shop"


urlpatterns = [
    path("products/", ProductListView.as_view(), name="products_list"),
    path("products/<int:pk>/", ProductDetailView.as_view(), name="products_detail"),
    path("order/<int:pk>", OrderUserView.as_view(), name="order_user"),
    path("order-delivery/", OrderDeliveryView.as_view(), name="order_delivery"),
    path("order-pay/", OrderPayView.as_view(), name="order_pay"),
    path("order-confirm/", OrderConfirmView.as_view(), name="order_confirm"),
    path("order-confirm/payment/", OrderPayment.as_view(), name="payment"),
    path("order-confirm/payment/progressPayment", OrderPaymentProgress.as_view(), name="payment_progress"),
    path("order-history/", OrderHistoryView.as_view(), name="order_history"),
    path("order-detail/<int:pk>/", OrderDetailView.as_view(), name="order_detail"),
    path("cart/add/", CartAddView.as_view(), name="cart_add"),
    path("cart/remove/", CartRemoveView.as_view(), name="cart_remove"),
    path("cart/update/", CartUpdateView.as_view(), name="cart_update"),
    path("cart/", CartView.as_view(), name="cart"),
    path("discount/", DiscountView.as_view(), name="discount"),
]
