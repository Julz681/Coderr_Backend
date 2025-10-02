from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from reviews_app.models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewer, IsCustomerForCreate


class ReviewListCreateView(generics.ListCreateAPIView):
    """
    GET: list reviews (filterable/orderable)
    POST: create review (customer-only via permission -> 403 if not customer)
    """
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["business_user", "reviewer"]
    ordering_fields = ["updated_at", "rating"]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerForCreate()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save()


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: retrieve review
    PATCH/DELETE: reviewer-only (IsReviewer)
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewer]
    http_method_names = ["get", "patch", "delete"]
