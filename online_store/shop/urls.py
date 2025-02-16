from django.contrib import admin
from django.urls import path

from .views import check_integration_with_frontend
# from .views import product_characteristic

app_name = "shop"

# TODO: Remove the check_integration_with_frontend view function
#  - it is needed to check integration with the base frontend
urlpatterns = [
    path("check-frontend/", check_integration_with_frontend, name="check-frontend"),
    # path("product-characteristic/<int:product_id>/", product_characteristic, name="product-characterictic")
]
