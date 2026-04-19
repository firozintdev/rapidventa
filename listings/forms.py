"""
listings/forms.py
Forms for creating and filtering listings.
"""

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Category, Listing, Review


class ListingForm(forms.ModelForm):
    """Seller-facing form to create or update a listing."""

    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "category",
            "min_public_price",
            "max_public_price",
            "secret_reserve_price",
            "buy_now_price",
            "start_time",
            "end_time",
            "sku",
            "brand",
            "weight",
            "dimensions",
            "tags",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "start_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "end_time": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["start_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["end_time"].input_formats = ["%Y-%m-%dT%H:%M"]
        self.fields["secret_reserve_price"].help_text = _(
            "Hidden from buyers. Auction is VOID if no bid reaches this amount."
        )
        self.fields["buy_now_price"].help_text = _(
            "Optional. Buyers can skip bidding and purchase immediately at this price. "
            "Leave blank to disable Buy Now."
        )

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        min_price = cleaned.get("min_public_price")
        max_price = cleaned.get("max_public_price")

        if start and end and end <= start:
            raise forms.ValidationError(_("End time must be after start time."))

        if min_price and max_price and min_price > max_price:
            raise forms.ValidationError(
                _("Minimum price cannot exceed maximum price.")
            )

        buy_now = cleaned.get("buy_now_price")
        if buy_now is not None and max_price and buy_now <= max_price:
            raise forms.ValidationError(
                _("Buy Now price must be greater than the maximum public price "
                  "so it represents a genuine skip-the-auction premium.")
            )
        return cleaned


class ListingFilterForm(forms.Form):
    """Public search / filter form for the listing list page."""

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label=_("All Categories"),
    )
    order_by = forms.ChoiceField(
        choices=[
            ("end_time", _("Ending Soonest")),
            ("-end_time", _("Ending Latest")),
            ("min_public_price", _("Price: Low to High")),
            ("-min_public_price", _("Price: High to Low")),
        ],
        required=False,
        initial="end_time",
    )
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={"placeholder": _("Search auctions…")}),
    )


class CSVUploadForm(forms.Form):
    """Bulk listing upload via CSV."""

    csv_file = forms.FileField(
        label=_("CSV File"),
        help_text=_(
            "Required columns: title, description, category_slug, "
            "min_price, max_price, reserve_price, start_time, end_time"
        ),
        widget=forms.FileInput(attrs={"accept": ".csv"}),
    )


class ReviewForm(forms.ModelForm):
    """Buyer review form displayed on the listing detail page."""

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.RadioSelect(attrs={"class": "rv-star-radio"}),
            "comment": forms.Textarea(attrs={"rows": 3, "placeholder": _("Share your experience with this item…")}),
        }
