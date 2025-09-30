from rest_framework import serializers
from django.shortcuts import get_object_or_404
from orders_app.models import Order
from offers_app.models import OfferDetail

class OrderSerializer(serializers.ModelSerializer):
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
    offer_detail_id = serializers.IntegerField()

    def validate(self, attrs):
        user = self.context["request"].user
        prof = getattr(user, "profile", None)
        if not prof or prof.type != "customer":
            raise serializers.ValidationError("Only users with type 'customer' can create orders")
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
    class Meta:
        model = Order
        fields = ["status"]
