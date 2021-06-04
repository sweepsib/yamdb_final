from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        if request.user.is_authenticated:
            return request.user.is_admin
        return False

class IsAuthorOrAdminOrModeratorOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        if request.user.is_authenticated:
            if request.method == 'POST':
                return True
            return (
                obj.author == request.user or request.user.is_staff
            )
        return False

class IsAuthReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated

    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsStaffOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff

    def has_permission(self, request, view):
        return request.user.is_admin
