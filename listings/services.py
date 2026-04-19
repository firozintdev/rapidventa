"""
listings/services.py
Business logic for listings: create, approve, close, void, republish, bulk upload.
Views must NOT replicate this logic.
"""

import csv
import io
from decimal import Decimal, InvalidOperation
from typing import IO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Category, Listing, ListingImage, Review, Watchlist

User = get_user_model()


@transaction.atomic
def create_listing(
    *,
    seller: "User",
    title: str,
    description: str,
    category: Category,
    min_public_price: Decimal,
    max_public_price: Decimal,
    secret_reserve_price: Decimal,
    start_time,
    end_time,
    buy_now_price: Decimal = None,
    sku: str = "",
    brand: str = "",
    weight: str = "",
    dimensions: str = "",
    tags: str = "",
) -> Listing:
    """
    Create a new listing in PENDING state awaiting admin approval.
    Only users with role=SELLER can create listings.
    """
    if not seller.is_seller:
        raise PermissionDenied(_("Only sellers can create listings."))

    if end_time <= start_time:
        raise ValidationError(_("End time must be after start time."))

    if min_public_price > max_public_price:
        raise ValidationError(
            _("Minimum public price cannot exceed maximum public price.")
        )

    listing = Listing.objects.create(
        seller=seller,
        title=title,
        description=description,
        category=category,
        min_public_price=min_public_price,
        max_public_price=max_public_price,
        secret_reserve_price=secret_reserve_price,
        start_time=start_time,
        end_time=end_time,
        buy_now_price=buy_now_price,
        sku=sku,
        brand=brand,
        weight=weight,
        dimensions=dimensions,
        tags=tags,
        status=Listing.Status.PENDING,
    )
    return listing


def add_listing_images(*, listing: Listing, images: list) -> None:
    """Attach uploaded image files to a listing. The first image is marked primary."""
    for idx, image_file in enumerate(images):
        ListingImage.objects.create(
            listing=listing,
            image=image_file,
            order=idx,
            is_primary=(idx == 0),
        )


@transaction.atomic
def approve_listing(*, listing: Listing, approved_by: "User") -> Listing:
    """Admin approves a PENDING listing, making it ACTIVE."""
    if not approved_by.is_staff:
        raise PermissionDenied(_("Only staff can approve listings."))

    if listing.status != Listing.Status.PENDING:
        raise ValidationError(
            _("Only PENDING listings can be approved. Current status: %(status)s")
            % {"status": listing.get_status_display()}
        )

    listing.status = Listing.Status.ACTIVE
    listing.save(update_fields=["status", "updated_at"])
    return listing


@transaction.atomic
def reject_listing(*, listing: Listing, rejected_by: "User") -> Listing:
    """Admin rejects a PENDING listing, returning it to DRAFT."""
    if not rejected_by.is_staff:
        raise PermissionDenied(_("Only staff can reject listings."))

    listing.status = Listing.Status.DRAFT
    listing.save(update_fields=["status", "updated_at"])
    return listing


@transaction.atomic
def close_listing(*, listing: Listing) -> Listing:
    """
    Attempt to close an auction.
    - Highest bid >= secret_reserve_price → CLOSED + Order created
    - Highest bid < secret_reserve_price  → VOID + auto-republish
    """
    # Avoid circular import
    from orders.services import create_order_from_listing
    from .services import republish_listing

    if listing.status != Listing.Status.ACTIVE:
        raise ValidationError(_("Only ACTIVE listings can be closed."))

    highest_bid = listing.bids.order_by("-amount").first()

    if highest_bid and highest_bid.amount >= listing.secret_reserve_price:
        listing.status = Listing.Status.CLOSED
        listing.save(update_fields=["status", "updated_at"])
        create_order_from_listing(listing=listing, winner=highest_bid.user)
    else:
        listing.status = Listing.Status.VOID
        listing.save(update_fields=["status", "updated_at"])
        republish_listing(listing=listing)

    return listing


