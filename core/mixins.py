"""
core/mixins.py
Reusable view mixins to keep views DRY.
"""

from django.contrib import messages
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect


class SellerRequiredMixin(AccessMixin):
    """
    Allow access only to authenticated users with role=SELLER.
    Non-sellers are redirected to the dashboard with an error message.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_seller:
            messages.error(
                request,
                "Only seller accounts can perform this action. "
                "Please update your account role.",
            )
            return redirect("accounts:dashboard")

        return super().dispatch(request, *args, **kwargs)


class StaffRequiredMixin(AccessMixin):
    """Allow access only to is_staff users."""

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.is_staff:
            messages.error(request, "You do not have permission to access this page.")
            return redirect("accounts:dashboard")

        return super().dispatch(request, *args, **kwargs)


class ValidatedUserRequiredMixin(AccessMixin):
    """
    Allow access only to users validated by admin.
    Used for bid-sensitive pages.
    """

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not request.user.can_bid:
            messages.warning(
                request,
                "Your account is pending admin validation. "
                "You will be able to bid once approved.",
            )
            return redirect("accounts:dashboard")

        return super().dispatch(request, *args, **kwargs)
