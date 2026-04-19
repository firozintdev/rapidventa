"""
bids/emails.py
Email notifications for bid-related events.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)


def send_outbid_email(*, user, listing, new_amount) -> None:
    """
    Notify *user* that they have been outbid on *listing*.

    Args:
        user: The User instance whose bid is no longer the highest.
        listing: The Listing instance they were bidding on.
        new_amount: The new highest bid amount that surpassed theirs.
    """
    site_url = getattr(settings, "SITE_URL", "http://localhost:8000").rstrip("/")
    listing_path = reverse("listings:detail", kwargs={"pk": listing.pk})
    listing_url = f"{site_url}{listing_path}"

    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@rapidventa.com")
    subject = f"You have been outbid on {listing.title}"
    body = (
        f"Hi {user.full_name},\n\n"
        f"Unfortunately, your bid on \"{listing.title}\" has been surpassed.\n\n"
        f"New highest bid: ${new_amount}\n\n"
        f"You can place a higher bid and get back in the running here:\n"
        f"{listing_url}\n\n"
        f"Good luck!\n\n"
        f"The RapidVenta Team"
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=from_email,
            recipient_list=[user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send outbid email to %s for listing %s",
            user.email,
            listing.pk,
        )
