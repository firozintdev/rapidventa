from django.apps import AppConfig


class BidsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bids"
    verbose_name = "Bids"

    def ready(self):
        import bids.signals  # noqa: F401
