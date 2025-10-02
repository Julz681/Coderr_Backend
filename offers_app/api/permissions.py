from rest_framework.permissions import BasePermission


class IsBusiness(BasePermission):
    """
    Only allow 'business' profiles to create offers.
    """

    def has_permission(self, request, view):
        prof = getattr(request.user, "profile", None)
        return bool(request.user and request.user.is_authenticated and prof and prof.type == "business")


class IsOfferOwner(BasePermission):
    """
    Object-level permission to allow modifications only by the offer creator.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
