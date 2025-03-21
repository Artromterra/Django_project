import os
from typing import List
from logging import getLogger

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect
from django.views.generic import DetailView, ListView, View
from django.core.cache import cache
from django.db.models import Count
from django.conf import settings
from django.contrib import messages

from dto.product_list_dto import ProductListDTO
from services.settings_service import SettingsService

from services.settings_service import SettingsService
from services.view_history_products_service import ViewHistoryProductsService
from .models.product import Product
from django.contrib.auth.mixins import LoginRequiredMixin
import random
from .models.cart import CartItem, Cart
from .models.seller import Seller
import utils.files
import utils.celery_utils
from .forms import ImportFilesForm, NewImportFileForm
from .tasks import import_data_from_files

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
