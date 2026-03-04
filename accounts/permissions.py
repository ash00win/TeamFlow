from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "OWNER"


class IsManagerOrOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ["OWNER", "MANAGER"]


class IsProjectMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.role in ["OWNER", "MANAGER"]:
            return True

        return obj.assigned_to == request.user