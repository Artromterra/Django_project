from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView
from django.forms.models import model_to_dict
from django.core.cache import cache

from dto.product_dto import ProductDetailDTO
from services.product_service import ProductService
from .models.product import Product


# TODO: Remove the check_integration_with_frontend view function
#  - it is needed to check integration with the base frontend
def check_integration_with_frontend(request: HttpRequest) -> HttpResponse:
    return render(request, "base.html")


class ProductDetailView(DetailView):
    template_name = "product.html"
    model = Product
    context_object_name = "product"

    def get_object(self):
        product_service = ProductService(self.request.user)
        product_pk = self.kwargs["pk"]
        queryset = self.get_queryset()

        data = product_service.get_product_detail(product_pk, queryset)
        return data


# def product_properties(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     properties = model_to_dict(product)  # Преобразуем объект в словарь
#     return render(request,
#                   'product_properties_template.html',
#                   {'product': product, 'properties': properties})
