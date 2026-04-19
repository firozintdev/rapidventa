"""
listings/emails.py
Email notifications for listing status transitions.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def _send(*, subject: str, body: str, recipient_email: str, listing_pk) -> None:
    """Shared send helper — logs failures without re-raising."""
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@rapidventa.com")
    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[recipient_email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send '%s' email to %s for listing %s",
            subject,
            recipient_email,
            listing_pk,
        )


def send_listing_approved_email(listing) -> None:
    """
    Notify the seller that their listing has been approved and is now live.
    """
    site_url = getattr(settings, "SITE_URL", "http://localhost:8000").rstrip("/")
    listing_url = f"{site_url}{listing.get_absolute_url()}"
    seller = listing.seller

    body = (
        f"Hi {seller.full_name},\n\n"
        f"Great news! Your listing \"{listing.title}\" has been reviewed "
        f"and approved by our team. It is now live on RapidVenta and open "
        f"for bidding.\n\n"
        f"View your listing:\n"
        f"{listing_url}\n\n"
        f"Good luck with your auction!\n\n"
        f"The RapidVenta Team"
    )

    _send(
        subject="Your listing has been approved",
        body=body,
        recipient_email=seller.email,
        listing_pk=listing.pk,
    )


def send_listing_rejected_email(listing) -> None:
    """
    Notify the seller that their listing was not approved and has been
    returned to DRAFT so they can edit and resubmit.
    """
    seller = listing.seller

    body = (
        f"Hi {seller.full_name},\n\n"
        f"Thank you for submitting \"{listing.title}\" for review. "
        f"Unfortunately, our team was unable to approve your listing at "
        f"this time.\n\n"
        f"Your listing has been returned to Draft status. Please review "
        f"the item details, make any necessary corrections, and resubmit "
        f"it for approval.\n\n"
        f"If you have questions about why your listing was not approved, "
        f"please contact our support team by replying to this email.\n\n"
        f"The RapidVenta Team"
    )

    _send(
        subject="Your listing was not approved",
        body=body,
        recipient_email=seller.email,
        listing_pk=listing.pk,
    )
