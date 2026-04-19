"""
accounts/admin.py
Admin panel customisation for user management and validation workflow.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email", "full_name", "role", "is_validated_by_admin",
        "is_active", "is_staff", "date_joined",
    )
    list_filter = ("role", "is_validated_by_admin", "is_active", "is_staff")
    search_fields = ("email", "full_name", "phone", "national_id")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_login")

    # ── Fieldsets ─────────────────────────────────────────────────────────────
    fieldsets = (
        (_("Credentials"), {"fields": ("email", "password")}),
        (
            _("Personal Info"),
            {"fields": ("full_name", "phone", "address", "national_id")},
        ),
        (
            _("Role & Validation"),
            {"fields": ("role", "is_validated_by_admin")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important Dates"), {"fields": ("date_joined", "last_login")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "full_name",
                    "role",
                    "password1",
                    "password2",
                    "is_validated_by_admin",
                ),
            },
        ),
    )

    # ── Bulk actions ──────────────────────────────────────────────────────────
    actions = ["validate_users", "invalidate_users"]

    @admin.action(description=_("✅ Mark selected users as validated"))
    def validate_users(self, request, queryset):
        updated = queryset.update(is_validated_by_admin=True)
        self.message_user(request, f"{updated} user(s) validated successfully.")

    @admin.action(description=_("❌ Remove validation from selected users"))
    def invalidate_users(self, request, queryset):
        updated = queryset.update(is_validated_by_admin=False)
        self.message_user(request, f"{updated} user(s) unvalidated.")
