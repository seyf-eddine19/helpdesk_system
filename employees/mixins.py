from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

# Permission Required
class PermissionMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """
    Custom mixin that ensures the user has the required permission(s) OR is a superuser.
    """
    def has_permission(self):
        user = self.request.user
        perms = self.get_permission_required()
        if isinstance(perms, str):
            perms = [perms]
        return user.is_authenticated and (user.has_perms(perms) or user.is_superuser)