@transaction.atomic
def buy_now_purchase(*, user, listing: Listing):
    """
    Immediately purchase a listing at its buy_now_price, bypassing the auction.

    Rules:
    1. User must be eligible to bid (can_bid).
    2. Buy Now must be available on the listing (is_buy_now_available).
    3. Seller cannot buy their own listing.

    Creates an Order at the buy_now_price, closes the listing, and sends
    the standard winner/seller email notifications.
    """
    from orders.models import Order
    from orders.emails import send_auction_emails

    if not user.can_bid:
        raise PermissionDenied(
            _("Your account is not eligible to make purchases. "
              "Please ensure your profile is complete and your account is validated.")
        )

    if not listing.is_buy_now_available:
        raise ValidationError(
            _("Buy Now is not available for this listing.")
        )

    if listing.seller_id == user.pk:
        raise ValidationError(_("You cannot purchase your own listing."))

    order = Order.objects.create(
        buyer=user,
        listing=listing,
        winning_bid_amount=listing.buy_now_price,
        shipping_address=user.address,
    )

    listing.status = Listing.Status.CLOSED
    listing.save(update_fields=["status", "updated_at"])

    send_auction_emails(order=order)

    return order


@transaction.atomic
def republish_listing(*, listing: Listing) -> Listing:
    """
    Duplicate a VOID listing as a new PENDING listing.
    Preserves seller, pricing, and category; resets timing to now + 7 days.
    """
    new_end = timezone.now() + timezone.timedelta(days=7)

    new_listing = Listing.objects.create(
        seller=listing.seller,
        title=listing.title,
        description=listing.description,
        category=listing.category,
        min_public_price=listing.min_public_price,
        max_public_price=listing.max_public_price,
        secret_reserve_price=listing.secret_reserve_price,
        start_time=timezone.now(),
        end_time=new_end,
        sku=listing.sku,
        brand=listing.brand,
        weight=listing.weight,
        dimensions=listing.dimensions,
        tags=listing.tags,
        status=Listing.Status.REPUBLISHED,
        original_listing=listing,
    )
    for img in listing.images.all():
        ListingImage.objects.create(
            listing=new_listing,
            image=img.image,
            order=img.order,
            is_primary=img.is_primary,
        )
    return new_listing


def add_to_watchlist(*, user, listing: Listing) -> Watchlist:
    """Add a listing to a user's watchlist. Idempotent: safe to call twice."""
    entry, _ = Watchlist.objects.get_or_create(user=user, listing=listing)
    return entry


def remove_from_watchlist(*, user, listing: Listing) -> None:
    """Remove a listing from a user's watchlist. No-op if not present."""
    Watchlist.objects.filter(user=user, listing=listing).delete()


@transaction.atomic
def bulk_upload_listings(*, seller: "User", csv_file: IO) -> dict:
    """
    Parse a CSV file and bulk-create listings.

    Expected CSV columns:
        title, description, category_slug, min_price, max_price,
        reserve_price, start_time, end_time

    Returns a dict with 'created', 'errors' counts and list of error rows.
    """
    if not seller.is_seller:
        raise PermissionDenied(_("Only sellers can upload listings."))

    reader = csv.DictReader(io.TextIOWrapper(csv_file, encoding="utf-8"))
    created_count = 0
    errors = []

    for row_num, row in enumerate(reader, start=2):  # row 1 = headers
        try:
            category = Category.objects.get(slug=row["category_slug"].strip())
            listing = create_listing(
                seller=seller,
                title=row["title"].strip(),
                description=row["description"].strip(),
                category=category,
                min_public_price=Decimal(row["min_price"].strip()),
                max_public_price=Decimal(row["max_price"].strip()),
                secret_reserve_price=Decimal(row["reserve_price"].strip()),
                start_time=row["start_time"].strip(),
                end_time=row["end_time"].strip(),
            )
            created_count += 1
        except (KeyError, Category.DoesNotExist, InvalidOperation, ValidationError) as exc:
            errors.append({"row": row_num, "data": row, "error": str(exc)})

    return {"created": created_count, "errors": errors}


@transaction.atomic
def create_review(*, listing: Listing, user: "User", rating: int, comment: str = "") -> Review:
    """Submit a buyer review for a listing. One review per user per listing."""
    if Review.objects.filter(listing=listing, user=user).exists():
        raise ValidationError(_("You have already reviewed this listing."))
    return Review.objects.create(
        listing=listing,
        user=user,
        rating=rating,
        comment=comment,
    )
