import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("listings", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="listing",
            name="image",
        ),
        migrations.CreateModel(
            name="ListingImage",
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
                    "image",
                    models.ImageField(
                        upload_to="listings/%Y/%m/", verbose_name="image"
                    ),
                ),
                (
                    "order",
                    models.PositiveSmallIntegerField(default=0, verbose_name="order"),
                ),
                (
                    "is_primary",
                    models.BooleanField(default=False, verbose_name="primary"),
                ),
                (
                    "listing",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="images",
                        to="listings.listing",
                        verbose_name="listing",
                    ),
                ),
            ],
            options={
                "verbose_name": "listing image",
                "verbose_name_plural": "listing images",
                "ordering": ["order", "id"],
            },
        ),
    ]
