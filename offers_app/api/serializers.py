from rest_framework import serializers
from django.urls import reverse
from django.db.models import Min
from offers_app.models import Offer, OfferDetail

def _user_details_for(offer: Offer) -> dict:
    prof = getattr(offer.user, "profile", None)
    if not prof:
        return {"first_name": "", "last_name": "", "username": offer.user.username}
    return {
        "first_name": prof.first_name,
        "last_name": prof.last_name,
        "username": offer.user.username,
    }

class OfferDetailReadLinkSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = OfferDetail
        fields = ["id", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        return request.build_absolute_uri(reverse("offerdetail-detail", args=[obj.id]))

class OfferDetailSerializer(serializers.ModelSerializer):
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

class OfferCreateUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = ["id", "title", "image", "description", "details"]

    def validate_details(self, value):
        if len(value) != 3:
            raise serializers.ValidationError("An offer must contain exactly 3 details (basic, standard, premium)")
        types = {d.get("offer_type") for d in value}
        if types != {"basic", "standard", "premium"}:
            raise serializers.ValidationError("Details must include offer_type 'basic', 'standard' and 'premium'")
        return value

    def create(self, validated_data):
        details_data = validated_data.pop("details")
        offer = Offer.objects.create(user=self.context["request"].user, **validated_data)
        for d in details_data:
            OfferDetail.objects.create(offer=offer, **d)
        return offer

    def update(self, instance, validated_data):
        details_data = validated_data.pop("details", None)
        for attr in ["title", "image", "description"]:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])
        instance.save()
        if details_data is not None:
            existing = {od.offer_type: od for od in instance.details.all()}
            for d in details_data:
                ot = d.get("offer_type")
                if ot not in existing:
                    continue
                od = existing[ot]
                for f in ["title", "revisions", "delivery_time_in_days", "price", "features"]:
                    if f in d:
                        setattr(od, f, d[f])
                od.save()
        return instance
