from django.contrib import admin
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Review model.
    Displays key fields and supports search and filtering.
    """
    list_display = ("id", "business_user", "reviewer", "rating", "updated_at")
    search_fields = ("business_user__username", "reviewer__username")
    list_filter = ("rating",)
