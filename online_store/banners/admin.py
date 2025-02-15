from django.contrib import admin
from banners.models.banner_product import BannerProduct
from banners.models.banner_category import BannerCategory


@admin.register(BannerProduct)
class BannerProductAdmin(admin.ModelAdmin):
    list_display = ("product", "is_active")


@admin.register(BannerCategory)
class BannerCategoryAdmin(admin.ModelAdmin):
    list_display = ("category", "is_active")
