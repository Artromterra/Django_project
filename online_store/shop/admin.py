from django.contrib import admin
from django.core.cache import cache
from .models.product import Product, ProductImage
from .models.category import Category
from .models.product_properties import ProductProperties, ProductPropertiesValues


@admin.action(description="Сбросить кеш меню категорий")
def clear_category_menu_cache(modeladmin, request, queryset):
    cache_key = 'category_menu'
    cache.delete(cache_key)
    modeladmin.message_user(request, "Кеш меню категорий сброшен.")

admin.site.register(Product)
class ProductAdmin(admin.ModelAdmin):
    actions = [clear_category_menu_cache]

class ProductInline(admin.StackedInline):
    model = ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_preview")
    readonly_fields = ("icon_preview",)
    actions = [clear_category_menu_cache]


class ProductPropertiesValuesAdmin(admin.StackedInline):
    model = ProductPropertiesValues


class ProductPropertiesValuesInline(admin.TabularInline):
    model = ProductProperties.values.through
    extra = 1

@admin.register(ProductProperties)
class ProductPropertiesAdmin(admin.ModelAdmin):
    list_display = ("title", )
    actions = [clear_category_menu_cache]
    inlines = [ProductPropertiesValuesInline]

@admin.register(ProductPropertiesValues)
class ProductPropertiesValuesAdmin(admin.ModelAdmin):
    list_display = ("value",)