from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.urls.base import reverse_lazy
from django.views.generic import DetailView, ListView
from django.core.cache import cache
from django.db.models import Count
from django.views.generic import UpdateView
from django.views.generic.base import TemplateView, View
from django.views.generic.edit import FormView, FormMixin, CreateView
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.shortcuts import get_object_or_404

from dto.product_list_dto import ProductListDTO
from services.settings_service import SettingsService

from services.view_history_products_service import ViewHistoryProductsService
from .models.cart import Cart, CartItem
from .models.order import Order
from .models.product import Product, ProductSeller
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


class OrderUserView(FormView):
    template_name = "order_user.html"
    form_class = OrderUserForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pk = None
        self.session = None

    def get_initial(self):
        """
        метод добавления данных зарегистрированного пользователя в форму при инициализации
        :return: dict словарь данных пользователя
        """
        user = self.request.user
        pk = self.kwargs.get("pk")
        cart_queryset = Cart.objects.filter(pk=pk)
        if not cart_queryset.exists():
            return redirect('/')
        if user.is_authenticated:
            self.session['user_page'] = True
            account = Account.objects.get(user=user.pk)
            fio = account.last_name + ' ' + account.first_name + ' ' + account.patronymic
            initial = {
                'username': fio,
                'email': user.email,
                'phone': user.phone,
            }
            return initial

    def get(self, request, *args, **kwargs) -> HttpResponse:
        self.session = request.session
        self.session['delivery_page'] = False
        self.session['pay_page'] = False
        self.session['cart_id'] = self.kwargs.get('pk')
        session_key = request.session.session_key
        cart = Cart.objects.filter(pk=self.kwargs.get("pk"))
        if not cart.exists():
            return redirect('/')
        else:
            cart[0].session_key = session_key
            cart[0].save()
        return super().get(request, *args, **kwargs)


    def form_valid(self, form):
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
        self.session['user_page'] = True
        return super(OrderUserView, self).form_valid(form)

    def get_success_url(self, *args, **kwargs):
        pk = self.kwargs.get('pk')
        cart_obj = Cart.objects.get(pk=pk)
        cart_obj.user_id = self.pk
        cart_obj.save()
        self.session['user_page'] = True
        return reverse_lazy("profiles:login")

class OrderDeliveryView(FormView):
    template_name = 'order_delivery_page.html'
    form_class = OrderDeliveryForm
    # success_url = 'shop:order_pay'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = None
        self.cart_id = None

    def get(self, request, *args, **kwargs):
        self.cart_id = request.session.get('cart_id')
        if not request.session.has_key('delivery_page'):
            # исправить на путь к корзине
            return redirect('/')
        if request.session.get('delivery_page') and not request.session.get('pay_page'):
            return redirect(reverse_lazy('shop:order_pay'))
        elif request.session.get('pay_page') and request.session.get('delivery_page'):
            return redirect(reverse_lazy('shop:order_confirm'))
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        self.session['delivery'] = form.cleaned_data['delivery']
        self.session['city'] = form.cleaned_data['city']
        self.session['address'] = form.cleaned_data['address']
        self.session['delivery_page'] = True
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.session = request.session
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('shop:order_pay')



class OrderPayView(FormView):
    template_name = 'order_pay.html'
    form_class = OrderPayForm

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = None
        self.obj = None
        self.order_queryset = None

    def get(self, request, *args, **kwargs):
        if not request.session.has_key('delivery_page'):
            # исправить на путь к корзине по желанию
            return redirect('/')
        if not request.session.get('delivery_page'):
            return redirect('shop:order_delivery')
        if request.session.get('pay_page'):
            return redirect('shop:order_confirm')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if self.obj:
            self.obj.payment_method = form.cleaned_data['payment_method']
            self.obj.save()
            self.session['order_id'] = self.obj.pk
        else:
            self.order_queryset.update(payment_method=form.cleaned_data['payment_method'])
            data = self.order_queryset.values_list()

            self.session['order_id'] = self.order_queryset[0].pk
        self.session['pay_page'] = True

        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        self.session = request.session
        sk = self.session.session_key
        session = Session.objects.get(session_key=sk)
        data = session.get_decoded()
        self.order_queryset = Order.objects.filter(cart_id=self.session.get('cart_id'))
        if self.order_queryset.exists():
            self.order_queryset.update(
                city=self.session.get('city'),
                address=self.session.get('address'),
                delivery=self.session.get('delivery'),
            )
        else:
            self.obj, created = Order.objects.get_or_create(
                city=data['city'],
                address=data['address'],
                delivery=data['delivery'],
                cart_id=data['cart_id'],
            )
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('shop:order_confirm')


class OrderConfirmView(TemplateView):
    template_name = 'order_confirm.html'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = None

    def get(self, request, *args, **kwargs):
        """
        проверка пользователя на наличие ранее пройденных шагов при оформлении заказа
        """
        self.session = request.session
        s = Session.objects.get(session_key=self.session.session_key)
        data = s.get_decoded()
        if (request.session.has_key('delivery_page')
            and request.session.has_key('pay_page')
            and request.session.has_key('user_page')
        ):
            # исправить на путь к корзине по желанию
            return super().get(request, *args, **kwargs)
        return redirect('/')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order_pk = self.session.get('order_id')
        order= Order.objects.get(pk=order_pk)
        user = User.objects.get(pk=self.request.user.pk)
        cart = CartItem.objects.select_related(
            "product",
            "cart",
            "selected_seller"
        ).filter(cart_id=order.cart.pk)

        total = sum(item.get_final_price() * item.quantity for item in cart)

        context = {
            'cart': cart,
            'total': total,
            "user": user,
            "order": order,
        }
        return context
