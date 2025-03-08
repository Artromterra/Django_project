from typing import Optional
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.generic import DetailView, ListView
from django.forms.models import model_to_dict
from django.core.cache import cache

from dto.product_list_dto import ProductListDTO
from services.settings_service import SettingsService
from services.product_list_service import sort_list_products_dto
from .models.product import Product


# TODO: Remove the check_integration_with_frontend view function
#  - it is needed to check integration with the base frontend
def check_integration_with_frontend(request: HttpRequest) -> HttpResponse:
    return render(request, "base.html")


class ProductDetailView(DetailView):
    template_name = "product.html"
    model = Product
    context_object_name = "product"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("images", "features", "tags", "properties")
        )

    def get_object(self):
        cache_key = f"product_detail_{self.kwargs["pk"]}"
        cache_data = cache.get(cache_key)
        if cache_data:
            return cache_data

        object = super().get_object()

        cache.set(cache_key, object, SettingsService.get_cache_timeout())
        return object


# def product_properties(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     properties = model_to_dict(product)  # Преобразуем объект в словарь
#     return render(request,
#                   'product_properties_template.html',
#                   {'product': product, 'properties': properties})


class ProductListView(ListView):
    template_name = "catalog.html"
    model = Product
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        sort_query = self.request.GET.get("sort", "-orders")

        cache_key = "products_list"
        cache_data = cache.get(cache_key)
        if cache_data:
            products_dto_sorted = sort_list_products_dto(
                products_list_dto=cache_data, sort_query=sort_query
            )
            return {self.context_object_name: products_dto_sorted}

        products = Product.objects.filter(is_active=True).all()
        products_dto = ProductListDTO.from_objects(products)
        cache.set(cache_key, products_dto, SettingsService.get_cache_timeout())

        products_dto_sorted = sort_list_products_dto(
            products_list_dto=products_dto, sort_query=sort_query
        )
        return {self.context_object_name: products_dto_sorted}
