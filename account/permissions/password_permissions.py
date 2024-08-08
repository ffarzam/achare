from rest_framework.permissions import BasePermission


class IsPasswordSet(BasePermission):
    message = "Permission denied, you have already set your password."

    def has_object_permission(self, request, view, obj):
        if request.data.get("password") or request.data.get("password").strip() in [""]:
            return not bool(obj.password)
        return True
