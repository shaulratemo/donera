from rest_framework.permissions import BasePermission


class IsOrganizationAdmin(BasePermission):
    """Allows access only to authenticated organization users."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "ORGANIZATION"
        )