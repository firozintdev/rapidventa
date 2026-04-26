"""
Usage:
    python manage.py seed_categories            # insert missing categories only
    python manage.py seed_categories --reset    # delete all & re-insert
"""

from django.core.management.base import BaseCommand
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


class Command(BaseCommand):
    help = "Seed the canonical category tree into the database."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete ALL existing categories (and orphaned listings) before seeding.",
        )

    def handle(self, *args, **options):
        from listings.models import Category

        if options["reset"]:
            deleted, _ = Category.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing categories."))

        created_parents = 0
        created_children = 0
        skipped = 0

        for parent_name, parent_order, children in CATEGORY_TREE:
            parent_slug = slugify(parent_name)
            parent, p_created = Category.objects.get_or_create(
                slug=parent_slug,
                defaults={
                    "name": parent_name,
                    "order": parent_order,
                    "parent": None,
                },
            )
            if p_created:
                created_parents += 1
                self.stdout.write(f"  + {parent_name}")
            else:
                skipped += 1
                self.stdout.write(f"  = {parent_name} (already exists)")

            for child_name, child_order in children:
                child_slug = _child_slug(parent_name, child_name)
                child, c_created = Category.objects.get_or_create(
                    slug=child_slug,
                    defaults={
                        "name": child_name,
                        "order": child_order,
                        "parent": parent,
                    },
                )
                if c_created:
                    created_children += 1
                    self.stdout.write(f"      + {child_name}")
                else:
                    skipped += 1
                    self.stdout.write(f"      = {child_name} (already exists)")

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created {created_parents} parent(s), "
                f"{created_children} subcategorie(s). "
                f"{skipped} skipped (already existed)."
            )
        )
