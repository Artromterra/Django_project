from django.contrib import admin
from .models import Product, Banner


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("product", "banner_type", "is_active")
