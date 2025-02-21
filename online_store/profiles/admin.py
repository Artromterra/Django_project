from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User

    list_display = (
        'id',
        'username',
        'email',
        'is_superuser',
        'is_active',
        'image_preview'
    )
    list_display_links = 'id', 'username'
    readonly_fields = 'image_preview',
    search_fields = 'username', 'email'
    ordering = 'id',
