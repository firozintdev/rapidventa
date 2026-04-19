"""
accounts/models.py
Custom User model for RapidVenta with role-based access.
"""

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model replacing Django's default.
    Roles are additive: a Seller can also be a Buyer.
    Admin role is handled via is_staff / is_superuser.
    """

    class Role(models.TextChoices):
        BUYER = "BUYER", _("Buyer")
        SELLER = "SELLER", _("Seller")
        ADMIN = "ADMIN", _("Admin")

    # ── Identity ──────────────────────────────────────────────────────────────
    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=255)
    phone = models.CharField(_("phone number"), max_length=30, blank=True)
    address = models.TextField(_("address"), blank=True)
    national_id = models.CharField(
        _("national ID / document"), max_length=100, blank=True
    )

    # ── Role & Status ─────────────────────────────────────────────────────────
    role = models.CharField(
        _("role"), max_length=10, choices=Role.choices, default=Role.BUYER
    )
    is_validated_by_admin = models.BooleanField(
        _("validated by admin"),
        default=False,
        help_text=_("Must be True before the user can place bids."),
    )

    # ── Django internals ──────────────────────────────────────────────────────
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff"), default=False)
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"{self.full_name} <{self.email}>"

    # ── Convenience properties ────────────────────────────────────────────────
    @property
    def is_profile_complete(self) -> bool:
        """True only when all required contact fields are filled in."""
        return all([self.full_name, self.phone, self.address, self.national_id])

    @property
    def can_bid(self) -> bool:
        """User is active, has a complete profile, and is validated by admin."""
        return self.is_active and self.is_profile_complete and self.is_validated_by_admin

    @property
    def is_seller(self) -> bool:
        return self.role == self.Role.SELLER

    @property
    def is_buyer(self) -> bool:
        return self.role == self.Role.BUYER

    @property
    def display_role(self) -> str:
        return self.get_role_display()
