from django.contrib import admin
from django.core.cache import cache
from .models.product import Product, ProductImage
from .models.category import Category


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