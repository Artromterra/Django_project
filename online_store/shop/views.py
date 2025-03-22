from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.core.cache import cache
from django.db.models import Count

from dto.product_list_dto import ProductListDTO
from services.settings_service import SettingsService
from services.product_catalog_services import get_context_data_sort, get_context_data_filtered

from services.view_history_products_service import ViewHistoryProductsService
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
            .prefetch_related(
                "images",
                "features",
                "tags",
                "product_properties",
                "product_sellers",
            )
        )

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        obj = super().get(request, *args, **kwargs)
        # класс для обработки и действий над просмотренными продуктами
        user = self.request.user
        if user.is_authenticated:
            viewed_products = ViewHistoryProductsService(
                user=user,
                product=self.object,
            )
            viewed_products.add_viewed_products()
        return obj

    def get_object(self, *args, **kwargs):
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
    context_object_name: str = "products"

    def get_context_data(self, **kwargs) -> dict:
        sort_query = self.request.GET.get("sort", "-carts_count")
        return get_context_data_sort(self.context_object_name, sort_query)

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обработка POST-запроса для фильтрации товаров на странице каталога.

        Порядок работы:
        1. Получаем текстовый фильтр из POST-запроса и применяем его к модели Product.
        2. Проверяем фильтр по цене и, если он присутствует, добавляем условия к запросу.
        3. Проверяем наличие чекбоксов для фильтрации по доступности и бесплатной доставке.
        4. Превращаем отфильтрованные объекты в ProductListDTO.
        5. Формируем контекст для рендеринга страницы каталога товаров,
            включая параметры фильтрации.
        6. Возвращаем отрендеренную страницу с отфильтрованными продуктами.
        """
        context = get_context_data_filtered(self.context_object_name, request.POST)
        return render(request, "catalog.html", context)
