from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls.base import reverse_lazy
from django.views.generic import DetailView, ListView
from django.core.cache import cache
from django.db.models import Count
from django.views.generic.edit import FormView, FormMixin

from dto.product_list_dto import ProductListDTO
from services.settings_service import SettingsService

from services.settings_service import SettingsService
from services.view_history_products_service import ViewHistoryProductsService
from .models.product import Product
from .forms import OrderUserForm


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


class OrderUserFormView(FormView, FormMixin):
    template_name = "order.html"
    form_class = OrderUserForm
    success_url = reverse_lazy("profiles:login")

    def get_initial(self):
        """
        метод добавления данных зарегистрированного пользователя в форму при инициализации
        :return: dict словарь данных пользователя
        """
        user = self.request.user
        if user.is_authenticated:
            initial = {
                'username': user.username,
                'email': user.email,
                'phone': user.phone,
            }
            return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        email = form.cleaned_data['email']
        phone = form.cleaned_data['phone']
        password_confirm = form.cleaned_data['password_confirm']
        form.clean()
        user.set_password(password_confirm)
        user.is_active = True
        user.username = username
        user.email = email
        user.phone = phone
        user.save()

        return response
