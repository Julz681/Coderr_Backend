from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """
    Admin configuration for Order model.
    Displays key fields, supports filtering and search.
    """
    list_display = ("id", "title", "customer_user", "business_user", "status", "updated_at")
    list_filter = ("status",)
    search_fields = ("title", "customer_user__username", "business_user__username")
