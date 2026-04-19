"""
orders/services.py
Business logic for order creation and status transitions.
"""

from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .emails import send_auction_emails
from .models import Order


@transaction.atomic
def create_order_from_listing(*, listing, winner) -> Order:
    """
    Called by listings.services.close_listing when reserve is met.
    Creates an Order snapshotting the winning bid amount.
    """
    highest_bid = listing.bids.order_by("-amount").first()
    if not highest_bid:
        raise ValidationError(_("Cannot create order: no bids found."))

    order = Order.objects.create(
        buyer=winner,
        listing=listing,
        winning_bid_amount=highest_bid.amount,
        shipping_address=winner.address,
    )

    send_auction_emails(order=order)
    return order


@transaction.atomic
def advance_order_status(*, order: Order, advanced_by, tracking_number: str = "") -> Order:
    """
    Move an order to the next logical status.
    Only staff can advance status beyond PENDING_PAYMENT.
    """
    transitions = {
        Order.Status.PENDING_PAYMENT: Order.Status.PAID,
        Order.Status.PAID: Order.Status.SHIPPED,
        Order.Status.SHIPPED: Order.Status.COMPLETED,
    }

    if order.status not in transitions:
        raise ValidationError(
            _("Order status '%(status)s' cannot be advanced further.")
            % {"status": order.get_status_display()}
        )

    if not advanced_by.is_staff:
        raise PermissionDenied(_("Only staff can advance order status."))

    order.status = transitions[order.status]
    if tracking_number:
        order.tracking_number = tracking_number
    order.save(update_fields=["status", "tracking_number", "updated_at"])
    return order


@transaction.atomic
def cancel_order(*, order: Order, cancelled_by) -> Order:
    """Cancel an order that has not yet shipped."""
    if order.status in (Order.Status.SHIPPED, Order.Status.COMPLETED):
        raise ValidationError(_("Cannot cancel a shipped or completed order."))

    if not cancelled_by.is_staff:
        raise PermissionDenied(_("Only staff can cancel orders."))

    order.status = Order.Status.CANCELLED
    order.save(update_fields=["status", "updated_at"])
    return order


@transaction.atomic
def update_tracking(*, order: Order, tracking_number: str, updated_by) -> Order:
    """Add or update the shipment tracking number."""
    if not updated_by.is_staff:
        raise PermissionDenied(_("Only staff can update tracking numbers."))

    order.tracking_number = tracking_number
    order.save(update_fields=["tracking_number", "updated_at"])
    return order
