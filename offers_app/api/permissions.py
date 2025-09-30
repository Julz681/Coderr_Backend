from rest_framework.permissions import BasePermission

class IsBusiness(BasePermission):
    def has_permission(self, request, view):
        prof = getattr(request.user, "profile", None)
        return bool(request.user and request.user.is_authenticated and prof and prof.type == "business")

class IsOfferOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
