import django_filters
from django.db.models import Min
from offers_app.models import Offer


class OfferFilter(django_filters.FilterSet):
    """
    FilterSet for Offer model.
    Allows filtering by creator ID, minimum price, and maximum delivery time.
    """
    creator_id = django_filters.NumberFilter(field_name="user__id", lookup_expr="exact")
    min_price = django_filters.NumberFilter(method="filter_min_price")
    max_delivery_time = django_filters.NumberFilter(method="filter_max_delivery")

    class Meta:
        model = Offer
        fields = ["creator_id"]

    def filter_min_price(self, queryset, name, value):
        qs = queryset.annotate(min_price_agg=Min("details__price"))
        return qs.filter(min_price_agg__gte=value)

    def filter_max_delivery(self, queryset, name, value):
        qs = queryset.annotate(min_delivery_agg=Min("details__delivery_time_in_days"))
        return qs.filter(min_delivery_agg__lte=value)
