from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView, View
from django.core.cache import cache
from django.db.models import Count

from dto.product_list_dto import ProductListDTO
from services.settings_service import SettingsService

from services.settings_service import SettingsService
from services.view_history_products_service import ViewHistoryProductsService
from .models.product import Product
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from .models.cart import CartItem, Cart
from .models.seller import Seller


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
    context_object_name = "products"
    sort_query_list = [
        "orders",
        "-orders",
        "price",
        "-price",
        "reviews",
        "-reviews",
        "created_at",
        "-created_at",
    ]

    def get_context_data(self, **kwargs):
        sort_query = self.request.GET.get("sort", "-orders")

        if sort_query not in self.sort_query_list:
            sort_query = "-orders"

        cache_key = f"products_list_sort_{sort_query}"
        cache_data = cache.get(cache_key)
        if cache_data:
            return {self.context_object_name: cache_data}

        products = (
            Product.objects.filter(is_active=True)
            .annotate(orders_count=Count("orders"))
            .annotate(reviews_count=Count("reviews"))
            .order_by(sort_query)
            .all()
        )
        products_dto = ProductListDTO.from_objects(products)
        cache.set(cache_key, products_dto, SettingsService.get_cache_timeout())

        return {self.context_object_name: products_dto}


class CartView(LoginRequiredMixin, View):
    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart)

        total_price = sum(
            item.get_final_price() * item.quantity
            for item in cart_items
        )

        context = {
            'cart_items': cart_items,
            'total_price': total_price
        }
        return render(request, 'cart.html', context)


class AddToCartView(LoginRequiredMixin, View):
    def post(self, request, product_id):
        product = Product.objects.get(id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)


        sellers = Seller.objects.filter(sellerproduct__product=product)
        selected_seller = random.choice(sellers) if sellers else None

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'selected_seller': selected_seller}
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        return redirect('cart')


class UpdateCartItemView(LoginRequiredMixin, View):
    def post(self, request, item_id):
        cart_item = CartItem.objects.get(id=item_id)
        action = request.POST.get('action')

        if action == 'update_quantity':
            quantity = int(request.POST.get('quantity', 1))
            cart_item.quantity = max(1, quantity)
        elif action == 'update_seller':
            seller_id = request.POST.get('seller_id')
            cart_item.selected_seller = Seller.objects.get(id=seller_id)
        elif action == 'delete':
            cart_item.delete()
            return redirect('cart')

        cart_item.save()
        return redirect('cart')