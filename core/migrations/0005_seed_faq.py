from django.db import migrations

FAQS = [
    (1, "What is an auction?",
     "An auction is a public sale where items are sold to the highest bidder within a set time period. "
     "At RapidVenta, all auctions are live with a countdown timer — the highest bid when the clock hits zero wins."),
    (2, "How do auctions work?",
     "Browse active listings, place your bid above the current price, and watch the live countdown. "
     "If your bid is the highest when the auction ends, you win and proceed to complete the order."),
    (3, "What types of auctions are there?",
     "RapidVenta hosts live timed auctions across many categories including electronics, collectibles, art, "
     "jewelry, real estate, and more. Each listing shows a category badge and countdown timer."),
    (4, "Who can participate in auctions?",
     "Anyone can register for free. After registration, our admin team validates your account, giving you "
     "full access to bid on all live auctions. Sellers also go through a verification process."),
    (5, "What happens if I win an auction?",
     "When you win, you'll receive a notification and can complete your order from your dashboard. "
     "Our team will coordinate payment and delivery. We offer a money-back guarantee if there's any issue."),
]


def seed(apps, schema_editor):
    FaqSection = apps.get_model("core", "FaqSection")
    FaqItem = apps.get_model("core", "FaqItem")
    section, _ = FaqSection.objects.get_or_create(pk=1)
    for order, question, answer in FAQS:
        FaqItem.objects.get_or_create(
            section=section, order=order,
            defaults=dict(question=question, answer=answer),
        )


def unseed(apps, schema_editor):
    apps.get_model("core", "FaqItem").objects.all().delete()
    apps.get_model("core", "FaqSection").objects.filter(pk=1).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_faq"),
    ]

    operations = [
        migrations.RunPython(seed, reverse_code=unseed),
    ]
