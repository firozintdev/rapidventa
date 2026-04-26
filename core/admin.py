from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import AboutSection, FaqItem, FaqSection, FooterSection, HowItWorksSection, ProcessStep, TopbarSection


# ── About Section ─────────────────────────────────────────────────────────────

@admin.register(AboutSection)
class AboutSectionAdmin(admin.ModelAdmin):
    """Singleton — changelist redirects straight to the edit form."""

    fieldsets = (
        ("Title", {
            "fields": ("title_bold", "title_italic"),
        }),
        ("Top Image & Description", {
            "fields": ("image", "description"),
        }),
        ("Feature Bullets", {
            "description": "Leave a field blank to hide that bullet.",
            "fields": ("feature_1", "feature_2", "feature_3", "feature_4", "feature_5"),
        }),
        ("Stat Labels", {
            "description": "Numbers are pulled live from the database; only the text labels are editable here.",
            "fields": (
                ("stat_auctions_label",   "stat_auctions_sub"),
                ("stat_categories_label", "stat_categories_sub"),
                ("stat_sellers_label",    "stat_sellers_sub"),
            ),
        }),
        ("CTA Button", {
            "fields": ("cta_text",),
        }),
        ("Testimonial", {
            "fields": ("testimonial_text", "testimonial_author"),
        }),
        ("Bottom Image", {
            "fields": ("bottom_image",),
        }),
    )

    def has_add_permission(self, request):
        return not AboutSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = AboutSection.get_solo()
        return HttpResponseRedirect(
            reverse("admin:core_aboutsection_change", args=[obj.pk])
        )


# ── How It Works Section ──────────────────────────────────────────────────────

class ProcessStepInline(admin.TabularInline):
    model = ProcessStep
    extra = 0
    fields = ("order", "icon", "title", "item_1", "item_2", "item_3", "is_active")
    ordering = ("order",)


@admin.register(HowItWorksSection)
class HowItWorksSectionAdmin(admin.ModelAdmin):
    """Singleton — changelist redirects straight to the edit form."""

    fieldsets = (
        ("Section Heading", {
            "fields": ("title_bold", "title_italic", "subtitle"),
        }),
        ("Steps", {
            "description": (
                "Add up to 4 steps. Set 'Order' (1, 2, 3 …) to control left-to-right position. "
                "Uncheck 'Active' to hide a step without deleting it."
            ),
            "fields": (),
        }),
    )
    inlines = [ProcessStepInline]

    def has_add_permission(self, request):
        return not HowItWorksSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = HowItWorksSection.get_solo()
        return HttpResponseRedirect(
            reverse("admin:core_howitworkssection_change", args=[obj.pk])
        )


# ── FAQ Section ───────────────────────────────────────────────────────────────

class FaqItemInline(admin.TabularInline):
    model = FaqItem
    extra = 0
    fields = ("order", "question", "answer", "is_active")
    ordering = ("order",)


@admin.register(FaqSection)
class FaqSectionAdmin(admin.ModelAdmin):
    """Singleton — changelist redirects straight to the edit form."""

    fieldsets = (
        ("Section Heading", {
            "fields": ("title_bold", "title_italic", "subtitle"),
        }),
        ("Contact Card", {
            "fields": ("contact_heading", "contact_label", "contact_email"),
        }),
        ("Question Form", {
            "fields": ("form_heading", "form_btn_text"),
        }),
    )
    inlines = [FaqItemInline]

    def has_add_permission(self, request):
        return not FaqSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = FaqSection.get_solo()
        return HttpResponseRedirect(
            reverse("admin:core_faqsection_change", args=[obj.pk])
        )


# ── Topbar Section ───────────────────────────────────────────────────────────

@admin.register(TopbarSection)
class TopbarSectionAdmin(admin.ModelAdmin):
    """Singleton — changelist redirects straight to the edit form."""

    fieldsets = (
        ("Site Identity", {
            "description": "Logo and site name used across the navbar and footer.",
            "fields": ("logo", "site_name"),
        }),
        ("Topbar — Left: Contact Info", {
            "fields": ("email", "support_url", "support_label"),
        }),
        ("Topbar — Right: Action Buttons", {
            "description": "Button URLs are fixed (How to Bid / How to Sell pages). Only the label text is editable.",
            "fields": ("btn_how_to_bid", "btn_sell", "language_label"),
        }),
        ("Navbar — Navigation Labels", {
            "fields": ("nav_home", "nav_auctions", "nav_contact", "search_placeholder"),
        }),
    )

    def has_add_permission(self, request):
        return not TopbarSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = TopbarSection.get_solo()
        return HttpResponseRedirect(
            reverse("admin:core_topbarsection_change", args=[obj.pk])
        )


# ── Footer Section ────────────────────────────────────────────────────────────

@admin.register(FooterSection)
class FooterSectionAdmin(admin.ModelAdmin):
    """Singleton — changelist redirects straight to the edit form."""

    fieldsets = (
        ("Brand", {
            "description": "Logo shown in the footer. Leave blank to reuse the navbar logo.",
            "fields": ("logo", "tagline"),
        }),
        ("Social Links", {
            "description": "Leave blank to hide the icon. Use full URLs (https://…).",
            "fields": ("whatsapp_url", "facebook_url", "instagram_url", "twitter_url"),
        }),
        ("How It Works Steps (footer column)", {
            "description": "Short one-line labels shown in the footer's 'How It Works' column.",
            "fields": ("step_1", "step_2", "step_3", "step_4"),
        }),
        ("Bottom Bar", {
            "fields": ("copyright_name", "bottom_text"),
        }),
    )

    def has_add_permission(self, request):
        return not FooterSection.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = FooterSection.get_solo()
        return HttpResponseRedirect(
            reverse("admin:core_footersection_change", args=[obj.pk])
        )
