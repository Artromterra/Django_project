from django.contrib import admin, messages
from django.core.cache import cache
from .models.product import Product, ProductImage
from .models.category import Category
from .models.reviews import Review
from .models.product_properties import ProductProperties,Property, PropertyValue


@admin.action(description="Сбросить кеш меню категорий")
def clear_category_menu_cache(modeladmin, request, queryset):
    cache_key = 'category_menu'
    cache.delete(cache_key)
    modeladmin.message_user(request, "Кеш меню категорий сброшен.")


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [clear_category_menu_cache, "clear_cache"]
    inlines = [ReviewInline]

    @admin.action(description="Сбросить кеш каталога")
    def clear_cache(self, request, queryset):
        cache.delete("catalog_cache")
        self.message_user(
            request, "Кеш каталога успешно сброшен.", messages.SUCCESS
        )


class ProductInline(admin.StackedInline):
    model = ProductImage


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
