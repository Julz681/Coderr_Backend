from rest_framework.permissions import BasePermission

class IsBusinessForStatusUpdate(BasePermission):
    def has_object_permission(self, request, view, obj):
        prof = getattr(request.user, "profile", None)
        return bool(prof and prof.type == "business" and obj.business_user == request.user)

class IsStaffForDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_staff)

class IsCustomerForOrderCreate(BasePermission):
    """
    Allow creating orders only for users with profile.type == 'customer'.
    Returns 403 (Forbidden) on POST if condition is not met.
    """
    def has_permission(self, request, view):
        if request.method != "POST":
            return True
        prof = getattr(request.user, "profile", None)
        return bool(prof and prof.type == "customer")
