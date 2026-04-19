"""
listings/managers.py
Custom queryset/manager for Listing model.
"""

from django.db import models
from django.utils import timezone


class ListingQuerySet(models.QuerySet):
    def active(self):
        now = timezone.now()
        return self.filter(
            status="ACTIVE",
            start_time__lte=now,
            end_time__gte=now,
        )

    def pending(self):
        return self.filter(status="PENDING")

    def ended_unclosed(self):
        """Active auctions past their end_time not yet processed."""
        return self.filter(status="ACTIVE", end_time__lt=timezone.now())

    def by_category(self, category_slug: str):
        return self.filter(category__slug=category_slug)

    def by_seller(self, seller):
        return self.filter(seller=seller)


class ListingManager(models.Manager):
    def get_queryset(self):
        return ListingQuerySet(self.model, using=self._db)

    def active(self):
        return self.get_queryset().active()

    def pending(self):
        return self.get_queryset().pending()

    def ended_unclosed(self):
        return self.get_queryset().ended_unclosed()

    def by_seller(self, seller):
        return self.get_queryset().by_seller(seller)
