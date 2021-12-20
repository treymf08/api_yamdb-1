from rest_framework import permissions

from users.models import UserRole

YOU_CANNOT = 'У вас недостаточно прав для данного действия.'


class IsAdmin(permissions.BasePermission):
    message = YOU_CANNOT

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return (request.user.role == UserRole.ADMIN.value
                    or request.user.is_superuser)
        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    message = YOU_CANNOT

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return (request.user.role == UserRole.ADMIN.value
                    or request.user.is_superuser)
        return False


class CommentReviewPermission(permissions.BasePermission):
    message = YOU_CANNOT

    def has_permission(self, request, view):
        return (request.user.is_authenticated
                or request.method in permissions.SAFE_METHODS)

    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return (obj.author == request.user or request.user.is_superuser
                    or request.user.role == UserRole.ADMIN.value
                    or request.user.role == UserRole.MODERATOR.value)
        return request.method in permissions.SAFE_METHODS
