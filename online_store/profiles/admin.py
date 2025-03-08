from django.contrib import admin

from .models import User, Account
from viewed_products.models import ViewedProducts


class ViewedProductsAdmin(admin.TabularInline):
    model = ViewedProducts
    # list_display = ('product', 'viewed_at')
    readonly_fields = ('viewed_at', 'product')
    ordering = ('-viewed_at',)
    extra = 0

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User

    list_display = (
        'id',
        'username',
        'email',
        'is_superuser',
        'is_active',
        'image_preview',
        'phone'
    )
    list_editable = (
        'phone',
    )

    list_display_links = 'id', 'username'
    readonly_fields = 'image_preview',
    search_fields = 'username', 'email'
    ordering = 'id',

    inlines = (ViewedProductsAdmin,)

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    model = Account, User

    list_display = (
        'user',
        'first_name',
        'last_name',
        'patronymic',
    )
    list_editable = (
        'first_name',
        'last_name',
        'patronymic',
    )
