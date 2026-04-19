"""
bids/services.py
Business logic for placing bids.
All rules are enforced here; views are kept thin.
"""

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Bid


@transaction.atomic
def place_bid(*, user, listing, amount: Decimal) -> Bid:
    """
    Place a bid on an active listing.

    Rules enforced:
    1. User must be authenticated and validated by admin.
    2. Listing must be ACTIVE and within its time window.
    3. Bid amount must exceed current highest bid + BID_INCREMENT.
    4. A seller cannot bid on their own listing.
    """
    # ── Rule 1: user validation ───────────────────────────────────────────────
    if not user.is_authenticated:
        raise PermissionDenied(_("You must be logged in to bid."))

    if not user.is_profile_complete:
        raise ValidationError(
            _(
                "Your profile is incomplete. Please fill in your name, phone, "
                "address, and national ID at /accounts/profile/ before bidding."
            )
        )

    if not user.can_bid:
        raise PermissionDenied(
            _(
                "Your account has not been validated yet. "
                "Please wait for admin approval before bidding."
            )
        )

    # ── Rule 2: listing state ─────────────────────────────────────────────────
    if not listing.is_active:
        raise ValidationError(_("This auction is not currently active."))

    now = timezone.now()
    if now < listing.start_time or now > listing.end_time:
        raise ValidationError(_("This auction is outside its bidding window."))

    # ── Rule 3: seller cannot bid on own listing ──────────────────────────────
    if listing.seller_id == user.pk:
        raise ValidationError(_("You cannot bid on your own listing."))

    # ── Rule 4: minimum bid amount ────────────────────────────────────────────
    increment = getattr(settings, "BID_INCREMENT", Decimal("10.00"))
    highest_bid = listing.bids.order_by("-amount").first()
    minimum_amount = (
        highest_bid.amount + increment if highest_bid else listing.min_public_price
    )

    if amount < minimum_amount:
        raise ValidationError(
            _(
                "Your bid must be at least %(min)s "
                "(current highest + increment of %(inc)s)."
            )
            % {"min": minimum_amount, "inc": increment}
        )

    bid = Bid.objects.create(user=user, listing=listing, amount=amount)
    return bid
