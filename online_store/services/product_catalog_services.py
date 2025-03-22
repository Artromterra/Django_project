'''Логика сортировки, фильтрации дял каталога товаров'''

from django.core.cache import cache
from django.db.models import Count
from django.http import QueryDict

from shop.models.product import Product
from dto.product_list_dto import ProductListDTO
from services.settings_service import SettingsService

SORT_QUERY_LIST = [
    "carts_count",
    "-carts_count",
    "price",
    "-price",
    "reviews_count",
    "-reviews_count",
    "created_at",
    "-created_at",
]


def get_context_data_sort(
    context_object_name: str, sort_query: str
) -> dict[str, list[ProductListDTO]]:
    '''Загружает контекстные данные и сортирует их по переданному методу соритровки'''

    if sort_query not in SORT_QUERY_LIST:
        sort_query = "-carts_count"

    cache_key = f"products_list_sort_{sort_query}"
    cache_data = cache.get(cache_key)
    if cache_data:
        return {context_object_name: cache_data}

    products = (
        Product.objects.filter(is_active=True)
        .annotate(carts_count=Count("cart_product_items"))
        .annotate(reviews_count=Count("reviews"))
        .order_by(sort_query)
        .all()
    )
    products_dto = ProductListDTO.from_objects(products)  # type: ignore
    cache.set(cache_key, products_dto, SettingsService.get_cache_timeout())

    return {context_object_name: products_dto}


def get_context_data_filtered(context_object_name: str, request_post_data: QueryDict) -> dict:
    '''Загружает контекстные данные и фильтрует их по переданным фильтрам'''
    text_filter = request_post_data.get("title")
    query = Product.objects.filter(title__icontains=text_filter)

    price_filter = request_post_data.get("price")
    if price_filter:
        min_price, max_price = map(float, price_filter.split(";"))
        query = query.filter(price__range=(min_price, max_price))
    else:
        min_price, max_price = 0, None

    available_only_filter = request_post_data.get("available_only") == "on"
    if available_only_filter:
        query = query.filter(is_active=True)

    free_shipping_filter = request_post_data.get("free_shipping") == "on"
    if free_shipping_filter:
        query = query.filter(product_sellers__free_shipping=True)

    products_dto = ProductListDTO.from_objects(query)
    context = {
        "min_price": min_price,
        "max_price": max_price,
        "text_filter": text_filter,
        "available_only": available_only_filter,
        "free_shipping": free_shipping_filter,
        context_object_name: products_dto,
    }
    return context
