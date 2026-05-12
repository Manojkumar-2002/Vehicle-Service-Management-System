from rest_framework.permissions import BasePermission


class IsOperationsUser(BasePermission):
    """Allows access only to users in the 'operations' group."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='operations').exists()


class IsRegularUser(BasePermission):
    """Allows access only to users in the 'user' group."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='user').exists()


class IsOperationsOrReadOnly(BasePermission):
    """
    Operations users can create/update/delete.
    Regular users can only read (GET).
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return request.user.groups.filter(name='operations').exists()