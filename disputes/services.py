"""
disputes/services.py
Mutation helpers for disputes. All business rules live here.
"""

from django.core.exceptions import PermissionDenied, ValidationError
from django.utils.translation import gettext_lazy as _

from orders.models import Order


def raise_dispute(*, order: Order, user, reason: str):
    """
    Open a new dispute on a completed order.

    Rules:
    - Only the buyer of the order may raise a dispute.
    - The order must be in COMPLETED status.
    - Only one dispute per order is allowed.
    """
    from .models import Dispute

    if order.buyer != user:
        raise PermissionDenied(_("Only the buyer of this order can raise a dispute."))

    if order.status != Order.Status.COMPLETED:
        raise ValidationError(_("Disputes can only be raised on completed orders."))

    if Dispute.objects.filter(order=order).exists():
        raise ValidationError(_("A dispute has already been raised for this order."))

    return Dispute.objects.create(order=order, raised_by=user, reason=reason.strip())


def resolve_dispute(*, dispute, resolved_by, notes: str):
    """
    Mark a dispute as RESOLVED and record staff resolution notes.
    Only staff members may resolve disputes.
    """
    from .models import Dispute

    if not resolved_by.is_staff:
        raise PermissionDenied(_("Only staff members can resolve disputes."))

    if not dispute.is_open:
        raise ValidationError(_("This dispute is already closed or resolved."))

    dispute.status = Dispute.Status.RESOLVED
    dispute.resolution_notes = notes.strip()
    dispute.save(update_fields=["status", "resolution_notes", "updated_at"])
    return dispute
