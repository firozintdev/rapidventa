"""
accounts/signals.py
Post-registration signals (e.g., welcome email, audit log).
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def notify_user_registered(sender, instance, created, **kwargs):
    """
    Triggered when a new user registers.
    Extend this to send a welcome email or create a default profile.
    """
    if created:
        # TODO: Send welcome email via Django's send_mail
        # send_welcome_email(user=instance)
        pass
