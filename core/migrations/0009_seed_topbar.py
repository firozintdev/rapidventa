from django.db import migrations


def seed(apps, schema_editor):
    TopbarSection = apps.get_model("core", "TopbarSection")
    TopbarSection.objects.get_or_create(
        pk=1,
        defaults=dict(
            email="info@rapidventa.com",
            support_url="https://wa.me/+584122392711",
            support_label="Customer support",
            btn_how_to_bid="HOW TO BID",
            btn_sell="SELL YOUR ITEM",
            language_label="Language",
        ),
    )


def unseed(apps, schema_editor):
    apps.get_model("core", "TopbarSection").objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_topbar"),
    ]

    operations = [
        migrations.RunPython(seed, reverse_code=unseed),
    ]
