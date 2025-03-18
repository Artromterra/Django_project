from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.urls.base import reverse_lazy
from django.views.generic import DetailView, ListView
from django.core.cache import cache
from django.db.models import Count
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, FormMixin, CreateView

from dto.product_list_dto import ProductListDTO
from services.settings_service import SettingsService

from services.settings_service import SettingsService
from services.view_history_products_service import ViewHistoryProductsService
from .models.cart import Cart
from .models.order import Order
from .models.product import Product
from .forms import OrderUserForm, OrderDeliveryForm, OrderPayForm
from profiles.models import Account, User


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


class OrderUserView(FormView, FormMixin):
    template_name = "order_user.html"
    form_class = OrderUserForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pk = None

    def get_initial(self):
        """
        метод добавления данных зарегистрированного пользователя в форму при инициализации
        :return: dict словарь данных пользователя
        """
        user = self.request.user
        if user.is_authenticated:
            account = Account.objects.get(user=user.pk)
            fio = account.last_name + ' ' + account.first_name + ' ' + account.patronymic
            initial = {
                'username': fio,
                'email': user.email,
                'phone': user.phone,
            }
            return initial

    def get_context_data(self, **kwargs):
        """
        Переопределен контекст для добавления id order и cart в шаблон выбора
        прогресса заполнения для его корректной работы
        :param kwargs:
        :return: dict
        """
        context = super().get_context_data(**kwargs)
        pk = self.kwargs.get("pk")
        order_id = Order.objects.get(cart=pk).pk
        context["order_id"] = order_id
        context["cart_id"] = pk
        return context

    def form_valid(self, form):
        user = self.request.user
        if not user.is_authenticated:
            user = form.save(commit=False)
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password_confirm = form.cleaned_data['password_confirm']
            form.clean()
            phone = form.cleaned_data['phone']
            user.set_password(password_confirm)
            user.is_active = True
            user.username = username
            user.email = email
            user.phone = phone
            user.save()
            self.pk = user.pk
            account = Account.objects.create(user=user)
            account.save()
        return super(OrderUserView, self).form_valid(form)

    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        cart_obj = Cart.objects.get(pk=pk)
        cart_obj.user_id = self.pk
        cart_obj.save()
        obj, created = Order.objects.get_or_create(cart=cart_obj)
        return super(OrderUserView, self).post(request, *args, **kwargs)

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy("profiles:login")

class OrderDeliveryView(UpdateView):
    model = Order
    template_name = 'order_delivery_page.html'
    form_class = OrderDeliveryForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_pk = self.kwargs.get("pk")
        cart_id = Order.objects.get(pk=order_pk).cart_id
        context["cart_id"] = cart_id
        context["order_id"] = order_pk
        return context

    def form_valid(self, form):
        form.instance.delivery = form.cleaned_data['delivery']
        form.instance.city = form.cleaned_data['city']
        form.instance.address = form.cleaned_data['address']
        form.instance.save()
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        order_pk = self.kwargs.get("pk")
        return reverse_lazy('shop:order_pay', kwargs={'pk': order_pk})


class OrderPayView(UpdateView):
    model = Order
    template_name = 'order_pay.html'
    form_class = OrderPayForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_pk = self.kwargs.get("pk")
        cart_id = Order.objects.get(pk=order_pk).cart_id
        context["cart_id"] = cart_id
        context["order_id"] = order_pk
        return context

    def form_valid(self, form):
        form.instance.payment_method = form.cleaned_data['payment_method']
        form.instance.save()
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        order_pk = self.kwargs.get("pk")
        return reverse_lazy('shop:order_confirm', kwargs={'pk': order_pk})


class OrderConfirmView(TemplateView):
    template_name = 'order_confirm.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_pk = self.kwargs.get("pk")
        cart_id = Order.objects.get(pk=order_pk).cart_id
        context["cart_id"] = cart_id
        context["order_id"] = order_pk
        return context

