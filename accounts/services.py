"""
accounts/services.py
Business logic for account management.
Views should call these functions instead of touching models directly.
"""

from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@transaction.atomic
def register_user(
    *,
    email: str,
    password: str,
    full_name: str,
    phone: str = "",
    address: str = "",
    national_id: str = "",
    role: str = "BUYER",
) -> "User":
    """
    Create and return a new (unvalidated) user account.
    Raises ValidationError if the email is already taken.
    """
    if User.objects.filter(email__iexact=email).exists():
        raise ValidationError(_("An account with this email already exists."))

    user = User.objects.create_user(
        email=email,
        password=password,
        full_name=full_name,
        phone=phone,
        address=address,
        national_id=national_id,
        role=role,
    )
    return user


@transaction.atomic
def update_profile(
    *,
    user: "User",
    full_name: str,
    phone: str,
    address: str,
    national_id: str,
) -> "User":
    """Update mutable profile fields for an existing user."""
    user.full_name = full_name
    user.phone = phone
    user.address = address
    user.national_id = national_id
    user.save(update_fields=["full_name", "phone", "address", "national_id"])
    return user


@transaction.atomic
def validate_user(*, user: "User", validated_by: "User") -> "User":
    """
    Mark a user as validated by admin.
    Only staff/superuser may call this.
    """
    if not validated_by.is_staff:
        raise ValidationError(_("Only staff members can validate users."))

    user.is_validated_by_admin = True
    user.save(update_fields=["is_validated_by_admin"])
    return user


@transaction.atomic
def deactivate_user(*, user: "User", deactivated_by: "User") -> "User":
    """Soft-deactivate a user account."""
    if not deactivated_by.is_staff:
        raise ValidationError(_("Only staff members can deactivate accounts."))

    user.is_active = False
    user.save(update_fields=["is_active"])
    return user
