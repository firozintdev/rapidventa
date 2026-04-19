"""
orders/selectors.py
Read-only query helpers for orders.
"""

from django.db.models import QuerySet
from .models import Order


def get_orders_by_buyer(*, buyer) -> QuerySet:
    return (
        Order.objects.filter(buyer=buyer)
        .select_related("listing__category", "listing__seller")
        .order_by("-created_at")
    )


def get_order_by_reference(*, reference) -> "Order | None":
    return (
        Order.objects.filter(reference=reference)
        .select_related("buyer", "listing__category", "listing__seller")
        .first()
    )


def get_all_orders() -> QuerySet:
    return Order.objects.select_related(
        "buyer", "listing__category", "listing__seller"
    ).order_by("-created_at")
