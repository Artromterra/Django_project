
from typing import Dict, Type
from logging import getLogger

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.core.cache import cache
from django.urls import path
from constance.admin import Config, ConstanceAdmin

from .models.order import Order, OrderDeliveryPrice
from .models.product import Product, ProductImage, ProductSeller
from .models.category import Category
from .models.reviews import Review
from .models.product_properties import ProductProperties,Property, PropertyValue
from .models.seller import Seller
from .models.cart import Cart,CartItem
from .models.discount import Discount
from .views import load_new_import_file, import_from_files_page

from services.cache.cleaners import BaseCleaner, AllCleaner, BannerCleaner, ShopCleaner

logger = getLogger("main.shop.admin")


@admin.action(description="Сбросить кеш меню категорий")
def clear_category_menu_cache(modeladmin, request, queryset):
    cache_key = 'category_menu'
    cache.delete(cache_key)
    modeladmin.message_user(request, "Кеш меню категорий сброшен.")


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1

class ProductSellerInline(admin.TabularInline):
    model = ProductSeller
    extra = 1

class ImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [clear_category_menu_cache, "clear_cache"]
    inlines = [ReviewInline, ProductSellerInline, ImageInline]

    list_display = ('title', 'price', 'is_active')
    list_filter = ('sellers', 'is_active')
    search_fields = ('title', 'sellers__name')
    
    @admin.action(description="Сбросить кеш каталога")
    def clear_cache(self, request, queryset):
        cache.delete("catalog_cache")
        self.message_user(
            request, "Кеш каталога успешно сброшен.", messages.SUCCESS
        )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(sellers__user=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "sellers" and not request.user.is_superuser:
            kwargs["queryset"] = Seller.objects.filter(user=request.user)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_preview")
    readonly_fields = ("icon_preview",)
    actions = [clear_category_menu_cache]


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'discount_type', 'value', 'start_date', 'end_date', 'priority', 'is_active')
    list_filter = ('discount_type', 'is_active', 'start_date', 'end_date')
    search_fields = ('name',)
    filter_horizontal = ('products', 'categories')


@admin.register(ProductProperties)
class ProductPropertiesAdmin(admin.ModelAdmin):
    list_display = ("get_products", "property", "value", "title")
    search_fields = ("property__name", "value__value")
    list_display_links = ("get_products",)

    def get_products(self, obj):
        return ", ".join([p.title for p in obj.product.all()])
    get_products.short_description = "Products"


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(PropertyValue)
class PropertyValueAdmin(admin.ModelAdmin):
    list_display = ("id", "value")
    search_fields = ("value",)


class SellerProductInline(admin.TabularInline):
    model = Product.sellers.through
    extra = 1


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email')
    search_fields = ('name', 'email')
    inlines = [SellerProductInline]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    inlines = [CartItemInline]

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product', 'selected_seller', 'quantity', 'get_final_price')
    list_filter = ('selected_seller',)
    search_fields = ('product__title', 'cart__user__username')

@admin.register(OrderDeliveryPrice)
class OrderDeliveryPriceAdmin(admin.ModelAdmin):
    list_display = ('express_price', 'regular_price', 'order_price_for_delivery')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('cart', 'product_in_cart', 'paid', 'created_at')
    search_fields = ('cart__user__username',)

    def product_in_cart(self, obj):
        products = obj.cart.cart_items.all()
        prod_list = [product.product.title for product in products]
        return prod_list


original_get_urls = admin.site.get_urls

def custom_get_urls():
    custom_urls = [
        path("shop/importing/", admin.site.admin_view(import_from_files_page), name="importing"),
        path("shop/importing/new_import_file", admin.site.admin_view(load_new_import_file), name="new_import_file"),
    ]
    return custom_urls + original_get_urls()


admin_site = admin.site
admin_site.get_urls = custom_get_urls


class CustomConstanceAdmin(ConstanceAdmin):
    change_list_template = "admin/constance_config/change_list.html"
    cache_cleaners: Dict[str, Type[BaseCleaner]] = {
        "all": AllCleaner,
        "shop": ShopCleaner,
        "banners": BannerCleaner,
    }

    def changelist_view(self, request, extra_context=None):
        """Clear the cache depending on the application selection."""
        extra_context = extra_context or {}
        extra_context['cache_apps'] = list(self.cache_cleaners.keys())

        if request.method == 'POST':
            cache_reset: bool = False
            for app_name in self.cache_cleaners.keys():
                button_name: str = f"reset_{app_name}_cache"
                if button_name in request.POST:
                    logger.debug("Reset cache for app %s", app_name)
                    self.cache_cleaners[app_name]().clean()
                    cache_reset = True

            if cache_reset:
                return HttpResponseRedirect(request.get_full_path())

        response = super().changelist_view(request, extra_context)
        response.context_data["cache_apps"] = list(self.cache_cleaners.keys())
        return response


admin.site.unregister([Config])
admin.site.register([Config], CustomConstanceAdmin)
