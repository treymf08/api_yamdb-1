from rest_framework import permissions

YOU_CANNOT = 'У вас недостаточно прав для данного действия.'


class IsAdmin(permissions.BasePermission):
    message = YOU_CANNOT

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'admin' or request.user.is_superuser
        return False


class IsModerator(permissions.BasePermission):
    message = YOU_CANNOT

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.role == 'moderator'
        return False
