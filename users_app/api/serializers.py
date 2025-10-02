from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers
from users_app.models import UserProfile


class ProfileSerializer(serializers.ModelSerializer):
    """
    Read/Write serializer for user profiles.
    - Exposes User id/username/email via computed fields.
    - Ensures string fields never return null (model defaults already handle this).
    - PATCH may also update the user's email.
    """
    username = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ("type", "created_at")

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    def get_user(self, obj):
        return obj.user.id

    def update(self, instance, validated_data):
        """
        Update mutable profile fields. If 'email' is present in payload,
        update the related User.email as well.
        """
        email = self.initial_data.get("email")
        if email is not None:
            instance.user.email = email
            instance.user.save(update_fields=["email"])

        # Only touch allowed fields; everything else stays as-is.
        for f in ["first_name", "last_name", "location", "tel", "description", "working_hours", "file"]:
            if f in validated_data:
                setattr(instance, f, validated_data[f])
        instance.save()
        return instance


class RegistrationSerializer(serializers.Serializer):
    """
    Input serializer used by /api/registration/.
    Creates a Django User and a paired UserProfile of the requested type.
    """
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=UserProfile.TYPE_CHOICES)

    def validate(self, attrs):
        if attrs["password"] != attrs["repeated_password"]:
            raise serializers.ValidationError({"repeated_password": "Passwords do not match"})
        if User.objects.filter(username=attrs["username"]).exists():
            raise serializers.ValidationError({"username": "Username already exists"})
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        UserProfile.objects.create(user=user, type=validated_data["type"])
        return user


class LoginSerializer(serializers.Serializer):
    """
    Input serializer used by /api/login/ to authenticate a user.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(username=attrs["username"], password=attrs["password"])
        if not user:
            raise serializers.ValidationError("Invalid credentials")
        attrs["user"] = user
        return attrs
