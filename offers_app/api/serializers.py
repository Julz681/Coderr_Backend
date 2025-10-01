from rest_framework import serializers
from django.urls import reverse
from django.db.models import Min
from offers_app.models import Offer, OfferDetail


def _user_details_for(offer: Offer) -> dict:
    """
    Helper function that extracts basic user profile information
    for a given offer.
    """
    prof = getattr(offer.user, "profile", None)
    if not prof:
        return {"first_name": "", "last_name": "", "username": offer.user.username}
    return {
        "first_name": prof.first_name,
        "last_name": prof.last_name,
        "username": offer.user.username,
    }


class OfferDetailReadLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for OfferDetail that returns only the ID
    and a generated URL link to the detail.
    """
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(reverse("offerdetail-detail", args=[obj.id]))


class OfferDetailSerializer(serializers.ModelSerializer):
    """
    Full serializer for OfferDetail, used for detailed read operations.
    """
    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]
        read_only_fields = ("id",)


class OfferListSerializer(serializers.ModelSerializer):
    """
    Serializer for Offer list views.
    Includes related details, minimum price, minimum delivery time,
    and user profile data.
    """
    details = OfferDetailReadLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user_details = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(m=Min("price"))["m"]

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(m=Min("delivery_time_in_days"))["m"]

    def get_user_details(self, obj):
        return _user_details_for(obj)


class OfferDetailItemSerializer(serializers.ModelSerializer):
    """
    Slim serializer for OfferDetail, used when creating or updating offers.
    Excludes the 'id' field because details are newly created or replaced.
    """
    class Meta:
        model = OfferDetail
        fields = [
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Offer instances.
    Handles nested creation and replacement of OfferDetails.
    """
    details = OfferDetailItemSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]

    def create(self, validated_data):
        details_data = validated_data.pop("details", [])

        offer = Offer.objects.create(**validated_data)
        for item in details_data:
            OfferDetail.objects.create(offer=offer, **item)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            instance.details.all().delete()
            for item in details_data:
                OfferDetail.objects.create(offer=instance, **item)

        return instance
