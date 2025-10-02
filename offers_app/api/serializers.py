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


class OfferRetrieveSerializer(serializers.ModelSerializer):
    """
    Serializer for Offer detail view (GET /api/offers/{id}/).
    Matches the documentation by providing detail links and
    min_price/min_delivery_time, but no extra user_details field.
    """
    details = OfferDetailReadLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()

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
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(m=Min("price"))["m"]

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(m=Min("delivery_time_in_days"))["m"]


class OfferDetailItemSerializer(serializers.ModelSerializer):
    """
    Slim serializer used for creation/update input.
    No 'id' in request body.
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


class OfferDetailFullSerializer(serializers.ModelSerializer):
    """
    Full serializer with 'id', used in response after creation/update.
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



class OfferReadSerializer(serializers.ModelSerializer):
    """
    Serializer for returning an offer with FULL detail objects.
    Used for POST /api/offers/ and PATCH /api/offers/{id}/ responses.
    """
    details = OfferDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]


class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating Offer instances.
    Handles nested creation and in-place updates of OfferDetails.

    Rules enforced to match API documentation:
    - Create requires exactly 3 details with distinct offer_type values:
      {'basic', 'standard', 'premium'}.
    - PATCH updates only provided fields. Details are updated in-place,
      matched by 'offer_type'; IDs remain unchanged.
    - Responses for POST/PATCH include full detail objects with IDs.
    """
    details = OfferDetailItemSerializer(many=True, required=False)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]

    def validate(self, attrs):
        if self.instance is None:
            details = attrs.get("details", [])
            if len(details) != 3:
                raise serializers.ValidationError(
                    {"details": "Exactly 3 details are required: basic, standard, premium."}
                )
            types = {d.get("offer_type") for d in details}
            if types != {"basic", "standard", "premium"}:
                raise serializers.ValidationError(
                    {"details": "Detail types must be exactly {'basic','standard','premium'}."}
                )
        else:
            details = attrs.get("details")
            if details is not None:
                for d in details:
                    if "offer_type" not in d:
                        raise serializers.ValidationError(
                            {"details": "Each detail item must include 'offer_type' to update."}
                        )
        return attrs

    def create(self, validated_data):
        details_data = validated_data.pop("details", [])
        offer = Offer.objects.create(**validated_data)
        for item in details_data:
            OfferDetail.objects.create(offer=offer, **item)
        return offer

    def update(self, instance, validated_data):
        """
        Partial update behaviour:

        - Offer fields ('title', 'image', 'description') are updated if provided.
        - If 'details' is provided: update existing details matched by 'offer_type'
          in-place (IDs remain the same). Non-provided details stay unchanged.
        - No creation/deletion of details on PATCH to adhere to the spec.
        """
        details_data = validated_data.pop("details", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
            existing = {d.offer_type: d for d in instance.details.all()}
            for item in details_data:
                otype = item["offer_type"]
                if otype not in existing:
                    raise serializers.ValidationError(
                        {"details": f"No existing detail with offer_type='{otype}' to update."}
                    )
                detail = existing[otype]
                for f in ["title", "revisions", "delivery_time_in_days", "price", "features"]:
                    if f in item:
                        setattr(detail, f, item[f])
                detail.save()

        return instance

    def to_representation(self, instance):
        """
        Return full offer data with FULL details (including IDs) to match docs.
        """
        rep = super().to_representation(instance)
        rep["details"] = OfferDetailSerializer(instance.details.all(), many=True).data
        return rep

