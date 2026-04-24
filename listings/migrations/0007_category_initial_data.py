from django.db import migrations
from django.utils.text import slugify


CATEGORY_TREE = [
    ("Art", 1, [
        ("National", 1),
        ("International", 2),
        ("Antique", 3),
    ]),
    ("Antiques & Collectibles", 2, [
        ("Furniture", 1),
        ("Books", 2),
        ("Military", 3),
        ("Posters", 4),
        ("Antiques / Advertising", 5),
        ("Decorative", 6),
    ]),
    ("Numismatics & Philately", 3, [
        ("Coins", 1),
        ("Banknotes", 2),
        ("Medals", 3),
        ("General", 4),
    ]),
    ("Sports", 4, [
        ("Cards", 1),
        ("Autographs", 2),
        ("Memorabilia", 3),
        ("General", 4),
    ]),
]


def _child_slug(parent_name, child_name):
    return f"{slugify(parent_name)}-{slugify(child_name)}"


def seed_categories(apps, schema_editor):
    Category = apps.get_model("listings", "Category")
    # Remove listings first to avoid PROTECT constraint on category FK
    Listing = apps.get_model("listings", "Listing")
    Listing.objects.all().delete()
    Category.objects.all().delete()

    for parent_name, parent_order, children in CATEGORY_TREE:
        parent = Category.objects.create(
            name=parent_name,
            slug=slugify(parent_name),
            order=parent_order,
            parent=None,
        )
        for child_name, child_order in children:
            Category.objects.create(
                name=child_name,
                slug=_child_slug(parent_name, child_name),
                order=child_order,
                parent=parent,
            )


def unseed_categories(apps, schema_editor):
    apps.get_model("listings", "Category").objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0006_category_hierarchy"),
    ]

    operations = [
        migrations.RunPython(seed_categories, reverse_code=unseed_categories),
    ]
