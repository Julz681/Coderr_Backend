from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OfferViewSet, OfferDetailRetrieveView

router = DefaultRouter()
router.register(r"offers", OfferViewSet, basename="offers")

urlpatterns = [
    path("", include(router.urls)),
    path("offerdetails/<int:pk>/", OfferDetailRetrieveView.as_view(), name="offerdetail-detail"),
]
