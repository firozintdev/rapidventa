"""
core/management/commands/close_auctions.py

Management command to close expired auctions.

Usage:
    python manage.py close_auctions            # dry-run safe, logs output
    python manage.py close_auctions --dry-run  # inspect without committing

Schedule with cron (every 5 minutes):
    */5 * * * * /path/to/venv/bin/python /path/to/manage.py close_auctions

Or with Celery Beat (preferred for production):
    See rapidventa/celery.py for task registration.
"""

import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from listings.models import Listing
from listings.services import close_listing

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Close all ACTIVE auctions that have passed their end_time."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Simulate the run without committing any changes.",
        )

    def handle(self, *args, **options):
        dry_run: bool = options["dry_run"]
        now = timezone.now()

        expired_listings = Listing.objects.filter(
            status=Listing.Status.ACTIVE,
            end_time__lt=now,
        ).select_related("seller").prefetch_related("bids")

        count = expired_listings.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS("No expired auctions to process."))
            return

        self.stdout.write(
            self.style.WARNING(
                f"Found {count} expired auction(s) to process"
                + (" [DRY RUN – no changes will be saved]" if dry_run else "") + "."
            )
        )

        closed_count = 0
        voided_count = 0
        error_count = 0

        for listing in expired_listings:
            highest_bid = listing.bids.order_by("-amount").first()
            reserve_met = (
                highest_bid is not None
                and highest_bid.amount >= listing.secret_reserve_price
            )

            outcome = "CLOSED (sold)" if reserve_met else "VOID (reserve not met)"

            if dry_run:
                self.stdout.write(
                    f"  [DRY RUN] #{listing.pk} "{listing.title}" → {outcome}"
                )
                if reserve_met:
                    closed_count += 1
                else:
                    voided_count += 1
                continue

            try:
                with transaction.atomic():
                    updated = close_listing(listing=listing)
                    if updated.status == Listing.Status.CLOSED:
                        closed_count += 1
                        self.stdout.write(
                            self.style.SUCCESS(
                                f"  ✓ #{listing.pk} "{listing.title}" → CLOSED"
                                f" (winning bid: ${highest_bid.amount})"
                            )
                        )
                    else:
                        voided_count += 1
                        self.stdout.write(
                            self.style.WARNING(
                                f"  ⚠ #{listing.pk} "{listing.title}" → VOID"
                                f" (republished as new listing)"
                            )
                        )
            except Exception as exc:
                error_count += 1
                logger.exception(
                    "Failed to close listing #%s: %s", listing.pk, exc
                )
                self.stderr.write(
                    self.style.ERROR(
                        f"  ✗ #{listing.pk} "{listing.title}" → ERROR: {exc}"
                    )
                )

        # ── Summary ───────────────────────────────────────────────────────────
        self.stdout.write("\n" + "─" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Closed: {closed_count} | "
                f"Voided: {voided_count} | "
                f"Errors: {error_count}"
                + (" [DRY RUN]" if dry_run else "")
            )
        )
