"""
bids/views.py
View for placing a bid on a listing.
"""

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from listings.models import Listing
from .forms import BidForm
from .services import place_bid


class PlaceBidView(LoginRequiredMixin, View):
    """POST-only view that places a bid on a listing."""

    def post(self, request, pk):
        listing = get_object_or_404(Listing, pk=pk)
        form = BidForm(request.POST)

        if form.is_valid():
            try:
                bid = place_bid(
                    user=request.user,
                    listing=listing,
                    amount=form.cleaned_data["amount"],
                )
                messages.success(
                    request,
                    f"Bid of ${bid.amount} placed successfully!",
                )
            except (ValidationError, PermissionDenied) as exc:
                messages.error(request, str(exc))
        else:
            for field_errors in form.errors.values():
                for error in field_errors:
                    messages.error(request, error)

        return redirect("listings:detail", pk=pk)
