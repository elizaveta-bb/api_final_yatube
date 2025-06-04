from rest_framework.permissions import BasePermission

class IsAuthorOrReadOnly(BasePermission):
    """Custom permission: Only owner can edit, others can view."""
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user == obj.author
