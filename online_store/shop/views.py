from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.generic import DetailView, ListView
from django.core.cache import cache
from django.db.models import Count

from dto.product_list_dto import ProductListDTO
from services.settings_service import SettingsService

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
    sort_query_list = [
        "carts_count",
        "-carts_count",
        "price",
        "-price",
        "reviews_count",
        "-reviews_count",
        "created_at",
        "-created_at",
    ]

    def get_context_data(self, **kwargs):
        sort_query = self.request.GET.get("sort", "-carts_count")

        if sort_query not in self.sort_query_list:
            sort_query = "-carts_count"

        cache_key = f"products_list_sort_{sort_query}"
        cache_data = cache.get(cache_key)
        if cache_data:
            return {self.context_object_name: cache_data}

        products = (
            Product.objects.filter(is_active=True)
            .annotate(carts_count=Count("cart_product_items"))
            .annotate(reviews_count=Count("reviews"))
            .order_by(sort_query)
            .all()
        )
        products_dto = ProductListDTO.from_objects(products)  # type: ignore
        cache.set(cache_key, products_dto, SettingsService.get_cache_timeout())

        return {self.context_object_name: products_dto}

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
        text_filter = request.POST.get("title")
        query = Product.objects.filter(title__icontains=text_filter)

        price_filter = request.POST.get("price")
        if price_filter:
            min_price, max_price = map(float, price_filter.split(";"))
            query = query.filter(price__range=(min_price, max_price))
        else:
            min_price, max_price = 0, None

        available_only_filter = request.POST.get("available_only") == "on"
        if available_only_filter:
            query = query.filter(is_active=True)

        free_shipping_filter = request.POST.get("free_shipping") == "on"
        if free_shipping_filter:
            query = query.filter(product_sellers__free_shipping=True)

        products_dto = ProductListDTO.from_objects(query)
        context = {
            "min_price": min_price,
            "max_price": max_price,
            "text_filter": text_filter,
            "available_only": available_only_filter,
            "free_shipping": free_shipping_filter,
            self.context_object_name: products_dto,
        }
        return render(request, "catalog.html", context)
