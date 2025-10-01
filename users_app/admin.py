from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Admin configuration for the UserProfile model.
    Displays key fields and supports search and filtering.
    """
    list_display = ("id", "user", "type", "first_name", "last_name", "location")
    search_fields = ("user__username", "user__email", "first_name", "last_name")
    list_filter = ("type",)
