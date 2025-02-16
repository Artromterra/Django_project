from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from .models.product import Product
from django.forms.models import model_to_dict

# TODO: Remove the check_integration_with_frontend view function
#  - it is needed to check integration with the base frontend
def check_integration_with_frontend(request: HttpRequest) -> HttpResponse:
    return render(request, "base.html")

# def product_characteristic(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     characteristics = model_to_dict(product)  # Преобразуем объект в словарь
#     return render(request,
#                   'product_characteristic_template.html',
#                   {'product': product, 'characteristics': characteristics})
