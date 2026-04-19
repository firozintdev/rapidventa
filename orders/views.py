"""
orders/views.py
Class-based views for order tracking and management.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import TemplateView

from core.mixins import StaffRequiredMixin
from .forms import AdvanceOrderForm, UpdateTrackingForm
from .models import Order
from .selectors import get_order_by_reference, get_orders_by_buyer, get_all_orders
from .services import advance_order_status, cancel_order, update_tracking


class OrderListView(LoginRequiredMixin, TemplateView):
    """Buyer's order history."""

    template_name = "orders/list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = get_orders_by_buyer(buyer=self.request.user)
        return ctx


class OrderDetailView(LoginRequiredMixin, View):
    """Order detail + tracking for the buyer or staff."""

    template_name = "orders/detail.html"

    def get(self, request, reference):
        order = get_object_or_404(Order, reference=reference)

        # Buyers can only see their own orders
        if order.buyer != request.user and not request.user.is_staff:
            raise PermissionDenied

        advance_form = AdvanceOrderForm() if request.user.is_staff else None
        tracking_form = UpdateTrackingForm(instance=order) if request.user.is_staff else None

        return render(
            request,
            self.template_name,
            {
                "order": order,
                "advance_form": advance_form,
                "tracking_form": tracking_form,
            },
        )

    def post(self, request, reference):
        if not request.user.is_staff:
            raise PermissionDenied

        order = get_object_or_404(Order, reference=reference)
        action = request.POST.get("action")

        try:
            if action == "advance":
                form = AdvanceOrderForm(request.POST)
                if form.is_valid():
                    advance_order_status(
                        order=order,
                        advanced_by=request.user,
                        tracking_number=form.cleaned_data.get("tracking_number", ""),
                    )
                    messages.success(request, f"Order advanced to {order.get_status_display()}.")

            elif action == "cancel":
                cancel_order(order=order, cancelled_by=request.user)
                messages.success(request, "Order cancelled.")

            elif action == "tracking":
                form = UpdateTrackingForm(request.POST, instance=order)
                if form.is_valid():
                    update_tracking(
                        order=order,
                        tracking_number=form.cleaned_data["tracking_number"],
                        updated_by=request.user,
                    )
                    messages.success(request, "Tracking number updated.")

        except (ValidationError, PermissionDenied) as exc:
            messages.error(request, str(exc))

        return redirect("orders:detail", reference=reference)


class StaffOrderListView(StaffRequiredMixin, TemplateView):
    """Staff-only view of all orders."""

    template_name = "orders/staff_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        status_filter = self.request.GET.get("status", "")
        qs = get_all_orders()
        if status_filter:
            qs = qs.filter(status=status_filter)
        ctx["orders"] = qs
        ctx["status_choices"] = Order.Status.choices
        ctx["current_status"] = status_filter
        return ctx
