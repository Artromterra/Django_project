from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views import View

from services.product_service import ProductService


# TODO: Remove the check_integration_with_frontend view function
#  - it is needed to check integration with the base frontend
def check_integration_with_frontend(request: HttpRequest) -> HttpResponse:
    return render(request, "base.html")


class ProductDetailView(View):
    template_name = "product.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Детальная страница продукта"""
        product_service = ProductService(request.user)
        product = product_service.get_product_detail(pk)
        context = {
            "object": product,
            "images": None,
            "features": None,
            "properties": None,
            "tags": None,
        }
        return render(request, self.template_name, context)
