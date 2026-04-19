from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Dispute
from .services import resolve_dispute


@admin.register(Dispute)
class DisputeAdmin(admin.ModelAdmin):
    list_display = (
        "id", "order_reference", "raised_by", "status", "created_at", "updated_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "order__reference", "raised_by__email", "raised_by__full_name",
    )
    ordering = ("-created_at",)
    readonly_fields = ("order", "raised_by", "reason", "created_at", "updated_at")

    fieldsets = (
        (_("Dispute Information"), {
            "fields": ("order", "raised_by", "reason", "status", "created_at", "updated_at"),
        }),
        (_("Resolution"), {
            "fields": ("resolution_notes",),
            "description": _(
                "Fill in resolution notes and set status to RESOLVED or CLOSED "
                "to close this dispute."
            ),
        }),
    )

    actions = ["mark_under_review", "mark_resolved", "mark_closed"]

    @admin.display(description=_("Order reference"))
    def order_reference(self, obj):
        return obj.order.short_reference

    @admin.action(description=_("Mark selected disputes as Under Review"))
    def mark_under_review(self, request, queryset):
        updated = queryset.filter(status=Dispute.Status.OPEN).update(
            status=Dispute.Status.UNDER_REVIEW
        )
        self.message_user(request, f"{updated} dispute(s) marked as Under Review.")

    @admin.action(description=_("Mark selected disputes as Resolved"))
    def mark_resolved(self, request, queryset):
        count = 0
        for dispute in queryset.filter(status__in=[Dispute.Status.OPEN, Dispute.Status.UNDER_REVIEW]):
            try:
                resolve_dispute(
                    dispute=dispute,
                    resolved_by=request.user,
                    notes=dispute.resolution_notes or "Resolved by admin action.",
                )
                count += 1
            except Exception:
                pass
        self.message_user(request, f"{count} dispute(s) marked as Resolved.")

    @admin.action(description=_("Mark selected disputes as Closed"))
    def mark_closed(self, request, queryset):
        updated = queryset.exclude(status=Dispute.Status.CLOSED).update(
            status=Dispute.Status.CLOSED
        )
        self.message_user(request, f"{updated} dispute(s) closed.")
