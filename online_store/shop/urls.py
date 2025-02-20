from django.contrib import admin
from django.urls import path

from .views import check_integration_with_frontend
# from .views import product_properties

app_name = "shop"

# TODO: Remove the check_integration_with_frontend view function
#  - it is needed to check integration with the base frontend
urlpatterns = [
    path("check-frontend/", check_integration_with_frontend, name="check-frontend"),
    # path("product-properties/<int:product_id>/", product_properties, name="product-characterictic")
]
