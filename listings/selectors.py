"""
listings/selectors.py
Read-only query helpers for listings. No mutations here.
"""

from django.db.models import Count, QuerySet, Sum
from .models import Category, Listing, Watchlist


def get_active_listings(*, category_slug: str = None, order_by: str = "end_time") -> QuerySet:
    from django.db.models import Q
    qs = Listing.objects.active().select_related("category", "seller")
    if category_slug:
        # Match the category itself or any of its children
        qs = qs.filter(
            Q(category__slug=category_slug) |
            Q(category__parent__slug=category_slug)
        )
    return qs.order_by(order_by)


def get_listing_detail(*, pk: int) -> "Listing | None":
    return (
        Listing.objects.select_related("category", "seller")
        .prefetch_related("bids__user")
        .filter(pk=pk)
        .first()
    )


def get_listings_by_seller(*, seller) -> QuerySet:
    return Listing.objects.by_seller(seller).select_related("category")


def get_all_categories() -> QuerySet:
    """Return root categories with their children prefetched, ordered."""
    return (
        Category.objects.filter(parent__isnull=True)
        .prefetch_related("children")
        .order_by("order", "name")
    )


def get_pending_listings() -> QuerySet:
    return Listing.objects.pending().select_related("category", "seller")


def get_seller_analytics(*, seller) -> dict:
    """Return aggregated analytics data for the given seller."""
    from bids.models import Bid
    from orders.models import Order

    listings_qs = Listing.objects.filter(seller=seller)

    status_display = dict(Listing.Status.choices)
    status_counts = [
        {
            "status": row["status"],
            "label": status_display.get(row["status"], row["status"]),
            "count": row["count"],
        }
        for row in listings_qs.values("status").annotate(count=Count("id")).order_by("status")
    ]

    total_bids = Bid.objects.filter(listing__seller=seller).count()

    revenue = Order.objects.filter(listing__seller=seller).aggregate(
        total=Sum("winning_bid_amount")
    )
    total_revenue = revenue["total"] or 0

    top_listing = (
        listings_qs
        .annotate(bid_count=Count("bids"))
        .order_by("-bid_count")
        .first()
    )

    recent_bids = (
        Bid.objects.filter(listing__seller=seller)
        .select_related("user", "listing")
        .order_by("-timestamp")[:10]
    )

    return {
        "status_counts": status_counts,
        "total_listings": listings_qs.count(),
        "total_bids": total_bids,
        "total_revenue": total_revenue,
        "top_listing": top_listing,
        "recent_bids": recent_bids,
    }


def get_watchlist(*, user) -> QuerySet:
    """Return the user's watchlist entries, newest first, with listing data prefetched."""
    return (
        Watchlist.objects.filter(user=user)
        .select_related("listing__category", "listing__seller")
        .prefetch_related("listing__bids", "listing__images")
        .order_by("-added_at")
    )
