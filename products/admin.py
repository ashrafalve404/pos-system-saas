from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'created_at']
    list_filter = ['organization']
    search_fields = ['name']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'stock_quantity', 'is_active']
    list_filter = ['organization', 'category', 'is_active']
    search_fields = ['name', 'barcode', 'sku']
    raw_id_fields = ['organization', 'category', 'store']
    list_editable = ['price', 'is_active']
