"""
bids/models.py
Bid model – each row is one bid placed by a user on a listing.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Bid(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="bids",
        verbose_name=_("bidder"),
    )
    listing = models.ForeignKey(
        "listings.Listing",
        on_delete=models.CASCADE,
        related_name="bids",
        verbose_name=_("listing"),
    )
    amount = models.DecimalField(_("bid amount"), max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(_("placed at"), auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = _("bid")
        verbose_name_plural = _("bids")
        ordering = ["-amount"]
        # Ensure a user cannot submit the exact same amount twice on the same listing
        unique_together = [("user", "listing", "amount")]

    def __str__(self) -> str:
        return f"{self.user.full_name} → {self.listing.title}: ${self.amount}"
