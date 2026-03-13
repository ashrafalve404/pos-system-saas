from django.contrib import admin
from .models import Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'subscription_plan', 'is_active', 'created_at']
    list_filter = ['subscription_plan', 'is_active']
    search_fields = ['name', 'owner__email']
    raw_id_fields = ['owner']
