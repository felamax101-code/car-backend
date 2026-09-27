from rest_framework.permissions import BasePermission


class HasRole(BasePermission):
    """
    Base class — subclass and set `allowed_roles`.
    Use directly on any APIView: permission_classes = [IsAdmin]
    """

    allowed_roles: tuple[str, ...] = ()

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user and user.is_authenticated and user.role in self.allowed_roles
        )


class IsAdmin(HasRole):
    allowed_roles = ("ADMIN",)


class IsGateOperator(HasRole):
    allowed_roles = ("GATE_OPERATOR",)


class IsAdminOrGateOperator(HasRole):
    """Use this on entry/exit endpoints — gate clerks operate them day-to-day,
    admins can too (e.g. for testing or manual override)."""

    allowed_roles = ("ADMIN", "GATE_OPERATOR")


class IsDriver(HasRole):
    allowed_roles = ("DRIVER",)