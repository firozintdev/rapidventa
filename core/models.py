"""
core/models.py
Singleton content models editable from Django admin.
"""

from django.db import models


class AboutSection(models.Model):
    """
    Singleton content block for the homepage 'Get In Know' section.
    Only one row is ever stored (pk=1). Use AboutSection.get_solo().
    """

    # ── Title ─────────────────────────────────────────────────────────────────
    title_bold   = models.CharField("Title (bold part)",   max_length=100, default="Get In")
    title_italic = models.CharField("Title (italic part)", max_length=100, default="Know")

    # ── Top image ─────────────────────────────────────────────────────────────
    image = models.ImageField(
        "Top image", upload_to="about/top/", null=True, blank=True,
        help_text="Displayed on the left of the Get In Know section.",
    )

    # ── Description ───────────────────────────────────────────────────────────
    description = models.TextField(
        "Description",
        default=(
            "Welcome to RapidVenta, where digital innovation meets auction "
            "excellence. Discover exclusive items and bid your way to great deals."
        ),
    )

    # ── Feature bullets (up to 5) ─────────────────────────────────────────────
    feature_1 = models.CharField(max_length=200, default="Ready to boost your bidding strategy",        blank=True, verbose_name="Feature 1")
    feature_2 = models.CharField(max_length=200, default="Join our exclusive auction community",         blank=True, verbose_name="Feature 2")
    feature_3 = models.CharField(max_length=200, default="Verified sellers, real products, fair prices", blank=True, verbose_name="Feature 3")
    feature_4 = models.CharField(max_length=200, default="Live countdowns — bid until the last second",  blank=True, verbose_name="Feature 4")
    feature_5 = models.CharField(max_length=200, default="Secure payments and buyer protection",         blank=True, verbose_name="Feature 5")

    # ── Stat labels (numbers come from DB, only text is editable) ─────────────
    stat_auctions_label = models.CharField(max_length=50, default="Auctions",       verbose_name="Auctions label")
    stat_auctions_sub   = models.CharField(max_length=50, default="Live Right Now", verbose_name="Auctions sub-label")
    stat_categories_label = models.CharField(max_length=50, default="Categories",   verbose_name="Categories label")
    stat_categories_sub   = models.CharField(max_length=50, default="To Browse",    verbose_name="Categories sub-label")
    stat_sellers_label  = models.CharField(max_length=50, default="Sellers",        verbose_name="Sellers label")
    stat_sellers_sub    = models.CharField(max_length=50, default="Verified Sellers", verbose_name="Sellers sub-label")

    # ── CTA button ────────────────────────────────────────────────────────────
    cta_text = models.CharField("CTA button text", max_length=100, default="Start Bidding Now")

    # ── Testimonial ───────────────────────────────────────────────────────────
    testimonial_text = models.TextField(
        "Testimonial quote", blank=True,
        default=(
            "RapidVenta transformed how I buy and sell collectibles. "
            "The platform is transparent, fast, and the support team is always available."
        ),
    )
    testimonial_author = models.CharField(
        "Testimonial author", max_length=100, default="A Happy Buyer", blank=True,
    )

    # ── Bottom image ──────────────────────────────────────────────────────────
    bottom_image = models.ImageField(
        "Bottom image", upload_to="about/bottom/", null=True, blank=True,
        help_text="Displayed on the right of the testimonial row.",
    )

    class Meta:
        verbose_name = "About Section"
        verbose_name_plural = "About Section"

    def __str__(self):
        return "Homepage – Get In Know"

    # ── Singleton helpers ─────────────────────────────────────────────────────

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass  # prevent deletion of the only instance

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class HowItWorksSection(models.Model):
    """Singleton header for the 'How It Works' section."""

    title_bold   = models.CharField("Title (bold part)",   max_length=100, default="How It's")
    title_italic = models.CharField("Title (italic part)", max_length=100, default="Work")
    subtitle     = models.CharField("Subtitle", max_length=255,
                                    default="Start bidding in 4 simple steps and win exclusive auction items")

    class Meta:
        verbose_name = "How It Works Section"
        verbose_name_plural = "How It Works Section"

    def __str__(self):
        return "Homepage – How It Works"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class ProcessStep(models.Model):
    """One card in the 'How It Works' section."""

    section = models.ForeignKey(
        HowItWorksSection, on_delete=models.CASCADE, related_name="steps",
    )
    order  = models.PositiveSmallIntegerField("Order", default=0)
    icon   = models.CharField(
        "Bootstrap icon class", max_length=100, default="bi-star-fill",
        help_text="E.g. bi-person-plus-fill — find icons at https://icons.getbootstrap.com",
    )
    title  = models.CharField("Step title", max_length=100)
    item_1 = models.CharField("Sub-item 1", max_length=200, blank=True)
    item_2 = models.CharField("Sub-item 2", max_length=200, blank=True)
    item_3 = models.CharField("Sub-item 3", max_length=200, blank=True)
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Process Step"
        verbose_name_plural = "Process Steps"

    def __str__(self):
        return f"Step {self.order:02d}: {self.title}"


