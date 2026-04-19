"""
core/tasks.py
Celery tasks for scheduled background work.
"""

import logging

from celery import shared_task
from django.db import transaction
from django.utils import timezone

from listings.models import Listing
from listings.services import close_listing

logger = logging.getLogger(__name__)


@shared_task(name="core.tasks.close_auctions_task")
def close_auctions_task() -> dict:
    """
    Celery counterpart to the ``close_auctions`` management command.

    Queries for every ACTIVE listing whose end_time has passed and calls
    ``close_listing()`` on each one inside its own atomic block so that a
    single failure does not roll back the other listings.

    Returns a summary dict so the result can be inspected in Flower / the
    Celery result backend.
    """
    now = timezone.now()

    expired = (
        Listing.objects.filter(status=Listing.Status.ACTIVE, end_time__lt=now)
        .select_related("seller")
        .prefetch_related("bids")
    )

    total = expired.count()
    if total == 0:
        logger.info("close_auctions_task: no expired auctions to process.")
        return {"closed": 0, "voided": 0, "errors": 0}

    logger.info("close_auctions_task: processing %d expired auction(s).", total)

    closed_count = 0
    voided_count = 0
    error_count = 0

    for listing in expired:
        try:
            with transaction.atomic():
                updated = close_listing(listing=listing)

            if updated.status == Listing.Status.CLOSED:
                closed_count += 1
                logger.info(
                    "Listing #%s '%s' → CLOSED.", listing.pk, listing.title
                )
            else:
                voided_count += 1
                logger.info(
                    "Listing #%s '%s' → VOID (republished as new listing).",
                    listing.pk,
                    listing.title,
                )
        except Exception:
            error_count += 1
            logger.exception(
                "Failed to close listing #%s '%s'.", listing.pk, listing.title
            )

    result = {"closed": closed_count, "voided": voided_count, "errors": error_count}
    logger.info(
        "close_auctions_task complete — closed: %d | voided: %d | errors: %d.",
        closed_count,
        voided_count,
        error_count,
    )
    return result
