"""
listings/models.py
Category, Listing (auction), ListingImage, and Review models.
"""

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from .managers import ListingManager


class Category(models.Model):
    name = models.CharField(_("name"), max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(_("description"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("category")
        verbose_name_plural = _("categories")
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Listing(models.Model):
    """Represents a single auction listing."""

    class Status(models.TextChoices):
        DRAFT = "DRAFT", _("Draft")
        PENDING = "PENDING", _("Pending Approval")
        ACTIVE = "ACTIVE", _("Active")
        CLOSED = "CLOSED", _("Closed – Sold")
        VOID = "VOID", _("Void – Reserve Not Met")
        REPUBLISHED = "REPUBLISHED", _("Republished")

    # ── Core Fields ───────────────────────────────────────────────────────────
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"))
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="listings",
        verbose_name=_("category"),
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="listings",
        verbose_name=_("seller"),
        limit_choices_to={"role": "SELLER"},
    )

    # ── Pricing ───────────────────────────────────────────────────────────────
    min_public_price = models.DecimalField(
        _("minimum public price"), max_digits=12, decimal_places=2
    )
    max_public_price = models.DecimalField(
        _("maximum public price"), max_digits=12, decimal_places=2
    )
    secret_reserve_price = models.DecimalField(
        _("secret reserve price"),
        max_digits=12,
        decimal_places=2,
        help_text=_("Auction is VOID if highest bid falls below this."),
    )
    buy_now_price = models.DecimalField(
        _("buy now price"),
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Optional. Buyers can skip the auction and purchase immediately at this price."),
    )

    # ── Timing ────────────────────────────────────────────────────────────────
    start_time = models.DateTimeField(_("start time"))
    end_time = models.DateTimeField(_("end time"))

    # ── Status ────────────────────────────────────────────────────────────────
    status = models.CharField(
        _("status"),
        max_length=15,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
    )

    # ── Additional Info (optional) ────────────────────────────────────────────
    sku = models.CharField(_("SKU"), max_length=100, blank=True)
    brand = models.CharField(_("brand"), max_length=100, blank=True)
    weight = models.CharField(
        _("weight"), max_length=50, blank=True, help_text=_("e.g. 2.5 kg")
    )
    dimensions = models.CharField(
        _("dimensions"), max_length=100, blank=True, help_text=_("e.g. 30 × 20 × 10 cm")
    )
    tags = models.CharField(
        _("tags"), max_length=255, blank=True, help_text=_("Comma-separated tags")
    )

    # ── Audit ─────────────────────────────────────────────────────────────────
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # ── Optional back-reference when republished ──────────────────────────────
    original_listing = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="republications",
        verbose_name=_("original listing"),
    )

    objects = ListingManager()

    class Meta:
        verbose_name = _("listing")
        verbose_name_plural = _("listings")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse("listings:detail", kwargs={"pk": self.pk})

    # ── Computed properties ───────────────────────────────────────────────────
    @property
    def is_active(self) -> bool:
        now = timezone.now()
        return (
            self.status == self.Status.ACTIVE
            and self.start_time <= now <= self.end_time
        )

    @property
    def is_buy_now_available(self) -> bool:
        """True when a buy-now price is set and the auction is currently ACTIVE."""
        return bool(self.buy_now_price) and self.is_active

    @property
    def time_remaining(self):
        """Timedelta until end, or None if expired."""
        if self.end_time > timezone.now():
            return self.end_time - timezone.now()
        return None

    @property
    def current_highest_bid(self):
        return self.bids.order_by("-amount").first()

    @property
    def current_price(self):
        top_bid = self.current_highest_bid
        return top_bid.amount if top_bid else self.min_public_price

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def tags_list(self):
        """Return a cleaned list of individual tag strings."""
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class ListingImage(models.Model):
    """An image attached to a listing. First image (order=0) is the primary."""

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name=_("listing"),
    )
    image = models.ImageField(_("image"), upload_to="listings/%Y/%m/")
    order = models.PositiveSmallIntegerField(_("order"), default=0)
    is_primary = models.BooleanField(_("primary"), default=False)

    class Meta:
        verbose_name = _("listing image")
        verbose_name_plural = _("listing images")
        ordering = ["order", "id"]

    def __str__(self) -> str:
        return f"Image {self.order} – {self.listing.title}"


class Watchlist(models.Model):
    """A user's saved watch on a listing."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="watchlist_entries",
        verbose_name=_("user"),
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="watchers",
        verbose_name=_("listing"),
    )
    added_at = models.DateTimeField(_("added at"), auto_now_add=True)

    class Meta:
        verbose_name = _("watchlist entry")
        verbose_name_plural = _("watchlist entries")
        unique_together = [("user", "listing")]
        ordering = ["-added_at"]

    def __str__(self) -> str:
        return f"{self.user.full_name} watches {self.listing.title}"


class Review(models.Model):
    """Buyer review for a listing."""

    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("listing"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name=_("user"),
    )
    rating = models.PositiveSmallIntegerField(
        _("rating"),
        choices=RATING_CHOICES,
    )
    comment = models.TextField(_("comment"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("review")
        verbose_name_plural = _("reviews")
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "user"], name="unique_listing_review"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} – {self.listing} ({self.rating}★)"
