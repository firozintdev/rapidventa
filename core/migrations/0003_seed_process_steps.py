from django.db import migrations

STEPS = [
    (1, "bi-person-plus-fill", "Registration",   "Create your free account", "Verify your identity",    "Get validated by admin"),
    (2, "bi-search",           "Select Product", "Search your auction",      "Find the right product",  "Choose your final lot"),
    (3, "bi-hammer",           "Go to Bidding",  "Choose the bid product",   "Bid within your budget",  "Watch the live countdown"),
    (4, "bi-bag-check-fill",   "Make Payment",   "Confirm your winning bid", "Complete secure payment", "Receive your item"),
]


def seed(apps, schema_editor):
    HowItWorksSection = apps.get_model("core", "HowItWorksSection")
    ProcessStep = apps.get_model("core", "ProcessStep")
    section, _ = HowItWorksSection.objects.get_or_create(pk=1)
    for order, icon, title, i1, i2, i3 in STEPS:
        ProcessStep.objects.get_or_create(
            section=section, order=order,
            defaults=dict(icon=icon, title=title, item_1=i1, item_2=i2, item_3=i3),
        )


def unseed(apps, schema_editor):
    apps.get_model("core", "ProcessStep").objects.all().delete()
    apps.get_model("core", "HowItWorksSection").objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_how_it_works"),
    ]

    operations = [
        migrations.RunPython(seed, reverse_code=unseed),
    ]