class FaqSection(models.Model):
    """Singleton settings for the homepage FAQ section."""

    title_bold   = models.CharField("Title (bold part)",   max_length=100, default="Frequently Asked")
    title_italic = models.CharField("Title (italic part)", max_length=100, default="Questions")
    subtitle     = models.CharField("Subtitle", max_length=255,
                                    default="Everything you need to know about bidding on RapidVenta")

    # Left panel contact card
    contact_heading = models.CharField(
        "Contact card heading", max_length=200,
        default="Ask the help community — write to us now!",
    )
    contact_label = models.CharField(
        "Contact label (e.g. 'To Send Mail')", max_length=100, default="To Send Mail",
    )
    contact_email = models.EmailField(
        "Contact / recipient email",
        help_text="Questions submitted via the form are sent to this address.",
        default="info@rapidventa.com",
    )

    # Form panel
    form_heading = models.CharField("Form heading", max_length=100, default="Any Question?")
    form_btn_text = models.CharField("Submit button text", max_length=50, default="Send Now")

    class Meta:
        verbose_name = "FAQ Section"
        verbose_name_plural = "FAQ Section"

    def __str__(self):
        return "Homepage – FAQ"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FaqItem(models.Model):
    """One FAQ accordion item."""

    section  = models.ForeignKey(FaqSection, on_delete=models.CASCADE, related_name="items")
    order    = models.PositiveSmallIntegerField("Order", default=0)
    question = models.CharField("Question", max_length=255)
    answer   = models.TextField("Answer")
    is_active = models.BooleanField("Active", default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "FAQ Item"
        verbose_name_plural = "FAQ Items"

    def __str__(self):
        return self.question


class TopbarSection(models.Model):
    """Singleton settings for the topbar strip and main navbar."""

    # ── Site identity ──────────────────────────────────────────────────────────
    logo = models.ImageField(
        "Site logo", upload_to="site/logo/", null=True, blank=True,
        help_text="Recommended: transparent PNG, ~180 × 50 px. Leave blank to use the default static logo.",
    )
    site_name = models.CharField("Site name", max_length=100, default="RapidVenta",
                                 help_text="Used in image alt text and browser title.")

    # ── Topbar: left contact info ──────────────────────────────────────────────
    email         = models.EmailField("Contact email", default="info@rapidventa.com")
    support_url   = models.CharField("Support link URL", max_length=200,
                                     default="https://wa.me/+584122392711",
                                     help_text="Full URL for the support link (WhatsApp, tel:, mailto:, …)")
    support_label = models.CharField("Support link label", max_length=100, default="Customer support")

    # ── Topbar: right action buttons ───────────────────────────────────────────
    btn_how_to_bid = models.CharField("'How to Bid' button label", max_length=80, default="HOW TO BID")
    btn_sell       = models.CharField("'Sell' button label",        max_length=80, default="SELL YOUR ITEM")
    language_label = models.CharField("Language label",             max_length=50, default="Language")

    # ── Navbar: navigation labels ──────────────────────────────────────────────
    nav_home      = models.CharField("'Home' link label",             max_length=60, default="Home")
    nav_auctions  = models.CharField("'Auctions Category' link label",max_length=60, default="Auctions Category")
    nav_contact   = models.CharField("'Contact' link label",          max_length=60, default="Contact")
    search_placeholder = models.CharField("Search box placeholder",   max_length=100, default="Search your product...")

    class Meta:
        verbose_name = "Topbar Section"
        verbose_name_plural = "Topbar Section"

    def __str__(self):
        return "Site-wide Topbar"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class FooterSection(models.Model):
    """Singleton content for the site-wide footer."""

    # Brand column
    logo = models.ImageField(
        "Footer logo", upload_to="site/footer_logo/", null=True, blank=True,
        help_text="Leave blank to use the same logo as the navbar.",
    )
    tagline = models.CharField(
        "Tagline", max_length=255,
        default="The fast, transparent online auction house. Bid smart, win big.",
    )

    # Social links
    whatsapp_url  = models.CharField("WhatsApp URL",   max_length=200, blank=True, default="https://wa.me/+584122392711")
    facebook_url  = models.URLField( "Facebook URL",   max_length=200, blank=True, default="#")
    instagram_url = models.URLField( "Instagram URL",  max_length=200, blank=True, default="#")
    twitter_url   = models.URLField( "Twitter / X URL",max_length=200, blank=True, default="#")

    # "How It Works" quick steps (footer column)
    step_1 = models.CharField("Step 1", max_length=200, default="Register & get validated")
    step_2 = models.CharField("Step 2", max_length=200, default="Browse live auctions")
    step_3 = models.CharField("Step 3", max_length=200, default="Place your highest bid")
    step_4 = models.CharField("Step 4", max_length=200, default="Win & complete the order")

    # Bottom bar
    copyright_name = models.CharField("Company name (copyright)", max_length=100, default="RapidVenta")
    bottom_text    = models.CharField("Bottom tagline", max_length=255, blank=True,
                                      default="Built with love using Django 5.2")

    class Meta:
        verbose_name = "Footer Section"
        verbose_name_plural = "Footer Section"

    def __str__(self):
        return "Site-wide Footer"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
