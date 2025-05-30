'''Модуль для подготовки контента для глановй страницы'''

from django.db.models import F, Case, When, DecimalField, ExpressionWrapper, Value, Min, Sum, Count
from django.utils.timezone import now
from django.core.cache import cache

from dto.product_list_dto import ProductDTO
from shop.models import Product


class HomepageContentService:

    def get_contex_products(self) -> dict['str', list[ProductDTO] | ProductDTO | None]:
        '''Возвращает продукты для отображения главной страницы'''

        cache_key = 'homepage_context_products'
        if cache_products := cache.get(cache_key):
            return cache_products

        products = self._get_products()
        cache.set(key=cache_key, value=products)
        return products

    def _get_products(self) -> dict['str', list[ProductDTO] | ProductDTO | None]:
        '''Формирует словарь с продуктами'''
        return {
            'popular_products': self._get_popular_products(),
            'limited_products': self._get_limited_products(),
            'discount_product': self._get_discount_produtcs(),
        }

    def _get_popular_products(self) -> list[ProductDTO]:
        '''Возвращает 6 популярных продуктов'''
        return ProductDTO.from_objects(
            Product.objects.filter(is_active=True)
            .annotate(carts_count=Count("cart_product_items"))
            .order_by('-carts_count')[:6]
        )

    def _get_limited_products(self) -> list[ProductDTO]:
        '''Возвращает 12 продуктов ограниченного тиража'''
        return ProductDTO.from_objects(
            Product.objects.filter(is_active=True)
            .annotate(total_amount=Sum('product_sellers__amount'))
            .order_by('total_amount')[:12]
        )

    def _get_discount_produtcs(self) -> ProductDTO | None:
        '''Возвращает 1 продукт с истекающей скидкой'''
        discount_product = (
            Product.objects.filter(is_active=True, discounts__is_active=True)
            .filter(discounts__end_date__gt=now())
            .annotate(
                nearest_end=Min('discounts__end_date'),
                discount_value=F('discounts__value'),
                discount_type=F('discounts__discount_type'),
                discount_price=Case(
                    When(
                        discounts__discount_type='percentage',
                        then=ExpressionWrapper(
                            F('price') - (F('price') * F('discounts__value') / Value(100)),
                            output_field=DecimalField(max_digits=10, decimal_places=2),
                        ),
                    ),
                    When(
                        discounts__discount_type='fixed',
                        then=ExpressionWrapper(
                            F('price') - F('discounts__value'),
                            output_field=DecimalField(max_digits=10, decimal_places=2),
                        ),
                    ),
                    default=F('price'),
                    output_field=DecimalField(max_digits=10, decimal_places=2),
                ),
            )
            .order_by('nearest_end')[:1]
        )
        pr = discount_product.first()
        dt = ProductDTO.from_object_for_discount_card(discount_product[0])
        return (
            ProductDTO.from_object_for_discount_card(discount_product[0])
            if discount_product
            else None
        )
