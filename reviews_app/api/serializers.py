from rest_framework import serializers
from reviews_app.models import Review

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ("reviewer", "created_at", "updated_at")

    def validate(self, attrs):
        request = self.context["request"]
        if request.method == "POST":
            prof = getattr(request.user, "profile", None)
            if not prof or prof.type != "customer":
                raise serializers.ValidationError("Only customers can create reviews")
            if attrs["business_user"] == request.user:
                raise serializers.ValidationError("Cannot review yourself")
        if "rating" in attrs and not (1 <= int(attrs["rating"]) <= 5):
            raise serializers.ValidationError({"rating": "Rating must be between 1 and 5"})
        return attrs

    def create(self, validated_data):
        validated_data["reviewer"] = self.context["request"].user
        return super().create(validated_data)
