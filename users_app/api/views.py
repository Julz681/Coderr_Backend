from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.models import Token
from users_app.models import UserProfile
from .serializers import RegistrationSerializer, LoginSerializer, ProfileSerializer
from .permissions import IsSelfOrReadOnly

class RegistrationView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "username": user.username,
            "email": user.email,
            "user_id": user.id,
        })

class ProfileDetailView(generics.RetrieveUpdateAPIView):
    queryset = UserProfile.objects.select_related("user").all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated & IsSelfOrReadOnly]
    lookup_field = "user__id"

    def get_object(self):
        user_id = self.kwargs.get("pk")
        return generics.get_object_or_404(self.get_queryset(), user__id=user_id)

class BusinessProfilesListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.select_related("user").filter(type="business")

class CustomerProfilesListView(generics.ListAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserProfile.objects.select_related("user").filter(type="customer")
