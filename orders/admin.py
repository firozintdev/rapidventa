from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Order
from .services import advance_order_status


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "short_reference", "buyer", "listing", "status",
        "winning_bid_amount", "tracking_number", "created_at",
    )
    list_filter = ("status",)
    search_fields = (
        "buyer__email", "buyer__full_name",
        "listing__title", "tracking_number",
    )
    readonly_fields = ("reference", "created_at", "updated_at", "winning_bid_amount")
    ordering = ("-created_at",)

    fieldsets = (
        (_("Reference"), {"fields": ("reference",)}),
        (_("Parties"), {"fields": ("buyer", "listing")}),
        (_("Financials"), {"fields": ("winning_bid_amount",)}),
        (_("Status & Shipping"), {"fields": ("status", "tracking_number", "shipping_address", "notes")}),
        (_("Audit"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["mark_paid", "mark_shipped", "mark_completed"]

    @admin.action(description=_("Mark selected orders as PAID"))
    def mark_paid(self, request, queryset):
        for order in queryset.filter(status=Order.Status.PENDING_PAYMENT):
            try:
                advance_order_status(order=order, advanced_by=request.user)
            except Exception:
                pass
        self.message_user(request, "Orders marked as PAID.")

    @admin.action(description=_("Mark selected orders as SHIPPED"))
    def mark_shipped(self, request, queryset):
        for order in queryset.filter(status=Order.Status.PAID):
            try:
                advance_order_status(order=order, advanced_by=request.user)
            except Exception:
                pass
        self.message_user(request, "Orders marked as SHIPPED.")

    @admin.action(description=_("Mark selected orders as COMPLETED"))
    def mark_completed(self, request, queryset):
        for order in queryset.filter(status=Order.Status.SHIPPED):
            try:
                advance_order_status(order=order, advanced_by=request.user)
            except Exception:
                pass
        self.message_user(request, "Orders marked as COMPLETED.")
