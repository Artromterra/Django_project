from django.contrib import admin
from .models import BannerProduct, BannerCategory


@admin.register(BannerProduct)
class BannerProductAdmin(admin.ModelAdmin):
    list_display = ("product", "is_active")


@admin.register(BannerCategory)
class BannerCategoryAdmin(admin.ModelAdmin):
    list_display = ("category", "is_active")
