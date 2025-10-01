from django.urls import path
from .views import ReviewListCreateView, ReviewDetailView

"""
URL configuration for reviews_app API.
Provides routes for listing/creating reviews and retrieving/updating/deleting a single review.
"""

urlpatterns = [
    path("reviews/", ReviewListCreateView.as_view(), name="reviews"),
    path("reviews/<int:pk>/", ReviewDetailView.as_view(), name="review-detail"),
]
