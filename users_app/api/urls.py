from django.urls import path
from .views import (
    RegistrationView,
    LoginView,
    ProfileDetailView,
    BusinessProfilesListView,
    CustomerProfilesListView,
)

"""
URL configuration for users_app API.
Provides routes for registration, login, profile details,
and listing business or customer profiles.
"""

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/",        LoginView.as_view(),        name="login"),
    path("profile/<int:pk>/", ProfileDetailView.as_view(), name="profile-detail"),
    path("profiles/business/", BusinessProfilesListView.as_view(), name="profiles-business"),
    path("profiles/customer/", CustomerProfilesListView.as_view(), name="profiles-customer"),
]
