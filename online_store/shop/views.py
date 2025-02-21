from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.forms.models import model_to_dict

from services.product_service import ProductService
from services.product_feature_service import ProductFeatureService
from services.product_image_service import ProductImageService
from services.product_properties_service import ProductPropertiesService
from services.product_tag_service import ProductTagService
from .models.product import Product


# TODO: Remove the check_integration_with_frontend view function
#  - it is needed to check integration with the base frontend
def check_integration_with_frontend(request: HttpRequest) -> HttpResponse:
    return render(request, "base.html")


class ProductDetailView(View):
    template_name = "product.html"

    def get(self, request: HttpRequest, pk: int) -> HttpResponse:
        """Детальная страница продукта"""
        user = request.user
        product_service = ProductService(user)
        product_images_service = ProductImageService(user)
        product_features_service = ProductFeatureService(user)
        product_properties_service = ProductPropertiesService(user)
        product_tags_service = ProductTagService(user)

        product = product_service.get_product_detail(pk)
        images = product_images_service.get_images_to_product_detail(pk)
        features = product_features_service.get_features_to_product_detail(pk)
        properties = (
            product_properties_service.get_properties_to_product_detail(pk)
        )
        tags = product_tags_service.get_tags_to_product_detail(pk)

        context = {
            "object": product,
            "images": images,
            "features": features,
            "properties": properties,
            "tags": tags,
        }
        return render(request, self.template_name, context)


# def product_properties(request, product_id):
#     product = get_object_or_404(Product, id=product_id)
#     properties = model_to_dict(product)  # Преобразуем объект в словарь
#     return render(request,
#                   'product_properties_template.html',
#                   {'product': product, 'properties': properties})
