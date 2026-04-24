"""
listings/admin.py
Admin panel customisation for Category and Listing.
"""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Category, Listing, ListingImage, Review
from .services import approve_listing, reject_listing


class ListingImageInline(admin.TabularInline):
    model = ListingImage
    extra = 1
    fields = ("image", "order", "is_primary")


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ("user", "rating", "comment", "created_at")
    can_delete = True


class SubCategoryInline(admin.TabularInline):
    model = Category
    fk_name = "parent"
    extra = 1
    fields = ("name", "slug", "order", "description")
    prepopulated_fields = {"slug": ("name",)}
    verbose_name = "Subcategory"
    verbose_name_plural = "Subcategories"


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug", "order", "listing_count")
    list_filter = ("parent",)
    list_select_related = ("parent",)
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("parent__order", "parent__name", "order", "name")
    inlines = [SubCategoryInline]

    fieldsets = (
        (None, {"fields": ("name", "slug", "parent", "order", "description")}),
    )

    @admin.display(description=_("Listings"))
    def listing_count(self, obj):
        return obj.listings.count()


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title", "seller", "category", "status",
        "min_public_price", "secret_reserve_price", "buy_now_price",
        "start_time", "end_time",
    )
    list_filter = ("status", "category")
    search_fields = ("title", "seller__email", "seller__full_name")
    readonly_fields = ("created_at", "updated_at", "original_listing")
    date_hierarchy = "start_time"

    inlines = [ListingImageInline, ReviewInline]

    fieldsets = (
        (_("Listing Info"), {"fields": ("title", "description", "category", "seller")}),
        (
            _("Pricing"),
            {
                "fields": (
                    "min_public_price",
                    "max_public_price",
                    "secret_reserve_price",
                    "buy_now_price",
                )
            },
        ),
        (_("Timing"), {"fields": ("start_time", "end_time")}),
        (
            _("Additional Info"),
            {
                "fields": ("sku", "brand", "weight", "dimensions", "tags"),
                "classes": ("collapse",),
            },
        ),
        (_("Status"), {"fields": ("status", "original_listing")}),
        (_("Audit"), {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    actions = ["approve_selected", "reject_selected"]

    @admin.action(description=_("✅ Approve selected listings"))
    def approve_selected(self, request, queryset):
        count = 0
        for listing in queryset.filter(status="PENDING"):
            try:
                approve_listing(listing=listing, approved_by=request.user)
                count += 1
            except Exception:
                pass
        self.message_user(request, f"{count} listing(s) approved.")

    @admin.action(description=_("❌ Reject selected listings (back to DRAFT)"))
    def reject_selected(self, request, queryset):
        count = 0
        for listing in queryset.filter(status="PENDING"):
            try:
                reject_listing(listing=listing, rejected_by=request.user)
                count += 1
            except Exception:
                pass
        self.message_user(request, f"{count} listing(s) rejected.")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("listing", "user", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("listing__title", "user__email", "user__full_name")
    readonly_fields = ("listing", "user", "rating", "comment", "created_at")
