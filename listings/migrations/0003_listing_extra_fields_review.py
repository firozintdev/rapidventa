import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0002_remove_listing_image_listingimage"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        # ── Additional Info fields on Listing ────────────────────────────────
        migrations.AddField(
            model_name="listing",
            name="sku",
            field=models.CharField(blank=True, max_length=100, verbose_name="SKU"),
        ),
        migrations.AddField(
            model_name="listing",
            name="brand",
            field=models.CharField(blank=True, max_length=100, verbose_name="brand"),
        ),
        migrations.AddField(
            model_name="listing",
            name="weight",
            field=models.CharField(
                blank=True,
                help_text="e.g. 2.5 kg",
                max_length=50,
                verbose_name="weight",
            ),
        ),
        migrations.AddField(
            model_name="listing",
            name="dimensions",
            field=models.CharField(
                blank=True,
                help_text="e.g. 30 × 20 × 10 cm",
                max_length=100,
                verbose_name="dimensions",
            ),
        ),
        migrations.AddField(
            model_name="listing",
            name="tags",
            field=models.CharField(
                blank=True,
                help_text="Comma-separated tags",
                max_length=255,
                verbose_name="tags",
            ),
        ),
        # ── Review model ─────────────────────────────────────────────────────
        migrations.CreateModel(
            name="Review",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "rating",
                    models.PositiveSmallIntegerField(
                        choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                        verbose_name="rating",
                    ),
                ),
                ("comment", models.TextField(blank=True, verbose_name="comment")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to="listings.listing",
                        verbose_name="listing",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="reviews",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
            ],
            options={
                "verbose_name": "review",
                "verbose_name_plural": "reviews",
                "ordering": ["-created_at"],
            },
        ),
        migrations.AddConstraint(
            model_name="review",
            constraint=models.UniqueConstraint(
                fields=["listing", "user"], name="unique_listing_review"
            ),
        ),
    ]
