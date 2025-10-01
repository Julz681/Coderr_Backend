from rest_framework.permissions import BasePermission


class IsBusinessForStatusUpdate(BasePermission):
    """
    Permission that allows only business users,
    who own the object, to update its status.
    """
    def has_object_permission(self, request, view, obj):
        prof = getattr(request.user, "profile", None)
        return bool(prof and prof.type == "business" and obj.business_user == request.user)


class IsStaffForDelete(BasePermission):
    """
    Permission that allows only staff users to delete objects.
    """
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_staff)
