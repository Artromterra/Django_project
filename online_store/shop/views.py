import os
import random
from typing import List
from logging import getLogger

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls.base import reverse_lazy
from django.views.generic import DetailView, ListView, View
from django.core.cache import cache
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.sessions.models import Session
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator

from services.settings_service import SettingsService
from services.product_catalog_services import get_context_data_sort, get_context_data_filtered
from services.view_history_products_service import ViewHistoryProductsService
from profiles.models import Account, User
from .models.cart import CartItem, Cart
from .models.seller import Seller
from .models.order import Order, OrderDeliveryPrice
from .models.product import Product
import utils.files
import utils.celery_utils
from utils.calculating_price import calculate_price
from .forms import (
    ImportFilesForm,
    NewImportFileForm,
    OrderUserForm,
    OrderDeliveryForm,
    OrderPayForm,
)
from .tasks import import_data_from_files


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from shop.models.cart import Cart, CartItem
from services.cart_service import CartService

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.views.generic import TemplateView

logger = getLogger("main.shop.views")


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
    paginate_by = 10

    def get_context_data(self, **kwargs) -> dict:
        """
        Сортировка товара, для вывода на странице каталога товаров

        Порядок работы:
        1. Получаю метод сортировки из GET параметра.
        2. Если метод не передан, устанавливаю сортировку по популярности.
        3. Запрашиваю данные из кеша, если они есть, вывожу.
        4. Если кеша нет, запрашиваю товары с сортировкой в БД
        5. Перевожу товары в DTO формат.
        6. Кеширую данные.
        7. Пагинирую данные.
        8. Вывожу данные.
        """
        sorting_method = self.request.GET.get("sort", "-carts_count")
        sorted_context = get_context_data_sort(self.context_object_name, sorting_method)
        patinated_sorted_context = self._context_pagination(sorted_context)
        return patinated_sorted_context

    def post(self, request: HttpRequest) -> HttpResponse:
        """
        Обработка POST-запроса для фильтрации товаров на странице каталога.

        Порядок работы:
        1. Получаем текстовый фильтр из POST-запроса и применяем его к модели Product.
        2. Проверяем фильтр по цене и, если он присутствует, добавляем условия к запросу.
        3. Проверяем наличие чекбоксов для фильтрации по доступности и бесплатной доставке.
        4. Превращаем отфильтрованные объекты в ProductDTO.
        5. Формируем контекст для рендеринга страницы каталога товаров,
            включая параметры фильтрации.
        6. Пагинирует данные.
        7. Возвращаем отрендеренную страницу с продуктами.
        """
        filtered_context = get_context_data_filtered(self.context_object_name, request.POST)
        patinated_filtered_context = self._context_pagination(filtered_context)
        return render(request, "catalog.html", patinated_filtered_context)

    def _context_pagination(self, context: dict) -> dict:
        """Пагинирует контекст и возвращает его же"""
        page_number = self.request.GET.get("page")
        paginator = Paginator(context[self.context_object_name], self.paginate_by)
        page_obj = paginator.get_page(page_number)

        context[self.context_object_name] = page_obj
        context["paginator"] = paginator
        context["page_obj"] = page_obj
        return context


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


def load_new_import_file(request: HttpRequest) -> HttpResponse:
    """Process the download of a new import file."""
    form = NewImportFileForm(request.POST, request.FILES)
    if form.is_valid():
        logger.debug("Form with import files is valid.")
        logger.debug("Form data: %s", str(form.cleaned_data))
        import_file = form.cleaned_data["new_import_file"]
        filename: str = import_file.name
        logger.debug("Init filename: %s", filename)
        unique_filename: str = utils.files.generate_unique_filename(filename)
        logger.debug("Unique filename: %s", unique_filename)
        file_path = os.path.join(settings.DIR_WITH_IMPORT_FILES, unique_filename)
        logger.debug("Path loaded file: %s", file_path)

        with open (file_path, "wb+") as uploaded_import_file:
            for chunk in import_file.chunks():
                uploaded_import_file.write(chunk)

        return redirect("admin:importing")
    else:
        raise HttpResponseBadRequest


