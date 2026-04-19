"""
core/views.py
Platform-level views (staff-only admin dashboard, etc.).
"""

from django.views.generic import TemplateView

from core.mixins import StaffRequiredMixin
from core.selectors import get_platform_stats


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    """Platform-wide analytics dashboard, visible to staff only."""

    template_name = "core/admin_dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update(get_platform_stats())
        return ctx


class HowToBidView(TemplateView):
    template_name = "core/how_to_bid.html"


class HowToSellView(TemplateView):
    template_name = "core/how_to_sell.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"
