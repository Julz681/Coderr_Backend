from rest_framework import serializers
from django.shortcuts import get_object_or_404
from orders_app.models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """
    Read-only serializer used for listing/retrieving orders and responses.
    Ensures price is rendered as a number in JSON.
    """
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class OrderCreateSerializer(serializers.Serializer):
    """
    Input serializer for POST /api/orders/.
    Accepts an OfferDetail ID and creates an Order for the authenticated customer.
    """
    offer_detail_id = serializers.IntegerField()

    def validate(self, attrs):
        od = get_object_or_404(OfferDetail, id=attrs["offer_detail_id"])
        attrs["offer_detail"] = od
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        od: OfferDetail = validated_data["offer_detail"]
        order = Order.objects.create(
            customer_user=user,
            business_user=od.offer.user,
            title=od.title,
            revisions=od.revisions,
            delivery_time_in_days=od.delivery_time_in_days,
            price=od.price,
            features=od.features,
            offer_type=od.offer_type,
        )
        return order


class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Input serializer for PATCH /api/orders/{id}/ to update the order status.
    """

    class Meta:
        model = Order
        fields = ["status"]