def import_from_files_page(request: HttpRequest) -> HttpResponse:
    """Return admin import page."""
    import_files: List[str] = utils.files.get_files_in_dir(settings.DIR_WITH_IMPORT_FILES)
    logger.debug(f"Import files: %s", str(import_files))
    new_import_file_form = NewImportFileForm()
    if request.method == "POST":
        form = ImportFilesForm(request.POST)
        form.fields["files"].choices = [(file, file) for file in import_files]

        if form.is_valid():
            logger.debug("Form with import files is valid.")
            selected_import_files = form.cleaned_data["files"]
            logger.error("Selected files: %s", str(selected_import_files))
            email = form.cleaned_data.get("email")

            action = request.POST.get("action")
            if action == "delete":
                filepaths = [
                    str(os.path.join(settings.DIR_WITH_IMPORT_FILES, filename))
                    for filename in selected_import_files
                ]
                utils.files.delete_files(filepaths)
            elif action == "import":
                utils.files.create_dir_if_not_exists(settings.DIR_WITH_SUCCESSFUL_IMPORTS)
                utils.files.create_dir_if_not_exists(settings.DIR_WITH_IMPORTS_WITH_ERRORS)

                import_data_from_files.apply_async(
                    kwargs={
                        "import_filenames": selected_import_files,
                        "emails": [email] if email else None
                    }
                )
            else:
                messages.error(request, "Unknown action")
            return redirect("admin:importing")
    else:
        if (utils.celery_utils.are_there_any_active_importing_tasks() or
                utils.celery_utils.are_there_any_reserved_importing_tasks()):
            return render(request, "admin/shop/import_running.html")
        form = ImportFilesForm()
        form.fields["files"].choices = [(file, file) for file in import_files]

    context = {
        "new_import_file_form": new_import_file_form,
        "form": form,
        "files": import_files,
    }
    return render(request, "admin/shop/import_page.html", context)


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
        # if request.session.get('pay_page'):
        #     return redirect('shop:order_confirm')
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        if self.obj:
            self.obj.payment_method = form.cleaned_data['payment_method']
            self.obj.save()
            self.session['order_id'] = self.obj.pk
        else:
            self.order_queryset.update(payment_method=form.cleaned_data['payment_method'])

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
        total = calculate_price(
            cart_queryset=cart,
            order=order,
            delivery_price=OrderDeliveryPrice(),
        )
        order.total_price = total
        order.save()
        context = {
            'cart': cart,
            'total': total,
            "user": user,
            "order": order,
        }
        return context


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'historyorder.html'
    context_object_name = 'orders'

    def get_queryset(self):
        queryset = (Order.objects.
        filter(cart__user_id=self.request.user.pk).
        order_by('-created_at')[:3])

        return queryset


class OrderDetailView(LoginRequiredMixin ,DetailView):
    model = Order
    context_object_name = 'order'
    template_name = 'oneorder.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        order = Order.objects.get(pk=self.kwargs.get('pk'))
        user = User.objects.get(pk=self.request.user.pk)
        cart = CartItem.objects.select_related(
            "product",
            "cart",
            "selected_seller"
        ).filter(cart_id=order.cart_id)
        context['cart'] = cart
        context['user'] = user
        return context


@method_decorator(csrf_exempt, name='dispatch')
class CartAddView(APIView):
    """Добавление товара в корзину"""

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        seller_id = request.data.get("seller_id")
        quantity = int(request.data.get("quantity", 1))

        cart_service = CartService(request)
        cart_service.add_product(product_id, seller_id, quantity)

        return Response(
            {"message": "Товар добавлен", "cart_count": cart_service.get_cart_count()},
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class CartRemoveView(APIView):
    """Удаление товара из корзины"""

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        seller_id = request.data.get("seller_id")

        cart_service = CartService(request)
        cart_service.remove_product(product_id, seller_id)

        return Response(
            {"message": "Товар удален", "cart_count": cart_service.get_cart_count()},
            status=status.HTTP_200_OK,
        )


@method_decorator(csrf_exempt, name='dispatch')
class CartUpdateView(APIView):
    """Изменение количества товара в корзине"""

    def post(self, request, *args, **kwargs):
        product_id = request.data.get("product_id")
        seller_id = request.data.get("seller_id")
        delta = int(request.data.get("delta", 0))

        cart_service = CartService(request)
        cart_service.update_product_quantity(product_id, seller_id, delta)

        return Response(
            {"message": "Количество обновлено", "cart_count": cart_service.get_cart_count()},
            status=status.HTTP_200_OK,
        )


# class CartView(APIView):
class CartView(TemplateView):
    template_name = "cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context["cart"] = cart
        return context
    # """Получение списка товаров в корзине"""
    #
    # def get(self, request, *args, **kwargs):
    #     cart_service = CartService(request)
    #     items = [
    #         {
    #             "product": item.product.name,
    #             "seller": item.selected_seller.name,
    #             "quantity": item.quantity,
    #             "price": item.get_final_price(),
    #         }
    #         for item in cart_service.get_cart_items()
    #     ]
    #     return Response(
    #         {"cart": items, "cart_count": cart_service.get_cart_count()},
    #         status=status.HTTP_200_OK,
    #     )