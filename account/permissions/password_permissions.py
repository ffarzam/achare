from rest_framework.permissions import BasePermission


class IsPasswordSet(BasePermission):
    message = "Permission denied, you have already set your password."

    def has_object_permission(self, request, view, obj):
        return not bool(obj.password)
