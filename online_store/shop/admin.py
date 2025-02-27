from django.contrib import admin
from django.core.cache import cache
from .models.product import Product, ProductImage, ProductSeller
from .models.category import Category
from .models.reviews import Review
from .models.product_properties import ProductProperties,Property, PropertyValue
from .models.seller import Seller


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
    actions = [clear_category_menu_cache]
    inlines = [ReviewInline, ProductSellerInline, ImageInline]

    list_display = ('title', 'price', 'is_active')
    list_filter = ('sellers', 'is_active')
    search_fields = ('title', 'sellers__name')

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


@admin.register(ProductProperties)
class ProductPropertiesAdmin(admin.ModelAdmin):
    list_display = ("id", "property", "value", "get_products")
    search_fields = ("property__name", "value__value")

    def get_products(self, obj):
        return ", ".join([p.name for p in obj.product.all()])
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
