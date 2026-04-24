from .models import Category


def nav_categories(request):
    """Inject root categories with prefetched children into every template."""
    categories = (
        Category.objects.filter(parent__isnull=True)
        .prefetch_related("children")
        .order_by("order", "name")
    )
    return {"nav_categories": categories}
