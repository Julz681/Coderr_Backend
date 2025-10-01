from django.urls import path
from .views import BaseInfoView

"""
URL configuration for stats_app API.
Provides a route for retrieving base application information.
"""

urlpatterns = [
    path("base-info/", BaseInfoView.as_view(), name="base-info"),
]
