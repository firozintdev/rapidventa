"""
accounts/managers.py
Custom manager for the User model.
"""

from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager for User with email as the primary identifier."""

    def _create_user(self, email: str, password: str, **extra_fields):
        if not email:
            raise ValueError(_("An email address is required."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_validated_by_admin", True)

        if not extra_fields.get("is_staff"):
            raise ValueError(_("Superuser must have is_staff=True."))
        if not extra_fields.get("is_superuser"):
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(email, password, **extra_fields)

    def validated(self):
        """Return only admin-validated users."""
        return self.get_queryset().filter(is_validated_by_admin=True, is_active=True)

    def pending_validation(self):
        """Return users waiting for admin approval."""
        return self.get_queryset().filter(is_validated_by_admin=False, is_active=True)
