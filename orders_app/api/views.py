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
from .permissions import IsBusinessForStatusUpdate, IsStaffForDelete, IsCustomerForOrderCreate


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET: list orders where the user is either the customer or the business
    POST: create order (customer-only, enforced via permission to return 403)
    """

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated(), IsCustomerForOrderCreate()]
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user
        return Order.objects.filter(
            models.Q(customer_user=user) | models.Q(business_user=user)
        )

    def get_serializer_class(self):
        return OrderCreateSerializer if self.request.method == "POST" else OrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: retrieve an order
    PATCH: business owner updates status (returns full order object)
    DELETE: staff-only
    """
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        return OrderStatusUpdateSerializer if self.request.method in ["PATCH", "PUT"] else OrderSerializer

    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthenticated(), IsStaffForDelete()]
        if self.request.method in ["PATCH", "PUT"]:
            return [IsAuthenticated(), IsBusinessForStatusUpdate()]
        return super().get_permissions()

    def update(self, request, *args, **kwargs):
        """Return the full order after status update to match the docs."""
        kwargs["partial"] = True
        return self.partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        order = self.get_object()
        serializer = OrderStatusUpdateSerializer(order, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_200_OK)


class OrderCountView(APIView):
    """
    GET /api/order-count/{business_user_id}/
    Returns the count of 'in_progress' orders for the given business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, id=business_user_id)
        count = Order.objects.filter(business_user=user, status="in_progress").count()
        return Response({"order_count": count})


class CompletedOrderCountView(APIView):
    """
    GET /api/completed-order-count/{business_user_id}/
    Returns the count of 'completed' orders for the given business user.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, business_user_id):
        user = get_object_or_404(User, id=business_user_id)
        count = Order.objects.filter(business_user=user, status="completed").count()
        return Response({"completed_order_count": count})
