from rest_framework import serializers
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for listing/creating/updating reviews.
    - 'reviewer' is set to the current user on create.
    - Validates rating boundaries and prevents duplicate/self-reviews.
    """

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
            # Prevent reviewing yourself
            if attrs["business_user"] == request.user:
                raise serializers.ValidationError("Cannot review yourself")
            # One review per business per reviewer
            if Review.objects.filter(business_user=attrs["business_user"], reviewer=request.user).exists():
                raise serializers.ValidationError("You have already reviewed this business")

        # Rating must be in [1..5]
        if "rating" in attrs and not (1 <= int(attrs["rating"]) <= 5):
            raise serializers.ValidationError({"rating": "Rating must be between 1 and 5"})
        return attrs

    def create(self, validated_data):
        validated_data["reviewer"] = self.context["request"].user
        return super().create(validated_data)
