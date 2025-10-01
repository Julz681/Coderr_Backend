from rest_framework.permissions import BasePermission


class IsReviewer(BasePermission):
    """
    Permission that grants access only to the assigned reviewer of the object.
    """
    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user
