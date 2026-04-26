from django.db import migrations


def seed(apps, schema_editor):
    FooterSection = apps.get_model("core", "FooterSection")
    FooterSection.objects.get_or_create(
        pk=1,
        defaults=dict(
            tagline="The fast, transparent online auction house. Bid smart, win big.",
            whatsapp_url="https://wa.me/+584122392711",
            facebook_url="#",
            instagram_url="#",
            twitter_url="#",
            step_1="Register & get validated",
            step_2="Browse live auctions",
            step_3="Place your highest bid",
            step_4="Win & complete the order",
            copyright_name="RapidVenta",
            bottom_text="Built with love using Django 5.2",
        ),
    )


def unseed(apps, schema_editor):
    apps.get_model("core", "FooterSection").objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_footer"),
    ]

    operations = [
        migrations.RunPython(seed, reverse_code=unseed),
    ]
