"""
bids/signals.py
Post-bid signals – e.g., notify outbid users.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from .emails import send_outbid_email
from .models import Bid


@receiver(post_save, sender=Bid)
def notify_outbid_users(sender, instance, created, **kwargs):
    """
    When a new bid is placed, notify any previously highest bidder
    that they have been outbid.
    """
    if created:
        previous_top = (
            Bid.objects.filter(listing=instance.listing)
            .exclude(pk=instance.pk)
            .order_by("-amount")
            .first()
        )
        if previous_top and previous_top.user != instance.user:
            send_outbid_email(
                user=previous_top.user,
                listing=instance.listing,
                new_amount=instance.amount,
            )
