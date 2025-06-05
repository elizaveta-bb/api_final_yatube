from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Custom permission: Only owner can edit, others can view."""

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user == obj.author)
