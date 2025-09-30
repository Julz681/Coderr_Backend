from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from reviews_app.models import Review
from .serializers import ReviewSerializer
from .permissions import IsReviewer

class ReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["business_user", "reviewer"]
    ordering_fields = ["updated_at", "rating"]

    def get_queryset(self):
        return Review.objects.all()

    def perform_create(self, serializer):
        serializer.save()

class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated, IsReviewer]
    http_method_names = ["get", "patch", "delete"]
