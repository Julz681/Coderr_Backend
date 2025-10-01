from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, permissions, filters
from rest_framework.pagination import PageNumberPagination

from offers_app.models import Offer, OfferDetail
from .serializers import (
    OfferListSerializer,
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
)
from .permissions import IsBusiness, IsOfferOwner
from .filters import OfferFilter


class OfferPagination(PageNumberPagination):
    """
    Custom pagination settings for offers.
    """
    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100


class OfferViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Offer model.
    Provides CRUD operations, filtering, search, ordering, and pagination.
    """
    queryset = (
        Offer.objects.all()
        .select_related("user")
        .prefetch_related("details")
    )
    filterset_class = OfferFilter
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]
    pagination_class = OfferPagination

    def get_permissions(self):
        if self.action == "list":
            return [permissions.AllowAny()]
        if self.action == "retrieve":
            return [permissions.IsAuthenticated()]
        if self.action == "create":
            return [permissions.IsAuthenticated(), IsBusiness()]
        if self.action in ["partial_update", "update", "destroy"]:
            return [permissions.IsAuthenticated(), IsOfferOwner()]
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return OfferListSerializer
        return OfferCreateUpdateSerializer

    def get_queryset(self):
        qs = super().get_queryset()

        creator_id = self.request.query_params.get("creator_id")
        if creator_id:
            qs = qs.filter(user_id=creator_id)

        min_price = self.request.query_params.get("min_price")
        if min_price is not None:
            try:
                val = float(min_price)
                qs = qs.annotate(min_price=Min("details__price")).filter(min_price__gte=val)
            except (TypeError, ValueError):
                pass

        max_delivery_time = self.request.query_params.get("max_delivery_time")
        if max_delivery_time is not None:
            try:
                days = int(max_delivery_time)
                qs = qs.annotate(min_delivery_time=Min("details__delivery_time_in_days")).filter(
                    min_delivery_time__lte=days
                )
            except (TypeError, ValueError):
                pass

        ordering = self.request.query_params.get("ordering")
        if ordering and "min_price" in ordering:
            qs = qs.annotate(min_price=Min("details__price")).order_by(ordering)

        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    RetrieveAPIView for a single OfferDetail.
    Requires authentication.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
