from django.contrib import admin
from .models import Store


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'manager', 'phone', 'is_active']
    list_filter = ['organization', 'is_active']
    search_fields = ['name', 'phone']
    raw_id_fields = ['organization', 'manager']
