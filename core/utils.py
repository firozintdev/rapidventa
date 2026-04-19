"""
core/utils.py
Shared utility functions used across multiple apps.
"""

import re
from django.utils import timezone


def humanize_timedelta(td) -> str:
    """Convert a timedelta into a human-readable string: '2d 4h 30m'."""
    if td is None or td.total_seconds() <= 0:
        return "Ended"

    total_seconds = int(td.total_seconds())
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes or not parts:
        parts.append(f"{minutes}m")

    return " ".join(parts)


def slugify_unique(model_class, value: str, slug_field: str = "slug") -> str:
    """
    Generate a unique slug for a model instance.
    Appends a numeric suffix if the slug already exists.
    """
    from django.utils.text import slugify

    base_slug = slugify(value)
    slug = base_slug
    counter = 1
    while model_class.objects.filter(**{slug_field: slug}).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug
