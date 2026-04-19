"""
orders/models.py
Order model – created when a closed auction's reserve price is met.
No payment processing; pure status tracking.
"""

import uuid
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Order(models.Model):

    class Status(models.TextChoices):
        PENDING_PAYMENT = "PENDING_PAYMENT", _("Pending Payment")
        PAID = "PAID", _("Paid")
        SHIPPED = "SHIPPED", _("Shipped")
        COMPLETED = "COMPLETED", _("Completed")
        CANCELLED = "CANCELLED", _("Cancelled")

    # ── Reference ─────────────────────────────────────────────────────────────
    reference = models.UUIDField(
        _("order reference"),
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )

    # ── Relations ─────────────────────────────────────────────────────────────
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="orders",
        verbose_name=_("buyer"),
    )
    listing = models.OneToOneField(
        "listings.Listing",
        on_delete=models.PROTECT,
        related_name="order",
        verbose_name=_("listing"),
    )

    # ── Status ────────────────────────────────────────────────────────────────
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_PAYMENT,
        db_index=True,
    )

    # ── Financial snapshot ────────────────────────────────────────────────────
    winning_bid_amount = models.DecimalField(
        _("winning bid amount"),
        max_digits=12,
        decimal_places=2,
    )

    # ── Shipping ──────────────────────────────────────────────────────────────
    tracking_number = models.CharField(
        _("tracking number"),
        max_length=100,
        blank=True,
    )
    shipping_address = models.TextField(_("shipping address"), blank=True)
    notes = models.TextField(_("notes"), blank=True)

    # ── Audit ─────────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("order")
        verbose_name_plural = _("orders")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Order {self.reference} – {self.listing.title}"

    def get_absolute_url(self):
        return reverse("orders:detail", kwargs={"reference": self.reference})

    @property
    def short_reference(self) -> str:
        return str(self.reference).split("-")[0].upper()
