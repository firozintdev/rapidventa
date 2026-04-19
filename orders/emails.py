"""
orders/emails.py
Email notifications sent when an auction order is created.
"""

import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_auction_emails(*, order) -> None:
    """
    Send two emails after an auction closes with a winning bid:
      1. To the buyer (winner): congratulations notice.
      2. To the seller: item-sold notice.

    Both calls are best-effort; failures are logged but not re-raised so
    they do not roll back the surrounding transaction.
    """
    listing = order.listing
    winner = order.buyer
    seller = listing.seller
    amount = order.winning_bid_amount
    title = listing.title
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@rapidventa.com")

    # ── Winner email ──────────────────────────────────────────────────────────
    winner_subject = "Congratulations! You won the auction"
    winner_body = (
        f"Dear {winner.full_name},\n\n"
        f"Congratulations! You won the auction for \"{title}\" "
        f"with a winning bid of ${amount}.\n\n"
        f"To arrange payment and delivery, please contact the auction house "
        f"by replying to this email or reaching out to our support team.\n\n"
        f"Thank you for participating in RapidVenta!\n\n"
        f"The RapidVenta Team"
    )
    try:
        send_mail(
            subject=winner_subject,
            message=winner_body,
            from_email=from_email,
            recipient_list=[winner.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send winner email for order %s to %s",
            order.pk,
            winner.email,
        )

    # ── Seller email ──────────────────────────────────────────────────────────
    seller_subject = f"Your item \"{title}\" has been sold!"
    seller_body = (
        f"Dear {seller.full_name},\n\n"
        f"Great news! Your listing \"{title}\" has been sold "
        f"for ${amount}.\n\n"
        f"The auction house will be in touch to coordinate the next steps "
        f"for payment collection and item delivery.\n\n"
        f"Thank you for listing with RapidVenta!\n\n"
        f"The RapidVenta Team"
    )
    try:
        send_mail(
            subject=seller_subject,
            message=seller_body,
            from_email=from_email,
            recipient_list=[seller.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception(
            "Failed to send seller email for order %s to %s",
            order.pk,
            seller.email,
        )
