from rest_framework.permissions import BasePermission


class IsActiveUser(BasePermission):
    message = "Permission denied, your account is inactive."

    def has_object_permission(self, request, view, obj):
        return request.user.is_active
