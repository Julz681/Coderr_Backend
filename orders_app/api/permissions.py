from rest_framework.permissions import BasePermission

class IsBusinessForStatusUpdate(BasePermission):
    def has_object_permission(self, request, view, obj):
        prof = getattr(request.user, "profile", None)
        return bool(prof and prof.type == "business" and obj.business_user == request.user)

class IsStaffForDelete(BasePermission):
    def has_object_permission(self, request, view, obj):
        return bool(request.user and request.user.is_staff)
