"""
disputes/views.py
Views for raising and tracking buyer disputes.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from orders.models import Order

from .forms import RaiseDisputeForm
from .models import Dispute
from .services import raise_dispute


class RaiseDisputeView(LoginRequiredMixin, View):
    """Buyer opens a dispute against a completed order."""

    template_name = "disputes/raise.html"

    def _get_order(self, request, reference):
        order = get_object_or_404(Order, reference=reference)
        if order.buyer != request.user:
            raise PermissionDenied
        return order

    def get(self, request, reference):
        order = self._get_order(request, reference)
        return render(request, self.template_name, {
            "order": order,
            "form": RaiseDisputeForm(),
        })

    def post(self, request, reference):
        order = self._get_order(request, reference)
        form = RaiseDisputeForm(request.POST)
        if form.is_valid():
            try:
                dispute = raise_dispute(
                    order=order,
                    user=request.user,
                    reason=form.cleaned_data["reason"],
                )
                messages.success(
                    request,
                    "Your dispute has been submitted. Our team will review it shortly.",
                )
                return redirect(dispute.get_absolute_url())
            except (PermissionDenied, ValidationError) as exc:
                messages.error(request, str(exc))

        return render(request, self.template_name, {"order": order, "form": form})


class DisputeDetailView(LoginRequiredMixin, View):
    """View dispute status and resolution. Accessible by the buyer who raised it or staff."""

    template_name = "disputes/detail.html"

    def get(self, request, pk):
        dispute = get_object_or_404(Dispute, pk=pk)
        if dispute.raised_by != request.user and not request.user.is_staff:
            raise PermissionDenied
        return render(request, self.template_name, {"dispute": dispute})
