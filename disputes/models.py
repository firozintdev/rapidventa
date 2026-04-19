"""
disputes/models.py
Buyer-initiated dispute raised against a completed order.
"""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Dispute(models.Model):

    class Status(models.TextChoices):
        OPEN = "OPEN", _("Open")
        UNDER_REVIEW = "UNDER_REVIEW", _("Under Review")
        RESOLVED = "RESOLVED", _("Resolved")
        CLOSED = "CLOSED", _("Closed")

    # ── Relations ─────────────────────────────────────────────────────────────
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.PROTECT,
        related_name="disputes",
        verbose_name=_("order"),
    )
    raised_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="disputes_raised",
        verbose_name=_("raised by"),
    )

    # ── Content ───────────────────────────────────────────────────────────────
    reason = models.TextField(_("reason"))
    status = models.CharField(
        _("status"),
        max_length=15,
        choices=Status.choices,
        default=Status.OPEN,
        db_index=True,
    )
    resolution_notes = models.TextField(_("resolution notes"), blank=True)

    # ── Audit ─────────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("dispute")
        verbose_name_plural = _("disputes")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Dispute #{self.pk} – Order {self.order.short_reference} [{self.status}]"

    def get_absolute_url(self):
        return reverse("disputes:detail", kwargs={"pk": self.pk})

    @property
    def is_open(self) -> bool:
        return self.status in (self.Status.OPEN, self.Status.UNDER_REVIEW)
