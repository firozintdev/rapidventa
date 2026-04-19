"""
accounts/selectors.py
Read-only query helpers. Never mutate data here.
"""

from django.contrib.auth import get_user_model
from django.db.models import Avg, QuerySet

from bids.models import Bid

User = get_user_model()


def get_user_by_email(email: str) -> "User | None":
    return User.objects.filter(email__iexact=email).first()


def get_user_by_id(user_id: int) -> "User | None":
    return User.objects.filter(pk=user_id).first()


def get_validated_users() -> QuerySet:
    return User.objects.validated()


def get_pending_validation_users() -> QuerySet:
    return User.objects.pending_validation()


def get_all_sellers() -> QuerySet:
    return User.objects.filter(role="SELLER", is_active=True)


def get_won_auctions(*, user) -> QuerySet:
    """Bids where the listing closed and this user is the buyer on the order."""
    return (
        Bid.objects.filter(user=user, listing__status="CLOSED", listing__order__buyer=user)
        .select_related("listing__category", "listing__order")
        .order_by("-timestamp")
    )


def get_lost_auctions(*, user) -> QuerySet:
    """Bids on closed listings where someone else won."""
    return (
        Bid.objects.filter(user=user, listing__status="CLOSED")
        .exclude(listing__order__buyer=user)
        .select_related("listing__category", "listing__order")
        .order_by("-timestamp")
    )


def get_seller_public_profile(*, seller_id: int) -> "dict | None":
    """
    Return public stats for a seller. Returns None if the user does not
    exist, is not a seller, or is inactive — the view should raise Http404.
    """
    from listings.models import Listing, Review

    try:
        seller = User.objects.get(pk=seller_id, role=User.Role.SELLER, is_active=True)
    except User.DoesNotExist:
        return None

    listings_qs = Listing.objects.filter(seller=seller)

    active_listings = (
        Listing.objects.active()
        .filter(seller=seller)
        .select_related("category")
        .prefetch_related("images", "bids")
        .order_by("end_time")
    )

    raw_avg = (
        Review.objects.filter(listing__seller=seller)
        .aggregate(avg=Avg("rating"))["avg"]
    )
    avg_rating = round(raw_avg, 1) if raw_avg else 0

    return {
        "seller": seller,
        "total_listings": listings_qs.count(),
        "closed_count": listings_qs.filter(status=Listing.Status.CLOSED).count(),
        "active_listings": active_listings,
        "avg_rating": avg_rating,
    }


def get_void_auctions(*, user) -> QuerySet:
    """Bids on listings that ended void (reserve not met)."""
    return (
        Bid.objects.filter(user=user, listing__status="VOID")
        .select_related("listing__category")
        .order_by("-timestamp")
    )
