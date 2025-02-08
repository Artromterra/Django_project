from django.contrib import admin

from .models.product import Product, ProductImage
from .models.category import Category


admin.site.register(Product)

class ProductInline(admin.StackedInline):
    model = ProductImage

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "icon_preview")
    readonly_fields = ("icon_preview",)