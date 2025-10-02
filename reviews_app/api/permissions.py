from rest_framework.permissions import BasePermission


class IsReviewer(BasePermission):
    """
    Only the original reviewer may update/delete their review.
    """

    def has_object_permission(self, request, view, obj):
        return obj.reviewer == request.user


class IsCustomerForCreate(BasePermission):
    """
    Only users with profile.type == 'customer' may create reviews.
    Returns 403 on POST if violated, as required by the docs.
    """

    def has_permission(self, request, view):
        if request.method != "POST":
            return True
        prof = getattr(request.user, "profile", None)
        return bool(prof and prof.type == "customer")
