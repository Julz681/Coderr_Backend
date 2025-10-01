from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from orders_app.models import Order
from .serializers import (
    OrderSerializer,
    OrderCreateSerializer,
    OrderStatusUpdateSerializer,
)
from .permissions import IsBusinessForStatusUpdate, IsStaffForDelete


class OrderListCreateView(generics.ListCreateAPIView):
    """
    View for listing orders of the current user or creating new ones.
    Customers can create orders, businesses can view their related orders.
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OrderCreateSerializer
        return OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View for retrieving, updating, or deleting a specific order.
    Permissions differ depending on the action (update, delete).
    """
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PATCH", "PUT"]:
            return OrderStatusUpdateSerializer
        return OrderSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsStaffForDelete()]
        if self.request.method in ["PATCH", "PUT"]:
            return [IsAuthenticated(), IsBusinessForStatusUpdate()]
        return super().get_permissions()


class OrderCountView(APIView):
    """
    View for retrieving the number of in-progress orders
    for a specific business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, id=business_user_id)
        count = Order.objects.filter(business_user=user, status="in_progress").count()
        return Response({"order_count": count})


class CompletedOrderCountView(APIView):
    """
    View for retrieving the number of completed orders
    for a specific business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, id=business_user_id)
        count = Order.objects.filter(business_user=user, status="completed").count()
        return Response({"completed_order_count": count})
