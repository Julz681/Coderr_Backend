from django.db.models import Min
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, permissions, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from offers_app.models import Offer, OfferDetail
from .serializers import (
    OfferListSerializer,
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
    OfferRetrieveSerializer,
    OfferReadSerializer,
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
        if self.action == "list":
            return OfferListSerializer
        if self.action == "retrieve":
            # Matches GET /api/offers/{id}/ response shape from docs
            return OfferRetrieveSerializer
        # For input parsing on POST/PATCH/PUT
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

    # --- Custom responses to exactly match API doc payloads ---

    def create(self, request, *args, **kwargs):
        """
        Returns newly created offer with FULL details (ids + fields),
        as shown in the documentation for POST /api/offers/.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save(user=request.user)
        read = OfferReadSerializer(offer, context=self.get_serializer_context())
        return Response(read.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Returns the updated offer with FULL details,
        matching the PATCH response in the documentation.
        """
        kwargs["partial"] = True  # Allow partial updates (PATCH semantics)
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        offer = self.get_object()
        serializer = self.get_serializer(offer, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        offer = serializer.save()
        read = OfferReadSerializer(offer, context=self.get_serializer_context())
        return Response(read.data, status=status.HTTP_200_OK)


class OfferDetailRetrieveView(generics.RetrieveAPIView):
    """
    RetrieveAPIView for a single OfferDetail.
    Requires authentication.
    """
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "pk"
