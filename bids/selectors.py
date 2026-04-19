"""
bids/selectors.py
Read-only query helpers for bids.
"""

from django.db.models import QuerySet
from .models import Bid


def get_bids_by_user(*, user) -> QuerySet:
    return Bid.objects.filter(user=user).select_related("listing__category").order_by("-timestamp")


def get_bids_for_listing(*, listing) -> QuerySet:
    return Bid.objects.filter(listing=listing).select_related("user").order_by("-amount")


def get_highest_bid(*, listing) -> "Bid | None":
    return Bid.objects.filter(listing=listing).order_by("-amount").first()
