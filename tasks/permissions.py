from rest_framework.permissions import BasePermission


class HasRolePermission(BasePermission):
    """
    Base permission to check if user has any of the allowed roles.
    Override `roles` attribute in subclasses.
    """
    roles = []

    def has_permission(self, request, view):
        if not request or not request.user:
            return False
        user = request.user
        return user.is_authenticated and (
            user.is_superuser or user.has_any_role(self.roles)
        )


class CanManageTasks(HasRolePermission):
    roles = ['admin', 'manager', 'fieldofficer', 'owner']


class CanViewTasks(HasRolePermission):
    roles = [
        'admin', 'manager', 'fieldofficer',
        'farmer', 'owner', 'agronomist', 'qualitycontrol'
    ]

    def has_object_permission(self, request, view, obj):
        user = request.user
        return (
            user.is_superuser or
            user.has_any_role(['admin', 'manager']) or
            obj.assigned_to == user or
            obj.created_by == user
        )


class IsGrapesFarmerOrFieldOfficer(BasePermission):
    """
    Allow only Grapes industry farmers and field officers to use notification APIs.
    Does not affect other industries or roles.
    """

    def has_permission(self, request, view):
        if not request or not request.user or not request.user.is_authenticated:
            return False
        user = request.user
        if user.is_superuser:
            return True
        if not user.has_any_role(['farmer', 'fieldofficer']):
            return False
        if not getattr(user, 'industry', None):
            return False
        return getattr(user.industry, 'crop_type', None) == 'grapes'
