from django.contrib import admin
from .models import ComparisonItem

@admin.register(ComparisonItem)
class ComparisonItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'added_at')
    search_fields = ('user__username',)
