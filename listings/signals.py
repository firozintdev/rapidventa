"""
listings/signals.py
Signals fired on Listing status transitions.
"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .emails import send_listing_approved_email, send_listing_rejected_email
from .models import Listing


@receiver(pre_save, sender=Listing)
def _snapshot_listing_status(sender, instance, **kwargs):
    """
    Cache the current DB status onto the instance before it is overwritten,
    so that post_save can compare old vs new without an extra query.
    Stores None for new (unsaved) instances.
    """
    if instance.pk:
        instance._previous_status = (
            Listing.objects.filter(pk=instance.pk)
            .values_list("status", flat=True)
            .first()
        )
    else:
        instance._previous_status = None


@receiver(post_save, sender=Listing)
def listing_status_changed(sender, instance, created, **kwargs):
    """
    Send seller notifications when an admin approves or rejects a listing.

    Approval:  PENDING → ACTIVE  → send_listing_approved_email
    Rejection: PENDING → DRAFT   → send_listing_rejected_email

    The PENDING guard prevents spurious emails on unrelated saves (e.g. a
    newly created listing that starts as DRAFT, or a price update on an
    already-active listing).
    """
    if created:
        return

    previous = getattr(instance, "_previous_status", None)
    current = instance.status

    if previous == Listing.Status.PENDING:
        if current == Listing.Status.ACTIVE:
            send_listing_approved_email(instance)
        elif current == Listing.Status.DRAFT:
            send_listing_rejected_email(instance)
