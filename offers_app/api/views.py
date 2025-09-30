from django.db.models import Min
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from offers_app.models import Offer, OfferDetail
from .serializers import (
    OfferListSerializer,
    OfferCreateUpdateSerializer,
    OfferDetailSerializer,
)
from .permissions import IsBusiness, IsOfferOwner
from .filters import OfferFilter
from rest_framework import generics

class OfferViewSet(viewsets.ModelViewSet):
    queryset = Offer.objects.all().prefetch_related("details", "user__profile")
    filterset_class = OfferFilter
    search_fields = ["title", "description"]
    ordering_fields = ["updated_at", "min_price"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        if self.action in ["create"]:
            return [IsAuthenticated(), IsBusiness()]
        if self.action in ["partial_update", "update", "destroy"]:
            return [IsAuthenticated(), IsOfferOwner()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return OfferListSerializer
        return OfferCreateUpdateSerializer

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        ordering = request.query_params.get("ordering")
        if ordering and "min_price" in ordering:
            qs = qs.annotate(min_price=Min("details__price")).order_by(ordering)
            self.queryset = qs
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save()

class OfferDetailRetrieveView(generics.RetrieveAPIView):
    queryset = OfferDetail.objects.all()
    serializer_class = OfferDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"
