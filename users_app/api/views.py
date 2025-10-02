from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from users_app.models import UserProfile
from .serializers import RegistrationSerializer, LoginSerializer, ProfileSerializer
from .permissions import IsSelfOrReadOnly


class RegistrationView(generics.GenericAPIView):
    """
    POST /api/registration/
    Creates a new User + UserProfile and returns an auth token and user metadata.
    """
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(generics.GenericAPIView):
    """
    POST /api/login/
    Authenticates credentials and returns auth token + user metadata.
    """
    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "username": user.username,
                "email": user.email,
                "user_id": user.id,
            },
            status=status.HTTP_200_OK,
        )


class ProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    GET /api/profile/{pk}/
    PATCH /api/profile/{pk}/
    - Auth required
    - PATCH only allowed for profile owner (IsSelfOrReadOnly)
    """
    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsSelfOrReadOnly]

    # pk is the related User.id
    def get_object(self):
        """
        Resolve by related user ID and enforce object-level permission checks
        so non-owners receive HTTP 403 on PATCH.
        """
        user_id = self.kwargs.get("pk")
        obj = generics.get_object_or_404(self.get_queryset(), user__id=user_id)
        self.check_object_permissions(self.request, obj)
        return obj


class BusinessProfilesListView(generics.ListAPIView):
    """
    GET /api/profiles/business/
    Returns an array of business profiles (no pagination, as required by the FE).
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return UserProfile.objects.select_related("user").filter(type="business")


class CustomerProfilesListView(generics.ListAPIView):
    """
    GET /api/profiles/customer/
    Returns an array of customer profiles (no pagination).
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return UserProfile.objects.select_related("user").filter(type="customer")
