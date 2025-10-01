from django.contrib import admin
from .models import Offer, OfferDetail


class OfferDetailInline(admin.TabularInline):
    """
    Inline admin for OfferDetail within the Offer admin.
    """
    model = OfferDetail
    extra = 0


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    """
    Admin configuration for Offer model.
    Displays key fields and allows search/filter.
    """
    list_display = ("id", "title", "user", "updated_at")
    list_filter = ("user",)
    search_fields = ("title", "description", "user__username")
    inlines = [OfferDetailInline]


@admin.register(OfferDetail)
class OfferDetailAdmin(admin.ModelAdmin):
    """
    Admin configuration for OfferDetail model.
    Displays important fields and supports filtering by offer type.
    """
    list_display = ("id", "offer", "offer_type", "price", "delivery_time_in_days")
    list_filter = ("offer_type",)
