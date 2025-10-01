from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailRetrieveView


"""
URL configuration for offers_app API.
Provides routes for OfferViewSet and a detail view for OfferDetail.
"""

router = DefaultRouter()
router.register(r"offers", OfferViewSet, basename="offers")

urlpatterns = [
    path("", include(router.urls)),
    path("offerdetails/<int:pk>/", OfferDetailRetrieveView.as_view(), name="offerdetail-detail"),
]
