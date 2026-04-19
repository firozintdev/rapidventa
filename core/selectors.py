"""
core/selectors.py
Read-only platform-wide query helpers. No mutations here.
"""

from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone


def get_platform_stats() -> dict:
    """Aggregate platform-wide metrics for the admin dashboard."""
    from accounts.models import User
    from bids.models import Bid
    from listings.models import Listing
    from orders.models import Order

    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = today_start - timedelta(days=today_start.weekday())

    # ── Users ─────────────────────────────────────────────────────────────────
    total_users = User.objects.count()
    validated_users = User.objects.filter(is_validated_by_admin=True).count()
    pending_users = total_users - validated_users

    # ── Listings by status ────────────────────────────────────────────────────
    status_display = dict(Listing.Status.choices)
    listing_status_counts = [
        {
            "status": row["status"],
            "label": status_display.get(row["status"], row["status"]),
            "count": row["count"],
        }
        for row in (
            Listing.objects
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
    ]
    # Handy quick-lookup dict for individual status values
    _status_map = {row["status"]: row["count"] for row in listing_status_counts}

    # ── Bids ──────────────────────────────────────────────────────────────────
    bids_today = Bid.objects.filter(timestamp__gte=today_start).count()
    bids_this_week = Bid.objects.filter(timestamp__gte=week_start).count()
    bids_all_time = Bid.objects.count()

    # ── Orders by status ──────────────────────────────────────────────────────
    order_status_display = dict(Order.Status.choices)
    order_status_counts = [
        {
            "status": row["status"],
            "label": order_status_display.get(row["status"], row["status"]),
            "count": row["count"],
        }
        for row in (
            Order.objects
            .values("status")
            .annotate(count=Count("id"))
            .order_by("status")
        )
    ]
    total_orders = Order.objects.count()
    total_revenue = (
        Order.objects.aggregate(total=Sum("winning_bid_amount"))["total"] or 0
    )

    # ── Recent orders ─────────────────────────────────────────────────────────
    recent_orders = (
        Order.objects
        .select_related("listing__seller", "buyer")
        .order_by("-created_at")[:10]
    )

    return {
        # Users
        "total_users": total_users,
        "validated_users": validated_users,
        "pending_users": pending_users,
        # Listings
        "listing_status_counts": listing_status_counts,
        "total_listings": sum(row["count"] for row in listing_status_counts),
        "voided_count": _status_map.get("VOID", 0),
        "republished_count": _status_map.get("REPUBLISHED", 0),
        # Bids
        "bids_today": bids_today,
        "bids_this_week": bids_this_week,
        "bids_all_time": bids_all_time,
        # Orders
        "order_status_counts": order_status_counts,
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        # Recent activity
        "recent_orders": recent_orders,
    }
